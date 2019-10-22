package de.klierlinge.clear19.widgets;

import java.awt.Graphics2D;

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
        dateTimeWidget.setSize(dateTimeWidget.getPreferedSize(g));
        dateTimeWidget.setTopRight(this.getTopRight());
    }
}
