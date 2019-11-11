package de.klierlinge.clear19.data.web;

import java.awt.Image;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.file.AccessDeniedException;
import java.nio.file.Files;
import java.nio.file.NotDirectoryException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.BlockingDeque;
import java.util.concurrent.LinkedBlockingDeque;
import java.util.function.Consumer;
import java.util.function.Function;

import javax.imageio.ImageIO;

import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import com.google.common.cache.Cache;
import com.google.common.cache.CacheBuilder;

/**
 * Loads tiles from the Internet and cashes them in ram and on disk.
 */
public class ImageDownloader
{
    private final static Logger logger = LogManager.getLogger(ImageDownloader.class.getName());
    private final Path cachePath;

    private final Cache<String, BufferedImage> cache = CacheBuilder.newBuilder().maximumSize(10000).build();

    private final BlockingDeque<String> diskLoadStack = new LinkedBlockingDeque<>();
    private final Set<String> currentlyLoading = new HashSet<>();
    private final BlockingDeque<String> internetLoadStack = new LinkedBlockingDeque<>();
    
    private final Function<String, String> cacheFileNameCreator;
    private volatile boolean running = true;

    private final Map<String, List<Consumer<Image>>> callbacks = new HashMap<>();
    
    /**
     * @param cachePath Root-path of the disk-cache.
     * @throws IOException
     */
    public ImageDownloader(String cachePath, int maxDownloads, Function<String, String> cacheFileNameCreator) throws IOException
    {
        logger.traceEntry("cachePath: {}", cachePath);
        this.cachePath = Paths.get(cachePath);
        this.cacheFileNameCreator = cacheFileNameCreator;

        if(!Files.exists(this.cachePath))
            Files.createDirectories(this.cachePath);
        if(!Files.isDirectory(this.cachePath))
            throw new NotDirectoryException("DiskCachePath is no directory.");
        if(!Files.isWritable(this.cachePath))
            throw new AccessDeniedException("SidkCachePath is not writable.");

        final var diskLoadThread = new Thread(new DiskCacheLoader());
        diskLoadThread.setDaemon(true);
        diskLoadThread.setName("DiskCacheTileLoader");
        diskLoadThread.start();

        final var iLoader = new InternetLoader(internetLoadStack);
        for(var i = 1; i <= maxDownloads; i++)
        {
            final var t = new Thread(iLoader);
            t.setDaemon(true);
            t.setName("InternetLoader " + i);
            t.start();
        }

        logger.traceExit();
    }

    protected static BufferedImage download(String url, Path diskCache) throws IOException
    {
        logger.traceEntry("url: {}, cache: {}", url, diskCache);
        Files.createDirectories(diskCache.getParent());

        BufferedImage image = null;
        try (var httpClient = HttpClientBuilder.create().setUserAgent("Clear Maps").build())
        {
            final var httpGet = new HttpGet(url);
            try (var response = httpClient.execute(httpGet))
            {
                final var entity = response.getEntity();
                if(entity != null)
                {
                    try (var is = new CachingInputStream(entity.getContent(), diskCache))
                    {
                        image = ImageIO.read(is);
                    }
                    catch(IOException e)
                    {
                        throw e;
                    }
                }
            }
        }
        finally
        {
            if(image == null)
            {
                if(Files.exists(diskCache))
                {
                    logger.warn("Deleting incomplete downloaded image: " + diskCache);
                    try
                    {
                        Files.delete(diskCache);
                    }
                    catch(IOException e)
                    {
                        logger.warn("Failed to delete corrupt file: " + diskCache, e);
                    }
                }
            }
        }
        logger.traceExit(image);
        return image;
    }

    /**
     * @param tile The tile.
     * @return Cache path of the tile.
     */
    public Path getCacheFileName(String url)
    {
        return getCachePath().resolve(cacheFileNameCreator.apply(url));
    }

    /**
     * @return Root-path of the disk-cache.
     */
    public Path getCachePath()
    {
        return cachePath;
    }

    /**
     * Returns the image from the memory cache. When the image is not in the
     * memory cache, this function returns null and the image will be loaded in
     * the background.
     * 
     * @param url URL to get.
     * @return Image for the tile or null, when the tile is not in cache.
     */
    public BufferedImage getImage(String url, Consumer<Image> callback)
    {
        logger.traceEntry("tile: {}", url);
        final BufferedImage image;
        synchronized(currentlyLoading)
        {
            image = cache.getIfPresent(url);
        }
        if(image != null)
        {
            logger.traceExit(image);
            return image;
        }

        if(callback != null)
        {
            synchronized(callbacks)
            {
                if(!callbacks.containsKey(url))
                    callbacks.put(url, new ArrayList<>(10));
                callbacks.get(url).add(callback);
            }
        }

        enqueueDisk(url);

        logger.traceExit(null);
        return null;
    }
    
