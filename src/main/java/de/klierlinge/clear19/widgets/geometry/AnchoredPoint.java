package de.klierlinge.clear19.widgets.geometry;

public final class AnchoredPoint extends Point
{
    @SuppressWarnings("hiding")
    public static final AnchoredPoint ZERO = new AnchoredPoint(0, 0, Anchor.TOP_LEFT);
    
    private final Anchor anchor;
    
    public AnchoredPoint(int x, int y, Anchor anchor)
    {
        super(x, y);
        this.anchor = anchor;
    }
    
    public Anchor getAnchor()
    {
        return anchor;
    }

    @Override
    public AnchoredPoint add(Point other)
    {
        return new AnchoredPoint(getX() + other.getX(), getY() + other.getY(), getAnchor());
    }

    @Override
    public int hashCode()
    {
        final int prime = 31;
        int result = super.hashCode();
        result = prime * result + ((anchor == null) ? 0 : anchor.hashCode());
        return result;
    }

    @Override
    public boolean equals(Object obj)
    {
        if(this == obj)
            return true;
        if(!super.equals(obj))
            return false;
        if(getClass() != obj.getClass())
            return false;
        AnchoredPoint other = (AnchoredPoint)obj;
        if(anchor != other.anchor)
            return false;
        return true;
    }

    @Override
    public String toString()
    {
        return "AnchoredPoint [anchor=" + anchor + ", x=" + getX() + ", y=" + getY() + "]";
    }
}
