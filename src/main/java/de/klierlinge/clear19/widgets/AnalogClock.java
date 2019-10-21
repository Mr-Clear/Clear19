package de.klierlinge.clear19.widgets;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.Graphics2D;
import java.time.LocalTime;
import java.util.Timer;
import java.util.TimerTask;

public class AnalogClock extends Widget
{
    Timer timer;

    public AnalogClock(Widget parent)
    {
        super(parent);
        timer = new Timer();
        timer.schedule(new TimerTask()
        {
            @Override
            public void run()
            {
                setDirty(); 
            }
        }, 1, 37);
    }

    @Override
    public void paint(Graphics2D g)
    {
        g.setColor(Color.WHITE);
        g.fillRect(0, 0, 100, 100);
        g.setColor(Color.RED);
        g.drawOval(0, 0, 99, 99);
        //double s = new Date().getSeconds() / 60.0 * 2 * Math.PI;
        //final double s = (LocalTime.now().getSecond() * 1000 + LocalTime.now().getNano() / 1000000) / 60000.0 * 2 * Math.PI;
        final double s = LocalTime.now().getNano() / 1000000000.0 * 2 * Math.PI;
        g.drawLine(50, 50, (int)(50 + Math.sin(s) * 50), (int)(50 - Math.cos(s) * 50));
    }

    @Override
    public Dimension getPreferedSize(Graphics2D g)
    {
        return new Dimension(100, 100);
    }

}
