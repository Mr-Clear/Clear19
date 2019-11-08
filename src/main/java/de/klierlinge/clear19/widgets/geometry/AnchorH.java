package de.klierlinge.clear19.widgets.geometry;

public enum AnchorH
{
    TOP,
    CENTER,
    BOTTOM;
    
    public Anchor with(AnchorV other)
    {
        return Anchor.combine(this, other);
    }
}