package de.klierlinge.clear19.widgets.geometry;

public enum Anchor
{
    TOP_LEFT,
    TOP_CENTER,
    TOP_RIGHT,
    CENTER_LEFT,
    CENTER_CENTER,
    CENTER_RIGHT,
    BOTTOM_LEFT,
    BOTTOM_CENTER,
    BOTTOM_RIGHT;
    
    public static Anchor combine(AnchorV h, AnchorH v)
    {
        switch(h)
        {
        case TOP: switch(v)
            {
            case LEFT: return TOP_LEFT;
            case CENTER: return TOP_CENTER;
            case RIGHT: return TOP_RIGHT;
            default: return null;
            }
        case CENTER: switch(v)
            {
            case LEFT: return CENTER_LEFT;
            case CENTER: return CENTER_CENTER;
            case RIGHT: return CENTER_RIGHT;
            default: return null;
            }
        case BOTTOM: switch(v)
            {
            case LEFT: return BOTTOM_LEFT;
            case CENTER: return BOTTOM_CENTER;
            case RIGHT: return BOTTOM_RIGHT;
            default: return null;
            }
        default: return null;
        }
    }
}