package de.klierlinge.clear19;

import java.awt.Graphics2D;
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

    final Timer updateTimer = new Timer();

    LcdConnection lcdCon;
    LcdDevice lcdDevice;
    LcdRGBABitmap lcdBmp;
    
    public App()
    {
        logger.info("START");
        JFrame f = new JFrame("Clear19");
        f.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE);
        f.setLocation(500, 500);
        ImagePanel imagePanel = new ImagePanel();
        f.setContentPane(imagePanel);
        f.pack();
        BufferedImage image = new BufferedImage(320, 240, BufferedImage.TYPE_INT_RGB);
        imagePanel.setImage(image);
        
        MainScreen mainScreen = new MainScreen((Graphics2D)image.getGraphics());
        mainScreen.paint((Graphics2D)image.getGraphics());
        
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
                if(mainScreen.isDirty())
                {
                    synchronized(updateTimer)
                    {
                        mainScreen.paint((Graphics2D)image.getGraphics());
                        imagePanel.repaint();
                        
                        if (lcdBmp != null)
                        {
                            final Graphics2D g = (Graphics2D)lcdBmp.getGraphics();
                            g.drawImage(image, 0, 0, null);
                            g.dispose();
                            lcdBmp.updateScreen(Priority.ALERT, SyncType.SYNC);
                            lcdDevice.setForeground(true);
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
        new App();
    }
}
