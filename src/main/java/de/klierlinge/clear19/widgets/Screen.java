package de.klierlinge.clear19.widgets;

import java.awt.Graphics2D;
import java.awt.geom.AffineTransform;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import de.klierlinge.clear19.App.Button;
import de.klierlinge.clear19.widgets.geometry.Anchor;
import de.klierlinge.clear19.widgets.geometry.AnchoredPoint;
import de.klierlinge.clear19.widgets.geometry.Rectangle;
import de.klierlinge.clear19.widgets.geometry.Size;

public abstract class Screen extends ContainerWidget
{
    @SuppressWarnings("unused")
    private static final Logger logger = LogManager.getLogger(Screen.class.getName());
    private final String name;
    private final TextWidget nameWidget;
    private boolean eraseAll = true;
    
    public Screen(ContainerWidget parent, Graphics2D g, String name)
    {
        super(parent);
        setAbsRect(new Rectangle(AnchoredPoint.ZERO, getPreferedSize(null)));

        this.name = name;
        nameWidget = new TextWidget(this, name);
        setAbsRect(AnchoredPoint.ZERO, getPreferedSize(null));
        
        nameWidget.setVisible(true);
        nameWidget.setRelRect(getAbsRect());
        nameWidget.fitFontSize(g, getSize());
        nameWidget.pack(g, Anchor.TOP_LEFT);
        nameWidget.setLayer(1000);
        getApp().getScheduler().scheduleOnce(3000, () -> onButtonUp(null));
    }
    
    public String getName()
    {
        return name;
    }

    @Override
    public Size getPreferedSize(Graphics2D g)
    {
        return getApp().getPreferedSize(g);
    }

    @Override
    public void paintForeground(Graphics2D g)
    {
        if(nameWidget.isVisible())
        {
            final var oldTx = g.getTransform();
            final var oldClip = g.getClip();
            final var tx = new AffineTransform();
            tx.setToTranslation(nameWidget.getAbsLeft(), nameWidget.getAbsTop());
            g.setTransform(tx);
            g.setClip(new java.awt.Rectangle(nameWidget.getSize().toAwtDimension()));
            nameWidget.paint(g);
            g.setTransform(oldTx);
            g.setClip(oldClip);
            
        }
    }
    
    @Override
    protected void paintBackground(Graphics2D g)
    {
        if(eraseAll)
        {
            g.fillRect(0, 0, getWidth() - 1, getHeight() - 1);
            eraseAll = false;
        }
    }

    @Override
    public boolean isVisible()
    {
        return isVisible;
    }

    public void onShow(@SuppressWarnings("unused") Screen last)
    {
        nameWidget.setVisible(true);
        nameWidget.setDirty();
        setDirty(true);
        eraseAll = true;
    }
    public void onHide(@SuppressWarnings("unused") Screen next) { /* Empty default implemntation. */ }
    public void onButtonDown(@SuppressWarnings("unused") Button button) { /* Empty default implemntation. */ }
    public void onButtonUp(@SuppressWarnings("unused") Button button)
    {
        nameWidget.setVisible(false);
        setDirty(true);
        eraseAll = true;
    }
}
