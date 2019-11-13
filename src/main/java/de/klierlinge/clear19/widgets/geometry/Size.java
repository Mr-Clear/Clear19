package de.klierlinge.clear19.widgets.geometry;

import java.awt.Dimension;

public final class Size
{
    public static final Size ZERO = new Size(0, 0);
    
    private final int width;
    private final int height;

    public Size(int width, int height)
    {
        this.width = width;
        this.height = height;
    }
    
    public Size(Point a, Point b)
    {
        width = Math.abs(a.getX() - b.getX());
        height = Math.abs(a.getY() - b.getY());
    }
    
    public int getWidth()
    {
        return width;
    }

    public int getHeight()
    {
        return height;
    }
    
    public Point toVector()
    {
        return new Point(getWidth(), getHeight());
    }

    public Dimension toAwtDimension()
    {
        return new Dimension(width, height);
    }

    public AnchoredPoint getPos(Anchor anchor)
    {
        return new Rectangle(AnchoredPoint.ZERO, this).getPosition(anchor);
    }

    @Override
    public int hashCode()
    {
        final int prime = 31;
        int result = 1;
        result = prime * result + height;
        result = prime * result + width;
        return result;
    }

    @Override
    public boolean equals(Object obj)
    {
        if(this == obj)
            return true;
        if(obj == null)
            return false;
        if(getClass() != obj.getClass())
            return false;
        Size other = (Size)obj;
        if(height != other.height)
            return false;
        if(width != other.width)
            return false;
        return true;
    }

    @Override
    public String toString()
    {
        return "Size [width=" + width + ", height=" + height + "]";
    }
}