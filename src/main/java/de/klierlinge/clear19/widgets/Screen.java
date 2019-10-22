package de.klierlinge.clear19.widgets;

import java.awt.Dimension;
import java.awt.Graphics2D;
import java.awt.Point;
import java.awt.Rectangle;

public abstract class Screen extends Widget
{
    public Screen(Widget parent)
    {
        super(parent);
        setPos(new Rectangle(new Point(0, 0), getPreferedSize(null)));
    }

    @Override
    public Dimension getPreferedSize(Graphics2D g)
    {
        return new Dimension(320, 240);
    }

    @Override
    public void paintForeground(Graphics2D g)
    {
        /* Only paint children */
    }
    
    @Override
    protected void paintBackground(Graphics2D g)
    {
        /* Don't paint background. */
    }

    abstract void layout(Graphics2D g);
}
