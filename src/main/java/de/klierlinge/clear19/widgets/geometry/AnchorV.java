package de.klierlinge.clear19.widgets.geometry;

public enum AnchorV
{
    TOP,
    CENTER,
    BOTTOM;
    
    public Anchor with(AnchorH other)
    {
        return Anchor.combine(this, other);
    }
}