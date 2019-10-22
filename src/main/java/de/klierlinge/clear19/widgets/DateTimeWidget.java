package de.klierlinge.clear19.widgets;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.Graphics2D;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Timer;
import java.util.TimerTask;

public class DateTimeWidget extends Widget
{
    SimpleDateFormat dateFormat = new SimpleDateFormat("dd.MM.YYYY");
    SimpleDateFormat timeFormat = new SimpleDateFormat("HH:mm:ss.SSS");
    Timer timer;
    
    public DateTimeWidget(Widget parent)
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
        }, 37, 37);
    }
    
    @Override
    public void paint(Graphics2D g)
    {
        g.setColor(Color.WHITE);
        g.fillRect(0, 0, getPos().width, getPos().height);
        g.setColor(Color.RED);
        setFont(g);
        Date now = new Date();
        final String time = timeFormat.format(now);
        final String date = dateFormat.format(now);
        final int fontHeight = g.getFontMetrics().getHeight();
        final int fontAscent = g.getFontMetrics().getAscent();
        final int timeWidth = g.getFontMetrics().stringWidth(time);
        final int dateWidth = g.getFontMetrics().stringWidth(date);
        g.drawString(time, (getPos().width - timeWidth) / 2, fontAscent);
        g.drawString(date, (getPos().width - dateWidth) / 2, fontHeight + fontAscent);
    }

    @Override
    public Dimension getPreferedSize(Graphics2D g)
    {
        if(g == null)
            return new Dimension(200, 100);
        setFont(g);
        Date now = new Date();
        final String time = timeFormat.format(now);
        final String date = dateFormat.format(now);
        final int fontHeight = g.getFontMetrics().getHeight();
        final int timeWidth = g.getFontMetrics().stringWidth(time);
        final int dateWidth = g.getFontMetrics().stringWidth(date);
        return new Dimension(Math.max(timeWidth, dateWidth) + 2, fontHeight * 2);
    }
    
    private static void setFont(Graphics2D g)
    {
        g.setFont(new Font("Consolas", Font.BOLD, 14));
    }
}
