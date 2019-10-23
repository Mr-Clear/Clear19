package de.klierlinge.clear19.widgets;

import java.awt.Dimension;
import java.awt.Graphics2D;

import de.klierlinge.clear19.App;

public class MainScreen extends Screen
{
    final DateTimeWidget dateTimeWidget;
    final AnalogClock analogClock;

    public MainScreen(App parent, Graphics2D g)
    {
        super (parent);
        dateTimeWidget = new DateTimeWidget(this);
        analogClock = new AnalogClock(dateTimeWidget);
        layout(g);
    }

    @Override
    void layout(Graphics2D g)
    {
        dateTimeWidget.setTopLeft(getTopLeft());
        dateTimeWidget.setSize(getSize());
        dateTimeWidget.fitFontSize(g, dateTimeWidget.getSize());
        dateTimeWidget.setSize(dateTimeWidget.getPreferedSize(g));
        dateTimeWidget.setBottom(getBottom());
        analogClock.setSize(new Dimension(20, 20));
        analogClock.setCenter(dateTimeWidget.getCenter());
    }
}
