package de.klierlinge.clear19;

import java.awt.Graphics2D;
import java.awt.image.BufferedImage;
import java.util.Timer;
import java.util.TimerTask;

import javax.swing.JFrame;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import de.klierlinge.clear19.widgets.MainScreen;

public class App
{
    private static final Logger logger = LogManager.getLogger(App.class.getName());

    public static void main(String[] args)
    {
        logger.info("START");
        JFrame f = new JFrame("Clear19");
        f.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        f.setLocation(500, 500);
        ImagePanel imagePanel = new ImagePanel();
        f.setContentPane(imagePanel);
        f.pack();
        BufferedImage image = new BufferedImage(320, 240, BufferedImage.TYPE_INT_RGB);
        imagePanel.setImage(image);
        
        MainScreen mainScreen = new MainScreen((Graphics2D)image.getGraphics());
        mainScreen.paint((Graphics2D)image.getGraphics());
        
        f.setVisible(true);

        Runtime.getRuntime().addShutdownHook(new Thread()
        {
            @Override
            public void run()
            {
                logger.info("END");
            }
        });
        
        Timer timer = new Timer();
        timer.schedule(new TimerTask()
        {
            @Override
            public void run()
            {
                if(mainScreen.isDirty())
                {
                    mainScreen.paint((Graphics2D)image.getGraphics());
                    imagePanel.repaint();
                }
            }
        }, 31, 31);
    }
}
