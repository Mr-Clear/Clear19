package de.klierlinge.clear19.widgets;

import java.awt.Dimension;
import java.awt.Graphics2D;

import de.klierlinge.clear19.App;

public class MainScreen extends Screen
{
    DateTimeWidget dateTimeWidget;
    AnalogClock analogClock;

    public MainScreen(App parent, Graphics2D g)
    {
        super (parent);
        dateTimeWidget = new DateTimeWidget(this);
        analogClock = new AnalogClock(this);
        layout(g);
    }

    @Override
    void layout(Graphics2D g)
    {
        dateTimeWidget.setSize(dateTimeWidget.getPreferedSize(g));
        dateTimeWidget.setTopRight(getTopRight());
        analogClock.setSize(new Dimension(32, 24));
        analogClock.setTopRight(dateTimeWidget.getBottomRight());
    }
}
