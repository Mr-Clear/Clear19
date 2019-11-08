package de.klierlinge.clear19.widgets;

import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.geom.AffineTransform;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import de.klierlinge.clear19.App;
import de.klierlinge.clear19.widgets.geometry.Anchor;
import de.klierlinge.clear19.widgets.geometry.AnchoredPoint;
import de.klierlinge.clear19.widgets.geometry.Vector;
import de.klierlinge.clear19.widgets.geometry.Rectangle;
import de.klierlinge.clear19.widgets.geometry.Size;

public abstract class Widget
{
    private static final Logger logger = LogManager.getLogger(Widget.class.getName());
    private final Widget parent;
    protected final App app;
    protected List<Widget> children = new ArrayList<>();
    private Rectangle rectangle = Rectangle.ZEROS;
    private boolean dirty = true;
    private Color background = Color.BLACK;
    private Color foreground = Color.WHITE;

    public Widget(Widget parent)
    {
        this.parent = parent;
        if (parent != null)
        {
            parent.children.add(this);
            setBackground(parent.background);
            setForeground(parent.foreground);
            setAbsRect(new Rectangle(parent.getAbsRect().getPosition(Anchor.CENTER_CENTER), Size.ZERO));
            app = parent.app;
        }
        else
        {
            app = (App)this;
        }
    }
    
    public Rectangle getAbsRect()
    {
        return rectangle;
    }
    
    public Rectangle getRelRect()
    {
        return rectangle.withPosition(rectangle.getPosition(Anchor.TOP_LEFT).add(parent.getAbsPos(Anchor.TOP_LEFT)));
    }

    public void setAbsRect(Rectangle rectangle)
    {
        this.rectangle = rectangle;
        setDirty();
    }
    
    public void setRelRect(Rectangle rectangle)
    {
        setAbsRect(rectangle.moved(parent.getAbsPos(Anchor.TOP_LEFT)));
    }

    public void setAbsRect(AnchoredPoint from, Vector to)
    {
        setAbsRect(new Rectangle(from, to));
    }
        
    public void pack(Graphics2D g, Anchor anchor)
    {
        setAbsRect(getAbsRect().withSize(getPreferedSize(g), anchor));
    }

    public Color getBackground()
    {
        return background;
    }

    public void setBackground(Color background)
    {
        if(!Objects.equals(this.background, background))
        {
            this.background = background;
            setDirty();
        }
    }

    public Color getForeground()
    {
        return foreground;
    }

    public void setForeground(Color foreground)
    {
        if(!Objects.equals(this.foreground, foreground))
        {
            this.foreground = foreground;
            setDirty();
        }
    }

    public Widget getParent()
    {
        return parent;
    }
    
    public Screen getScreen()
    {
        if(this instanceof Screen)
            return (Screen)this;
        return parent.getScreen();
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

    protected void clearDirty()
    {
        dirty = false;
    }
    
    public void paint(Graphics2D g)
    {
        g.setColor(getBackground());
        paintBackground(g);
        paintChildren(g);
        g.setColor(getForeground());
        paintForeground(g);
        clearDirty();
    }
    
    protected void paintChildren(Graphics2D g)
    {
        for(Widget child : children)
        {
            if (child.isDirty())
            {
                final var oldTx = g.getTransform();
                final var tx = new AffineTransform();
                tx.setToTranslation(child.getAbsRect().getLeft(), child.getAbsRect().getTop());
                g.setTransform(tx);
                g.setClip(new java.awt.Rectangle(child.getAbsRect().getSize().toAwtDimension()));
                child.paint(g);
                g.setTransform(oldTx);
            }
        }
    }

    protected void paintBackground(Graphics2D g)
    {
        g.fillRect(0, 0, getAbsRect().getWidth(), getAbsRect().getHeight());
    }

    public void setAbsRect(AnchoredPoint position, Size size)
    {
        setAbsRect(new Rectangle(position, size));
    }
    
    public void setSize(Size size, Anchor anchor)
    {
        setAbsRect(getAbsRect().withSize(size, anchor));
    }
    
    /* Delegate Methods for geometry information: */   
    public Size getSize()
    {
        return getAbsRect().getSize();
    }
    public int getWidth()
    {
        return getAbsRect().getWidth();
    }
    public int getHeight()
    {
        return getAbsRect().getHeight();
    }
    public AnchoredPoint getAbsPos(Anchor anchor)
    {
        return getAbsRect().getPosition(anchor);
    }
    public int getAbsLeft()
    {
        return getAbsRect().getLeft();
    }
    public int getAbsRight()
    {
        return getAbsRect().getRight();
    }
    public int getAbsTop()
    {
        return getAbsRect().getTop();
    }
    public int getAbsBottom()
    {
        return getAbsRect().getBottom();
    }

    abstract public void paintForeground(Graphics2D g);
    abstract public Size getPreferedSize(Graphics2D g);
}
