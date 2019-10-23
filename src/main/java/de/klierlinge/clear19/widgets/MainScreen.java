package de.klierlinge.clear19.widgets;

import java.awt.Dimension;
import java.awt.Graphics2D;

import de.klierlinge.clear19.App;
import de.klierlinge.clear19.data.system.CpuUsage;

public class MainScreen extends Screen
{
    final DateTimeWidget dateTimeWidget;
    final AnalogClock analogClock;
    final AutoUpdateTextWidget cpuWidget;

    final CpuUsage cpuUsage;
    
    public MainScreen(App parent, Graphics2D g)
    {
        super (parent);
        
        cpuUsage = new CpuUsage(app);
        
        dateTimeWidget = new DateTimeWidget(this);
        analogClock = new AnalogClock(dateTimeWidget);
        
        cpuWidget = new AutoUpdateTextWidget(this, 1000, () -> Float.toString(cpuUsage.currentLoad[2]));
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
        
        cpuWidget.setSize(new Dimension(200, 30));
        cpuWidget.fitFontSize(g, cpuWidget.getSize());
        cpuWidget.setTopLeft(getTopLeft());
    }
}
