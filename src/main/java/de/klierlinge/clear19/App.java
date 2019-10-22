package de.klierlinge.clear19;

import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.util.Timer;
import java.util.TimerTask;

import javax.swing.JFrame;
import javax.swing.WindowConstants;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import de.klierlinge.clear19.widgets.MainScreen;
import de.klierlinge.clear19.widgets.Screen;
import net.djpowell.lcdjni.AppletCapability;
import net.djpowell.lcdjni.DeviceType;
import net.djpowell.lcdjni.LcdConnection;
import net.djpowell.lcdjni.LcdDevice;
import net.djpowell.lcdjni.LcdRGBABitmap;
import net.djpowell.lcdjni.Priority;
import net.djpowell.lcdjni.SyncType;

public class App
{
    private static final Logger logger = LogManager.getLogger(App.class.getName());

    private final BufferedImage image;
    Screen screen;
    
    private final Timer updateTimer = new Timer();

    private LcdConnection lcdCon;
    private LcdDevice lcdDevice;
    private LcdRGBABitmap lcdBmp;
    
    
    public App()
    {
        logger.info("START");
        JFrame f = new JFrame("Clear19");
        f.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE);
        f.setLocation(500, 500);
        ImagePanel imagePanel = new ImagePanel();
        f.setContentPane(imagePanel);
        f.pack();
        image = new BufferedImage(320, 240, BufferedImage.TYPE_INT_RGB);
        imagePanel.setImage(image);
        
        screen = new MainScreen(getGraphics());
        paint();
        
        f.setVisible(true);

        try
        {
            lcdCon = new LcdConnection("HelloWorld", false, AppletCapability.getCaps(AppletCapability.QVGA), null, null);
            lcdDevice = lcdCon.openDevice(DeviceType.QVGA, null);
            lcdBmp = lcdDevice.createRGBABitmap();
        }
        catch(UnsatisfiedLinkError e)
        {
            logger.error("Failed to load lcd library.", e);
            lcdCon = null;
            lcdDevice = null;
            lcdBmp = null;
        }
        
        
        
        updateTimer.schedule(new TimerTask()
        {
            @Override
            public void run()
            {
                if(screen.isDirty())
                {
                    synchronized(updateTimer)
                    {
                        paint();
                        
                        imagePanel.repaint();
                        
                        if (lcdBmp != null)
                        {
                            final Graphics2D g = (Graphics2D)lcdBmp.getGraphics();
                            g.drawImage(image, 0, 0, null);
                            g.dispose();
                            lcdBmp.updateScreen(Priority.ALERT, SyncType.SYNC);
                            lcdDevice.setForeground(true);
                            g.dispose();
                        }
                    }
                }
            }
        }, 31, 31);

        f.addWindowListener(new WindowAdapter()
        {
            @Override
            public void windowClosed(WindowEvent e)
            {
                exit();
            }
        });
    }
    
    private void paint()
    {
        final Graphics2D g = getGraphics();
        screen.paint(g);
        g.dispose();
    }
    
    private Graphics2D getGraphics()
    {
        final Graphics2D g = (Graphics2D)image.getGraphics();
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g.setRenderingHint(RenderingHints.KEY_ALPHA_INTERPOLATION, RenderingHints.VALUE_ALPHA_INTERPOLATION_QUALITY);
        g.setRenderingHint(RenderingHints.KEY_COLOR_RENDERING, RenderingHints.VALUE_COLOR_RENDER_QUALITY);
        g.setRenderingHint(RenderingHints.KEY_INTERPOLATION, RenderingHints.VALUE_INTERPOLATION_BICUBIC);
        g.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_QUALITY);
        g.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
        g.setRenderingHint(RenderingHints.KEY_FRACTIONALMETRICS, RenderingHints.VALUE_FRACTIONALMETRICS_ON);
        return g;
    }
    
    private void exit()
    {
        updateTimer.cancel();
        synchronized(updateTimer)
        {
            if (lcdBmp != null)
            {
                try
                {
                    lcdBmp.close();
                    lcdDevice.close();
                    lcdCon.close();
                }
                catch(IOException e2)
                {
                    logger.warn("Failed to close LCD", e2);
                }
                LcdConnection.deInit();
            }
        }
        logger.info("END");
        System.exit(0);
    }
    
    @SuppressWarnings("unused")
    public static void main(String[] args)
    {
        try
        {
            new App();            
        }
        catch (Throwable t)
        {
            logger.fatal("Failed to start app", t);
            System.exit(1);
        }
    }
}
