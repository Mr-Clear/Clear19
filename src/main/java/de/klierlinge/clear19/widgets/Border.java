package de.klierlinge.clear19.widgets;

import java.awt.Graphics2D;

import de.klierlinge.clear19.widgets.geometry.Size;

public class Border extends Widget
{
    private final Orientation orientation;

    public Border(ContainerWidget parent, Orientation orientation)
    {
        super(parent);
        this.orientation = orientation;
    }

    @Override
    protected void paintBackground(Graphics2D g)
    {
        /* Don't paint background. */
    }
    
    @Override
    public void paintForeground(Graphics2D g)
    {
        switch(orientation)
        {
            case HORIZONTAL -> g.drawLine(0, getHeight() / 2, getWidth(), getHeight() / 2);
            case VERTICAL -> g.drawLine(getWidth() / 2, 0, getWidth() / 2, getHeight());
        }
    }

    @Override
    public Size getPreferedSize(Graphics2D g)
    {
        return switch(orientation)
        {
            case HORIZONTAL -> new Size(getParent().getWidth(), 3);
            case VERTICAL -> new Size(3, getParent().getHeight());
        };
    }

    public enum Orientation
    {
        HORIZONTAL, VERTICAL
    }
}
