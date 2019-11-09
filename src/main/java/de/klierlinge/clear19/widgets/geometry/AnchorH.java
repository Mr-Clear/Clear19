package de.klierlinge.clear19.widgets.geometry;

public enum AnchorH
{
    LEFT,
    CENTER,
    RIGHT;
    
    public Anchor with(AnchorV other)
    {
        return Anchor.combine(other, this);
    }
}