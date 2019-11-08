package de.klierlinge.clear19;

import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.swing.JFrame;
import javax.swing.WindowConstants;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import de.klierlinge.clear19.data.system.SystemData;
import de.klierlinge.clear19.widgets.MainScreen;
import de.klierlinge.clear19.widgets.Screen;
import de.klierlinge.clear19.widgets.Widget;
import de.klierlinge.clear19.widgets.geometry.Size;
import net.djpowell.lcdjni.AppletCapability;
import net.djpowell.lcdjni.DeviceType;
import net.djpowell.lcdjni.LcdConnection;
import net.djpowell.lcdjni.LcdDevice;
import net.djpowell.lcdjni.LcdException;
import net.djpowell.lcdjni.LcdRGBABitmap;
import net.djpowell.lcdjni.Priority;
import net.djpowell.lcdjni.SyncType;

public class App extends Widget
{
    private static final Logger logger = LogManager.getLogger(App.class.getName());

    private final BufferedImage image;
    Screen screen;

    public final Scheduler scheduler = new Scheduler();

    private LcdConnection lcdCon;
    private LcdDevice lcdDevice;
    private LcdRGBABitmap lcdBmp;
    private final ImagePanel imagePanel;

    public final SystemData systemData = new SystemData();
    
    public App()
    {
        super(null);
        logger.info("START");
        
        setForeground(Color.LIGHT_GRAY);
        
        final var frame = new JFrame("Clear19");
        frame.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE);
        frame.setLocation(500, 500);
        imagePanel = new ImagePanel();
        frame.setContentPane(imagePanel);
        frame.pack();
        image = new BufferedImage(320, 240, BufferedImage.TYPE_INT_RGB);
        imagePanel.setImage(image);
        
        screen = new MainScreen(this, getGraphics());
        
        frame.setVisible(true);

        try
        {
            lcdCon = new LcdConnection("HelloWorld", false, AppletCapability.getCaps(AppletCapability.QVGA), null, null);
            lcdDevice = lcdCon.openDevice(DeviceType.QVGA, null);
            lcdBmp = lcdDevice.createRGBABitmap();
            lcdDevice.setForeground(true);
        }
        catch(UnsatisfiedLinkError e)
        {
            logger.error("Failed to load lcd library.", e);
            lcdCon = null;
            lcdDevice = null;
            lcdBmp = null;
        }

        frame.addWindowListener(new WindowAdapter()
        {
            @Override
            public void windowClosed(WindowEvent e)
            {
                exit();
            }
        });

        scheduler.schedule(10, () -> {
            if (isDirty())
                updateLcd();
        });
    }
    
    private void updateLcd()
    {
        logger.trace("Update LCD");
        {
            final Graphics2D g = getGraphics();
            paint(g);
            g.dispose();
        }
        
        synchronized(scheduler)
        {
            imagePanel.repaint();
            
            if (lcdBmp != null)
            {
                final var g = (Graphics2D)lcdBmp.getGraphics();
                g.drawImage(image, 0, 0, null);
                g.dispose();
                lcdBmp.updateScreen(Priority.NORMAL, SyncType.SYNC);
                g.dispose();
            }
        }
    }
    
    private Graphics2D getGraphics()
    {
        final var g = (Graphics2D)image.getGraphics();
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
        scheduler.close();
        synchronized(scheduler)
        {
            if (lcdBmp != null)
            {
                try
                {
                    lcdBmp.close();
                    lcdDevice.close();
                    lcdCon.close();
                }
                catch(LcdException | IOException e2)
                {
                    logger.warn("Failed to close LCD", e2);
                }
                LcdConnection.deInit();
            }
        }
        logger.info("END");
        System.exit(0);
    }

    @Override
    public void paint(Graphics2D g)
    {
        paintForeground(g);
        clearDirty();
    }
    
    @Override
    public void paintForeground(Graphics2D g)
    {
        screen.paint(g);
    }    

    @Override
    public Size getPreferedSize(Graphics2D g)
    {
        return Size.ZERO;
    }
    
    @SuppressWarnings("unused")
    public static void main(String[] args)
    {
        try
        {
            new App();            
        }
        catch(Throwable t)
        {
            logger.fatal("Failed to start app", t);
            System.exit(1);
        }
    }
}
