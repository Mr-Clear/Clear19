package de.klierlinge.clear19.widgets;

import java.awt.Dimension;
import java.awt.Graphics2D;
import java.awt.Point;
import java.awt.Rectangle;

public class MainScreen extends Screen
{
    DateTimeWidget dateTimeWidget;
    AnalogClock analogClock; 
    
    public MainScreen(Graphics2D g)
    {
        dateTimeWidget = new DateTimeWidget(this);
        analogClock = new AnalogClock(this);
        
        children.add(dateTimeWidget);
        children.add(analogClock);
        layout(g);
    }

    @Override
    void layout(Graphics2D g)
    {
        dateTimeWidget.setPos(new Rectangle(new Point(10, 10), dateTimeWidget.getPreferedSize(g)));
        analogClock.setPos(new Rectangle(new Point((int)(dateTimeWidget.getPos().getMaxX() + 10), 10), new Dimension(100, 100)));
    }
    
    
}
