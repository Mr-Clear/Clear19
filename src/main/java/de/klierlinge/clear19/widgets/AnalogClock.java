package de.klierlinge.clear19.widgets;

import java.awt.Dimension;
import java.awt.Graphics2D;
import java.time.LocalTime;
import java.util.Timer;
import java.util.concurrent.TimeUnit;

public class AnalogClock extends Widget
{
    Timer timer;

    public AnalogClock(Widget parent)
    {
        super(parent);
        app.scheduler.scheduleAtFixedRate(() -> setDirty(), 0, 37, TimeUnit.MILLISECONDS);
    }

    @Override
    public void paintForeground(Graphics2D g)
    {
        final int width = getWidth();
        final int height = getHeigth();
        final int midX = width / 2;
        final int midY = height / 2;
        g.setColor(getForeground());
        g.drawOval(0, 0, width - 1, height - 1);
        //double s = new Date().getSeconds() / 60.0 * 2 * Math.PI;
        //final double s = (LocalTime.now().getSecond() * 1000 + LocalTime.now().getNano() / 1000000) / 60000.0 * 2 * Math.PI;
        final double s = LocalTime.now().getNano() / 1000000000.0 * 2 * Math.PI;
        g.drawLine(midX, midY, (int)(midX + Math.sin(s) * midX), (int)(midY - Math.cos(s) * midY));
    }

    @Override
    public Dimension getPreferedSize(Graphics2D g)
    {
        return new Dimension(100, 100);
    }

}