    public Image getImage(String url)
    {
        return getImage(url, null);
    }

    /**
     * Put a tile in the load queue.
     * 
     * @param tile Tile to enqueue.
     */
    private synchronized void enqueueDisk(String job)
    {
        logger.traceEntry("tile: {}", job);
        diskLoadStack.push(job);
        logger.traceExit();
    }

    /**
     * Put a tile in the load queue.
     * 
     * @param tile Tile to enqueue.
     */
    private synchronized void enqueueInternet(String job)
    {
        logger.traceEntry("tile: {}", job);
        internetLoadStack.addFirst(job);
        logger.traceExit();
    }

    /**
     * @return True, when the background workers are still running.
     */
    public boolean isRunning()
    {
        return running;
    }

    private class DiskCacheLoader implements Runnable
    {
        @Override
        public void run()
        {
            while(running)
            {
                final String job;
                try
                {
                    job = diskLoadStack.takeFirst();
                }
                catch(InterruptedException e)
                {
                    logger.debug("Load thread interrupted.", e);
                    continue;
                }
                synchronized(currentlyLoading)
                {
                    if(cache.getIfPresent(job) != null || currentlyLoading.contains(job))
                        continue;
                    currentlyLoading.add(job);
                }

                final var diskCache = getCacheFileName(job);
                final BufferedImage image;

                if(Files.exists(diskCache))
                {
                    try
                    {
                        image = loadImage(diskCache.toFile());
                    }
                    catch(IllegalArgumentException | IOException e)
                    {
                        logger.error("Cacheload failed: " + diskCache, e);

                        synchronized(currentlyLoading)
                        {
                            currentlyLoading.remove(job);
                        }
                        enqueueInternet(job);
                        continue;
                    }

                    if(image == null)
                    {
                        logger.warn("Error detected in image: " + job);
                        try
                        {
                            Files.delete(diskCache);
                        }
                        catch(IOException e)
                        {
                            logger.warn("Failed to delete corrupt file: " + diskCache, e);
                        }

                        synchronized(currentlyLoading)
                        {
                            currentlyLoading.remove(job);
                        }
                        enqueueInternet(job);
                        continue;
                    }

                    synchronized(currentlyLoading)
                    {
                        currentlyLoading.remove(job);
                        cache.put(job, image);
                    }

                    synchronized(callbacks)
                    {
                        final var list = callbacks.get(job);
                        if(list != null)
                        {
                            for(final var callback : list)
                                callback.accept(image);
                        }
                        callbacks.remove(job);
                    }

                    // TODO: Redownload if expired.
                }
                else
                {
                    synchronized(currentlyLoading)
                    {
                        currentlyLoading.remove(job);
                    }
                    enqueueInternet(job);
                }
            }
        }
    }

    private class InternetLoader implements Runnable
    {
        private final BlockingDeque<String> loadStack;

        public InternetLoader(BlockingDeque<String> loadStack)
        {
            this.loadStack = loadStack;
        }

        @Override
        public void run()
        {
            while(running)
            {
                final String job;
                try
                {
                    job = loadStack.takeFirst();
                }
                catch(InterruptedException e)
                {
                    logger.debug("Load thread interrupted.", e);
                    continue;
                }

                synchronized(currentlyLoading)
                {
                    if(cache.getIfPresent(job) != null || currentlyLoading.contains(job))
                        continue;
                    currentlyLoading.add(job);
                }

                final var diskCache = getCacheFileName(job);
                final BufferedImage image;
                try
                {
                    logger.debug("Downloading " + job);
                    image = download(job, diskCache);
                }
                catch(IOException e)
                {
                    logger.error("Download failed: " + job, e);
                    synchronized(currentlyLoading)
                    {
                        currentlyLoading.remove(job);
                    }
                    continue;
                }

                if(image == null)
                {
                    logger.warn("Failed to lad image image: " + job);
                    synchronized(currentlyLoading)
                    {
                        currentlyLoading.remove(job);
                    }
                    continue;
                }

                synchronized(currentlyLoading)
                {
                    currentlyLoading.remove(job);
                    cache.put(job, image);
                }

                synchronized(callbacks)
                {
                    final var list = callbacks.get(job);
                    if(list != null)
                    {
                        for(final var callback : list)
                            callback.accept(image);
                    }
                    callbacks.remove(job);
                }
            }
        }
    }
    
    private static BufferedImage loadImage(File file) throws FileNotFoundException, IOException
    {
        try(var fis = new FileInputStream(file))
        {
            return ImageIO.read(fis);
        }
    }
}
