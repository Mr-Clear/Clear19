package de.klierlinge.clear19.widgets;

import java.awt.Dimension;
import java.awt.Graphics2D;

public class Border extends Widget
{
    private final Orientation orientation;

    public Border(Widget parent, Orientation orientation)
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
            case HORIZONTAL -> g.drawLine(0, getHeigth() / 2, getWidth(), getHeigth() / 2);
            case VERTICAL -> g.drawLine(getWidth() / 2, 0, getWidth() / 2, getHeigth());
        }
    }

    @Override
    public Dimension getPreferedSize(Graphics2D g)
    {
        return switch(orientation)
        {
            case HORIZONTAL -> new Dimension(getParent().getWidth(), 3);
            case VERTICAL -> new Dimension(3, getParent().getHeigth());
        };
    }

    public enum Orientation
    {
        HORIZONTAL, VERTICAL
    }
}
