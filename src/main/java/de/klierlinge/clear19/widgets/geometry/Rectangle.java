package de.klierlinge.clear19.widgets.geometry;

public final class Rectangle
{
    public static final Rectangle ZEROS = new Rectangle(0, 0, 0, 0, Anchor.TOP_LEFT);
    
    private final int x;
    private final int y;
    private final int width;
    private final int height;

    public Rectangle(int x, int y, int width, int height, Anchor anchor)
    {
        this.width = width;
        this.height = height;

        switch(anchor)
        {
            case TOP_LEFT -> 
            {
                this.x = x;
                this.y = y;
            }
            case TOP_CENTER -> 
            {
                this.x = x - width / 2;
                this.y = y;
            }
            case TOP_RIGHT -> 
            {
                this.x = x - width;
                this.y = y;
            }
            case CENTER_LEFT -> 
            {
                this.x = x;
                this.y = y - height / 2;
            }
            case CENTER_CENTER ->
            {
                this.x = x - width / 2;
                this.y = y - height / 2;
            }
            case CENTER_RIGHT -> 
            {
                this.x = x - width;
                this.y = y - height / 2;
            }
            case BOTTOM_LEFT -> 
            {
                this.x = x;
                this.y = y - height;
            }
            case BOTTOM_CENTER -> 
            {
                this.x = x - width / 2;
                this.y = y - height;
            }
            case BOTTOM_RIGHT -> 
            {
                this.x = x - width;
                this.y = y - height;
            }
            default ->
            {
                this.x = 0;
                this.y = 0;
            }
        }
    }
    
    public Rectangle(AnchoredPoint pos, Size size)
    {
        this(pos.getX(), pos.getY(), size.getWidth(), size.getHeight(), pos.getAnchor());
    }

    public Rectangle(AnchoredPoint from, Vector to)
    {
        this(from, new Size(from, to));
    }
    
    public Size getSize()
    {
        return new Size(width, height);
    }

    public AnchoredPoint getPosition(Anchor anchor)
    {
        return switch(anchor)
        {
            case TOP_LEFT -> new AnchoredPoint(x, y, anchor);
            case TOP_CENTER -> new AnchoredPoint(x + width / 2, y, anchor);
            case TOP_RIGHT -> new AnchoredPoint(x + width, y, anchor);
            case CENTER_LEFT -> new AnchoredPoint(x, y + height / 2, anchor);
            case CENTER_CENTER -> new AnchoredPoint(x + width / 2, y + height / 2, anchor);
            case CENTER_RIGHT -> new AnchoredPoint(x + width, y + height / 2, anchor);
            case BOTTOM_LEFT -> new AnchoredPoint(x, y + height, anchor);
            case BOTTOM_CENTER -> new AnchoredPoint(x + width / 2, y + height, anchor);
            case BOTTOM_RIGHT -> new AnchoredPoint(x + width, y + height, anchor);
        };
    }

    public Rectangle withPosition(AnchoredPoint pos)
    {
        return withPosition(pos.getX(), pos.getY(), pos.getAnchor());
    }
    
    public Rectangle withPosition(int newX, int newY, Anchor anchor)
    {
        return new Rectangle(newX, newY, width, height, anchor);
    }
    
    public Rectangle moved(Vector vector)
    {
        return new Rectangle(getLeft() + vector.getX(), getTop() + vector.getY(), getWidth(), getHeight(), Anchor.TOP_LEFT);
    }
    
    public Rectangle withSize(Size newSize, Anchor anchor)
    {
        return new Rectangle(getPosition(anchor).anchored(anchor), newSize);
    }
    
    public Rectangle withHeight(int newHeight, AnchorH anchor)
    {
        return new Rectangle(getLeft(), getTop(), getWidth(), newHeight, anchor.with(AnchorV.LEFT));
    }
    
    public Rectangle withWidth(int newWidth, AnchorV anchor)
    {
        return new Rectangle(getLeft(), getTop(), newWidth, getHeight(), anchor.with(AnchorH.TOP));
    }
    
    public int getLeft()
    {
        return x;
    }
    
    public int getRight()
    {
        return x + width;
    }
    
    public int getTop()
    {
        return y;
    }
    
    public int getBottom()
    {
        return y + height;
    }
    
    public int getWidth()
    {
        return width;
    }
    
    public int getHeight()
    {
        return height;
    }
    
    @Override
    public int hashCode()
    {
        final int prime = 31;
        int result = 1;
        result = prime * result + height;
        result = prime * result + width;
        result = prime * result + x;
        result = prime * result + y;
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
        Rectangle other = (Rectangle)obj;
        if(height != other.height)
            return false;
        if(width != other.width)
            return false;
        if(x != other.x)
            return false;
        if(y != other.y)
            return false;
        return true;
    }

    @Override
    public String toString()
    {
        return "Position [x=" + x + ", y=" + y + ", width=" + width + ", height=" + height + "]";
    }
}
