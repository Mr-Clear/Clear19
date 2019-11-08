package de.klierlinge.clear19.widgets;

import java.awt.Graphics2D;

import de.klierlinge.clear19.widgets.Border.Orientation;
import de.klierlinge.clear19.widgets.geometry.Anchor;
import de.klierlinge.clear19.widgets.geometry.Rectangle;
import de.klierlinge.clear19.widgets.geometry.Size;

public class WeatherWidget extends Widget
{
    private boolean layoutCorrect = false;
    private int columns = 6;
    
    public WeatherWidget(Widget parent)
    {
        super(parent);
        app.scheduler.schedule(1000, () -> setDirty());
    }

    private void relayout(Graphics2D g)
    {
        layoutCorrect = true;
        children.clear();

        for(int i = 1; i < columns; i++)
        {
            final Border b = new Border(this, Orientation.VERTICAL);
            final int width = b.getPreferedSize(g).getWidth();
            b.setRelRect(new Rectangle(getWidth() / columns * i - width / 2, 0, width, getHeight(), Anchor.TOP_LEFT));
        }
    }
    
    @Override
    public void paintForeground(Graphics2D g)
    {
        if (!layoutCorrect)
            relayout(g);
    }
    
    @Override
    protected void paintBackground(Graphics2D g)
    {
        /* Don't paint background. */
    }

    @Override
    public Size getPreferedSize(Graphics2D g)
    {
        final Screen screen = getScreen();
        return new Size(screen.getWidth(), screen.getWidth() / columns);
    }

}
