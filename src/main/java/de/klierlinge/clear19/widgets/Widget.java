package de.klierlinge.clear19.widgets;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.Graphics2D;
import java.awt.Point;
import java.awt.Rectangle;
import java.awt.geom.AffineTransform;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import de.klierlinge.clear19.App;

public abstract class Widget
{
    private static final Logger logger = LogManager.getLogger(Widget.class.getName());
    private final Widget parent;
    protected final App app;
    protected List<Widget> children = new ArrayList<>();
    private Rectangle pos = new Rectangle(0, 0, 0, 0);
    private boolean dirty = true;
    private Color background = Color.BLACK;
    private Color foreground = Color.WHITE;

    public Widget(Widget parent)
    {
        this.parent = parent;
        this.setSize(getPreferedSize(null));
        if (parent != null)
        {
            parent.children.add(this);
            setBackground(parent.background);
            setForeground(parent.foreground);
            this.setCenter(parent.getCenter());
            app = parent.app;
        }
        else
        {
            app = (App)this;
        }
    }
    
    public Rectangle getPos()
    {
        return pos;
    }

    public void setPos(Rectangle size)
    {
        this.pos = size;
    }
    
    public int getLeft()
    {
        return pos.x;
    }
    
    public void setLeft(int left)
    {
        pos.x = left;
    }
    
    public int getRight()
    {
        return pos.x + pos.width;
    }
    
    public void setRight(int right)
    {
        pos.x = right - pos.width;
    }
    
    public int getTop()
    {
        return pos.y;
    }
    
    public void setTop(int top)
    {
        pos.y = top;
    }
    
    public int getBottom()
    {
        return pos.y + pos.height;
    }
    
    public void setBottom(int bottom)
    {
        pos.y = bottom - pos.height;
    }
    
    public int getCenterX()
    {
        return pos.x + pos.width / 2;
    }
    
    public void setCenterX(int centerX)
    {
        pos.x = centerX - pos.width / 2;
    }
    
    public int getCenterY()
    {
        return pos.y + pos.height / 2;
    }
    
    public void setCentery(int centerY)
    {
        pos.y = centerY - pos.height / 2;
    }
    
    public Point getTopLeft()
    {
        return new Point(pos.x, pos.y); 
    }
    
    public void setTopLeft(Point topLeft)
    {
        pos.x = topLeft.x;
        pos.y = topLeft.y;
    }
    
    public Point getTopRight()
    {
        return new Point(pos.x + pos.width, pos.y);
    }
    
    public void setTopRight(Point topRight)
    {
        pos.x = topRight.x - pos.width;
        pos.y = topRight.y;
    }
    
    public Point getBottomLeft()
    {
        return new Point(pos.x, pos.y + pos.height); 
    }
    
    public void setBottomLeft(Point bottomLeft)
    {
        pos.x = bottomLeft.x;
        pos.y = bottomLeft.y - pos.height;
    }
    
    public Point getBottomRight()
    {
        return new Point(pos.x + pos.width, pos.y + pos.height);
    }
    
    public void setBottomRight(Point bottomRight)
    {
        pos.x = bottomRight.x - pos.width;
        pos.y = bottomRight.y - pos.height;
    }
    
    public Point getCenter()
    {
        return new Point(getCenterX(), getCenterY());
    }
    
    public void setCenter(Point center)
    {
        setCenterX(center.x);
        setCentery(center.y);
    }
    
    public int getWidth()
    {
        return pos.width;
    }
    
    public void setWidth(int width)
    {
        pos.width = width;
    }
    
    public int getHeigth()
    {
        return pos.height;
    }
    
    public void setHeight(int height)
    {
        pos.height = height;
    }
    
    public Dimension getSize()
    {
        return pos.getSize();
    }
    
    public void setSize(Dimension size)
    {
        pos.setSize(size);
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
        paintBackground(g);
        paintChildren(g);
        paintForeground(g);
        clearDirty();
    }
    
    protected void paintChildren(Graphics2D g)
    {
        for(Widget child : children)
        {
            if (child.isDirty())
            {
                final AffineTransform oldTx = g.getTransform();
                final AffineTransform tx = new AffineTransform();
                tx.setToTranslation(child.getPos().getX(), child.getPos().getY());
                g.setTransform(tx);
                child.paint(g);
                g.setTransform(oldTx);
            }
        }
    }

    protected void paintBackground(Graphics2D g)
    {
        g.setColor(getBackground());
        g.fillRect(0, 0, getWidth(), getHeigth());
    }
    
    abstract public void paintForeground(Graphics2D g);
    abstract public Dimension getPreferedSize(Graphics2D g);
}
