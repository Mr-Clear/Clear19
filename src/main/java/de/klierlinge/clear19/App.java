package de.klierlinge.clear19;

import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

import javax.swing.JFrame;
import javax.swing.WindowConstants;

import org.apache.log4j.BasicConfigurator;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import de.klierlinge.clear19.data.system.SystemData;
import de.klierlinge.clear19.widgets.MainScreen;
import de.klierlinge.clear19.widgets.Screen;
import de.klierlinge.clear19.widgets.SystemScreen;
import de.klierlinge.clear19.widgets.Widget;
import de.klierlinge.clear19.widgets.geometry.Size;
import net.djpowell.lcdjni.AppletCapability;
import net.djpowell.lcdjni.DeviceType;
import net.djpowell.lcdjni.KeyCallback;
import net.djpowell.lcdjni.LcdConnection;
import net.djpowell.lcdjni.LcdDevice;
import net.djpowell.lcdjni.LcdException;
import net.djpowell.lcdjni.LcdRGBABitmap;
import net.djpowell.lcdjni.Priority;
import net.djpowell.lcdjni.SyncType;

public class App extends Widget implements KeyCallback
{
    private static final Logger logger = LogManager.getLogger(App.class.getName());

    private final BufferedImage image;
    public final Screen mainScreen;
    public final Screen systemScreen;

    public final Scheduler scheduler = new Scheduler();

    private LcdConnection lcdCon;
    private LcdDevice lcdDevice;
    private LcdRGBABitmap lcdBmp;
    private final Set<Button> pressedButtons = new HashSet<>();
    private final ImagePanel imagePanel;

    public final SystemData systemData = new SystemData();
    
    public final Object exitObserver = new Object();
    
    public App() throws IOException
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

        Size imageSize;
        try
        {
            lcdCon = new LcdConnection("Clear19", false, AppletCapability.getCaps(AppletCapability.QVGA), null, null);
            lcdDevice = lcdCon.openDevice(DeviceType.QVGA, this);
            lcdBmp = lcdDevice.createRGBABitmap();
            lcdDevice.setForeground(true);
            final var buttons = lcdDevice.readSoftButtons();
            for(final var b : Button.values())
                if((buttons & b.keyValue) != 0)
                    pressedButtons.add(b);
            imageSize = new Size(lcdBmp.getImage().getWidth(), lcdBmp.getImage().getHeight());
        }
        catch(UnsatisfiedLinkError e)
        {
            logger.error("Failed to load lcd library.", e);
            lcdCon = null;
            lcdDevice = null;
            lcdBmp = null;
            imageSize = new Size(320, 240);
        }
        
        image = new BufferedImage(imageSize.getWidth(), imageSize.getHeight(), BufferedImage.TYPE_INT_RGB);
        imagePanel.setImage(image);

        mainScreen = new MainScreen(this, getGraphics());
        systemScreen = new SystemScreen(this, getGraphics());
        setCurrentScreen(mainScreen);
        
        frame.setVisible(true);

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
        
        getCurrentScreen().onShow(null);
        
        synchronized(exitObserver)
        {
            boolean noExcept = false;
            while(!noExcept)
            try
            {
                exitObserver.wait();
                noExcept = true;
            }
            catch(InterruptedException e)
            {
                logger.debug("Interrupted while waiting for exit.", e);
            }
        }
        
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
    }
    
    public Screen getCurrentScreen()
    {
        return (Screen)getChildren().get(0);
    }
    
    public void setCurrentScreen(Screen screen)
    {
        if(screen != getCurrentScreen())
        {
            final var lastScreen = getCurrentScreen();
            lastScreen.onHide(screen);
            getChildren().clear();
            getChildren().add(screen);
            screen.onShow(lastScreen);
            screen.setDirty(true);
            logger.debug("Changed Screen from " + lastScreen.getName() + " to " + screen.getName() + ".");
        }
    }
    
    public Size getImageSize()
    {
        return new Size(image.getWidth(), image.getHeight());
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
        g.setRenderingHint(RenderingHints.KEY_FRACTIONALMETRICS, RenderingHints.VALUE_FRACTIONALMETRICS_OFF);
        return g;
    }
    
    private void exit()
    {
        synchronized(exitObserver)
        {
            exitObserver.notifyAll();
        }
    }

    @Override
    public void paint(Graphics2D g)
    {
        paintChildren(g);
        clearDirty();
    } 

    @Override
    public Size getPreferedSize(Graphics2D g)
    {
        return new Size(image.getWidth(), image.getHeight());
    }
    
    @SuppressWarnings("unused")
    public static void main(String[] args)
    {
        BasicConfigurator.configure();
        
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


    @SuppressWarnings("hiding")
    public enum Button
    {
        LEFT(KeyCallback.LEFT),
        RIGHT(KeyCallback.RIGHT),
        OK(KeyCallback.OK),
        CANCEL(KeyCallback.CANCEL),
        UP(KeyCallback.UP),
        DOWN(KeyCallback.DOWN),
        MENU(KeyCallback.MENU);
        
        public final int keyValue;
        private Button(int keyValue)
        {
            this.keyValue = keyValue;
        }
        
        public static Button fromKeyValue(int keyValue)
        {
            for(final var b : Button.values())
                if((keyValue & b.keyValue) != 0)
                    return b;
            return null;
        }
    }

    @Override
    public void onKey(int buttons)
    {
        /* Ignore. */
    }

    @Override
    public void onKeyDown(int button)
    {
        final var b = Button.fromKeyValue(button);
        if (b != null)
        {
            getCurrentScreen().onButtonDown(b);
            pressedButtons.add(b);
        }
    }

    @Override
    public void onKeyUp(int button)
    {
        final var b = Button.fromKeyValue(button);
        if (b != null)
        {
            getCurrentScreen().onButtonUp(b);
            pressedButtons.remove(b);
        }
    }
    
    public Set<Button> getPressedButtons()
    {
        return Collections.unmodifiableSet(pressedButtons);
    }
}
