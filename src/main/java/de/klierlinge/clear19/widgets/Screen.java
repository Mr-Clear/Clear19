package de.klierlinge.clear19.widgets;

import java.awt.Graphics2D;

import de.klierlinge.clear19.widgets.geometry.AnchoredPoint;
import de.klierlinge.clear19.widgets.geometry.Rectangle;
import de.klierlinge.clear19.widgets.geometry.Size;

public abstract class Screen extends Widget
{
    public Screen(Widget parent)
    {
        super(parent);
        setAbsRect(new Rectangle(AnchoredPoint.ZERO, getPreferedSize(null)));
    }

    @Override
    public Size getPreferedSize(Graphics2D g)
    {
        return new Size(320, 240);
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
