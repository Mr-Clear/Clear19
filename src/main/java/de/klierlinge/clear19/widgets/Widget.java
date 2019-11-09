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
import de.klierlinge.clear19.widgets.geometry.AnchorH;
import de.klierlinge.clear19.widgets.geometry.AnchorV;
import de.klierlinge.clear19.widgets.geometry.AnchoredPoint;
import de.klierlinge.clear19.widgets.geometry.Vector;
import de.klierlinge.clear19.widgets.geometry.Rectangle;
import de.klierlinge.clear19.widgets.geometry.Size;

public abstract class Widget
{
    private static final Logger logger = LogManager.getLogger(Widget.class.getName());
    private final Widget parent;
    protected final App app;
    protected final Screen screen;
    protected List<Widget> children = new ArrayList<>();
    private Rectangle rectangle = Rectangle.ZEROS;
    private boolean isVisible = true;
    private int layer;
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
            if (this instanceof Screen)
                screen = (Screen)this;
            else
                screen = parent.screen;
        }
        else
        {
            app = (App)this;
            screen = null;
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

    public void setRelRect(AnchoredPoint from, Vector to)
    {
        setRelRect(new Rectangle(from, to));
    }

    public void setAbsRect(AnchoredPoint position, Size size)
    {
        setAbsRect(new Rectangle(position, size));
    }

    public void setRelRect(AnchoredPoint position, Size size)
    {
        setRelRect(new Rectangle(position, size));
    }
    
    public void setSize(Size size, Anchor anchor)
    {
        setAbsRect(getAbsRect().withSize(size, anchor));
    }
    
    public void setWidth(int height, AnchorH anchor)
    {
        setAbsRect(getAbsRect().withWidth(height, anchor));
    }
    
    public void setHeight(int height, AnchorV anchor)
    {
        setAbsRect(getAbsRect().withHeight(height, anchor));
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
        return screen;
    }
    
    public void setVisible(boolean isVisible)
    {
        if(this.isVisible != isVisible)
        {
            this.isVisible = isVisible;
            setDirty();
        }
    }

    public boolean isVisible()
    {
        return isVisible && (getScreen() == null || app.getCurrentScreen() == getScreen());
    }

    public int getLayer()
    {
        return layer;
    }

    public void setLayer(int layer)
    {
        this.layer = layer;
    }

    public boolean isDirty()
    {
        return dirty;
    }

    public void setDirty()
    {
        setDirty(false);
    }

    public void setDirty(boolean childrenToo)
    {
        if (!isDirty())
        {
            logger.trace("Set as dirty: " + this);
            dirty = true;
            if (parent != null)
                parent.setDirty();
        }
        
        if(childrenToo)
            for(final var child : children)
                child.setDirty(true);
    }

    protected void clearDirty()
    {
        if(layer < 1000)
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

    @SuppressWarnings("unused")
    public void paintForeground(Graphics2D g)
    { /* Empty default implementation. */ }
    
    protected void paintChildren(Graphics2D g)
    {
        children.sort((a, b) -> Integer.compare(a.getLayer(), b.getLayer()));
        for(Widget child : children)
        {
            if (child.isDirty() && child.isVisible())
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
    
    @SuppressWarnings({"static-method", "unused"})
    public Size getPreferedSize(Graphics2D g)
    {
        return Size.ZERO;
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
    public AnchoredPoint getRelPos(Anchor anchor)
    {
        return getRelRect().getPosition(anchor);
    }
    public int getRelLeft()
    {
        return getRelRect().getLeft();
    }
    public int getRelRight()
    {
        return getRelRect().getRight();
    }
    public int getRelTop()
    {
        return getRelRect().getTop();
    }
    public int getRelBottom()
    {
        return getRelRect().getBottom();
    }
}
