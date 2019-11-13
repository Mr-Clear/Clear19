package de.klierlinge.clear19.widgets;

import java.awt.Graphics2D;
import java.awt.geom.AffineTransform;
import java.util.ArrayList;
import java.util.List;

public class ContainerWidget extends Widget
{
    private List<Widget> children = new ArrayList<>();
    
    public ContainerWidget(ContainerWidget parent)
    {
        super(parent);
    }
    
    protected List<Widget> getChildren()
    {
        return children;
    }

    public void setDirty(boolean childrenToo)
    {
        super.setDirty();
        
        if(childrenToo)
            for(final var child : children)
                if(child instanceof ContainerWidget)
                    ((ContainerWidget)child).setDirty(childrenToo);
                else
                    child.setDirty();
    }

    @Override
    public void paint(Graphics2D g)
    {
        paintChildren(g);
        clearDirty();
    }
    
    protected void paintChildren(Graphics2D g)
    {
        children.sort((a, b) -> Integer.compare(a.getLayer(), b.getLayer()));
        for(Widget child : children)
        {
            if (child.isDirty() && child.isVisible())
            {
                final var oldTx = g.getTransform();
                final var tx = new AffineTransform(oldTx);
                tx.setToTranslation(child.getRectangle().getLeft(), child.getRectangle().getTop());
                g.setTransform(tx);
                g.setClip(new java.awt.Rectangle(child.getRectangle().getSize().toAwtDimension()));
                child.paint(g);
                g.setTransform(oldTx);
            }
        }
    }

    @Override
    public void paintForeground(Graphics2D g)
    { /* Foreground is for children. */ }

}
