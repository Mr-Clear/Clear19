package de.klierlinge.clear19.widgets.geometry;

public final class AnchoredPoint extends Vector
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
    public AnchoredPoint add(Vector other)
    {
        return new AnchoredPoint(getX() + other.getX(), getY() + other.getY(), getAnchor());
    }
}
