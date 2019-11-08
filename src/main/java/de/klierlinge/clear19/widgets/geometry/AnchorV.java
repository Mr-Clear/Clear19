package de.klierlinge.clear19.widgets.geometry;

public enum AnchorV
{
    LEFT,
    CENTER,
    RIGHT;
    
    public Anchor with(AnchorH other)
    {
        return Anchor.combine(other, this);
    }
}