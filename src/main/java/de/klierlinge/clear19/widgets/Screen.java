package de.klierlinge.clear19.widgets;

import java.awt.Dimension;
import java.awt.Graphics2D;
import java.awt.geom.AffineTransform;
import java.util.ArrayList;
import java.util.List;

public abstract class Screen extends Widget
{
    protected List<Widget> children = new ArrayList<>();

    public Screen()
    {
        super(null);
    }
    
    @Override
    public void paint(Graphics2D g)
    {
        for(Widget child : children)
        {
            if (child.isDirty())
            {
                AffineTransform tx = new AffineTransform();
                tx.setToTranslation(child.getPos().getX(), child.getPos().getY());
                g.setTransform(tx);
                child.paint(g);
                child.clearDirty();
            }
        }
    }

    @Override
    public Dimension getPreferedSize(Graphics2D g)
    {
        return new Dimension(320, 240);
    }

    abstract void layout(Graphics2D g);
}
