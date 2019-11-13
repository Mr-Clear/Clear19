package de.klierlinge.clear19.widgets;

import java.awt.Color;
import java.awt.Graphics2D;
import java.util.Objects;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import de.klierlinge.clear19.widgets.geometry.Anchor;
import de.klierlinge.clear19.widgets.geometry.AnchorH;
import de.klierlinge.clear19.widgets.geometry.AnchorV;
import de.klierlinge.clear19.widgets.geometry.AnchoredPoint;
import de.klierlinge.clear19.widgets.geometry.Rectangle;
import de.klierlinge.clear19.widgets.geometry.Size;
import de.klierlinge.clear19.widgets.geometry.Point;

public abstract class Widget
{
    private static final Logger logger = LogManager.getLogger(Widget.class.getName());
    private final Widget parent;
    private final AppWidget<?> app;
    private final Screen screen;
    private Rectangle rectangle = Rectangle.ZEROS;
    protected boolean isVisible = true;
    private int layer;
    private boolean dirty = true;
    private Color background = Color.BLACK;
    private Color foreground = Color.WHITE;

    public Widget(ContainerWidget parent)
    {
        this.parent = parent;
        if (parent != null)
        {
            parent.getChildren().add(this);
            setBackground(parent.getBackground());
            setForeground(parent.getForeground());
            setRectangle(new Rectangle(parent.getRectangle().getPosition(Anchor.CENTER_CENTER), Size.ZERO));
            app = parent.getApp();
            if (this instanceof Screen)
                screen = (Screen)this;
            else
                screen = parent.getScreen();
        }
        else
        {
            app = (AppWidget<?>)this;
            screen = null;
        }
    }
    
    protected Rectangle getAbsRect()
    {
        return rectangle;
    }
    
    public Rectangle getRectangle()
    {
        return rectangle.withPosition(rectangle.getPosition(Anchor.TOP_LEFT).add(parent.getAbsRect().getPosition(Anchor.TOP_LEFT).reversed()));
    }

    protected void setAbsRect(Rectangle rectangle)
    {
        this.rectangle = rectangle;
        setDirty();
    }
    
    public void setRectangle(Rectangle rectangle)
    {
        setAbsRect(rectangle.moved(parent.getAbsRect().getPosition(Anchor.TOP_LEFT)));
    }

    public void setRectangle(AnchoredPoint from, Point to)
    {
        setRectangle(new Rectangle(from, to));
    }

    public void setRectangle(AnchoredPoint position, Size size)
    {
        setRectangle(new Rectangle(position, size));
    }
    
    public void setSize(Size size, Anchor anchor)
    {
        setAbsRect(getAbsRect().withSize(size, anchor));
    }
    
    public void setWidth(int width, AnchorH anchor)
    {
        setAbsRect(getAbsRect().withWidth(width, anchor));
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
    
    public final AppWidget<?> getApp()
    {
        return app;
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
        return isVisible && (getScreen() == null || getScreen().isVisible());
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
        if(layer < 1000)
            dirty = false;
    }
    
    public void paint(Graphics2D g)
    {
        g.setColor(getBackground());
        paintBackground(g);
        g.setColor(getForeground());
        paintForeground(g);
        clearDirty();
    }

    abstract public void paintForeground(Graphics2D g);

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
    public AnchoredPoint getPosition(Anchor anchor)
    {
        return getRectangle().getPosition(anchor);
    }
    public int getLeft()
    {
        return getRectangle().getLeft();
    }
    public int getRight()
    {
        return getRectangle().getRight();
    }
    public int getTop()
    {
        return getRectangle().getTop();
    }
    public int getBottom()
    {
        return getRectangle().getBottom();
    }
}
