package de.klierlinge.clear19.widgets.geometry;

public class Vector
{
    public static final Vector ZERO = new Vector(0, 0);
    
    private final int x;
    private final int y;
    
    public Vector(int x, int y)
    {
        super();
        this.x = x;
        this.y = y;
    }
    
    final public int getX()
    {
        return x;
    }
    
    final public int getY()
    {
        return y;
    }

    public Vector add(Vector other)
    {
        return new Vector(getX() + other.getX(), getY() + other.getY());
    }
    
    public Vector reversed()
    {
        return new Vector(-x, -y);
    }
    
    public AnchoredPoint anchored(Anchor anchor)
    {
        return new AnchoredPoint(getX(), getY(), anchor);
    }

    @Override
    public int hashCode()
    {
        final int prime = 31;
        int result = 1;
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
        Vector other = (Vector)obj;
        if(x != other.x)
            return false;
        if(y != other.y)
            return false;
        return true;
    }

    @Override
    public String toString()
    {
        return "Point [x=" + x + ", y=" + y + "]";
    }
}
