package de.klierlinge.clear19.data.web;

import java.io.BufferedOutputStream;
import java.io.FilterInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * A FilterInputStream, that writes all read data into a file.
 */
public class CachingInputStream extends FilterInputStream
{
    final protected OutputStream cacheStream;

    /**
     * @param in From where the data comes. Will be closed when this is closed.
     * @param cacheStream Where the read data should be written. Is buffered.
     *            Will be closed when this is closed.
     */
    public CachingInputStream(InputStream in, OutputStream cacheStream)
    {
        super(in);
        this.cacheStream = new BufferedOutputStream(cacheStream);
    }

    /**
     * @param in From where the data comes. Will be closed when this is closed.
     * @param cacheFile Where the read data should be written.
     * @throws IOException Comes from Files.newOutputStream().
     */
    public CachingInputStream(InputStream in, Path cacheFile) throws IOException
    {
        this(in, Files.newOutputStream(cacheFile));
    }

    @Override
    public int read() throws IOException
    {
        int read = in.read();
        if (read != -1)
            cacheStream.write(read);
        return read;
    }

    @Override
    public int read(byte b[], int off, int len) throws IOException
    {
        final int read = in.read(b, off, len);
        if (read != -1)
            cacheStream.write(b, off, read);
        return read;
    }

    @Override
    public void close() throws IOException
    {
        try (OutputStream toClose = cacheStream)
        {
            super.close();
        }
    }
}
