package de.klierlinge.clear19.widgets;

import java.awt.Graphics2D;
import java.awt.Point;
import java.awt.Rectangle;

public class MainScreen extends Screen
{
    DateTimeWidget dateTimeWidget;
    
    public MainScreen(Graphics2D g)
    {
        dateTimeWidget = new DateTimeWidget(this);
        
        children.add(dateTimeWidget);
        layout(g);
    }

    @Override
    void layout(Graphics2D g)
    {
        dateTimeWidget.setPos(new Rectangle(new Point(10, 10), dateTimeWidget.getPreferedSize(g)));
    }
}
