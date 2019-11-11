package de.klierlinge.clear19.widgets;

import java.awt.Graphics2D;
import java.time.LocalTime;
import java.util.Timer;

import de.klierlinge.clear19.widgets.geometry.Size;

public class AnalogClock extends Widget
{
    Timer timer;

    public AnalogClock(ContainerWidget parent)
    {
        super(parent);
        getApp().scheduler.schedule(37, () -> setDirty());
    }

    @Override
    public void paintForeground(Graphics2D g)
    {
        final var width = getWidth();
        final var height = getHeight();
        final var midX = width / 2;
        final var midY = height / 2;
        g.setColor(getForeground());
        g.drawOval(0, 0, width - 1, height - 1);
        //double s = new Date().getSeconds() / 60.0 * 2 * Math.PI;
        //final double s = (LocalTime.now().getSecond() * 1000 + LocalTime.now().getNano() / 1000000) / 60000.0 * 2 * Math.PI;
        final var s = LocalTime.now().getNano() / 1000000000.0 * 2 * Math.PI;
        g.drawLine(midX, midY, (int)(midX + Math.sin(s) * midX), (int)(midY - Math.cos(s) * midY));
    }

    @Override
    public Size getPreferedSize(Graphics2D g)
    {
        return new Size(100, 100);
    }

}
