package de.klierlinge.clear19;

import java.awt.Color;
import java.awt.Graphics;
import java.io.IOException;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

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
    public static void main(String[] args) throws InterruptedException, IOException
    {
        logger.info("START");
        try (LcdConnection con = new LcdConnection("HelloWorld", false, AppletCapability.getCaps(AppletCapability.QVGA), null, null);
                LcdDevice device = con.openDevice(DeviceType.QVGA, null);
                LcdRGBABitmap bmp = device.createRGBABitmap();)
        {
            final Graphics g = bmp.getGraphics();
            g.setColor(Color.red);
            g.fillRect(0, 0, 320, 240);
            g.setColor(Color.white);
            g.drawString("Hello World!", 100, 100);
            g.dispose();
            bmp.updateScreen(Priority.ALERT, SyncType.SYNC);
            device.setForeground(true);
            Thread.sleep(10000);
        }
        finally
        {
            LcdConnection.deInit();
            logger.info("END");
        }
    }
}
