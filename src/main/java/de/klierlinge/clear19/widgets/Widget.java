package de.klierlinge.clear19.widgets;

import java.awt.Dimension;
import java.awt.Graphics2D;
import java.awt.Rectangle;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public abstract class Widget
{
    private static final Logger logger = LogManager.getLogger(Widget.class.getName());
    private final Widget parent; 
    private Rectangle pos = new Rectangle(0, 0, 0, 0);
    private boolean dirty = true;

    public Widget(Widget parent)
    {
        this.parent = parent;
    }
    
    public Rectangle getPos()
    {
        return pos;
    }

    public void setPos(Rectangle size)
    {
        this.pos = size;
    }

    public Widget getParent()
    {
        return parent;
    }

    public boolean isDirty()
    {
        return dirty;
    }

    public void setDirty()
    {
        if (!isDirty())
        {
            logger.trace("Set as dirty: " + this);
            dirty = true;
            if (parent != null)
                parent.setDirty();
        }
    }

    void clearDirty()
    {
        dirty = false;
    }

    abstract public void paint(Graphics2D g);
    abstract public Dimension getPreferedSize(Graphics2D g);
}
