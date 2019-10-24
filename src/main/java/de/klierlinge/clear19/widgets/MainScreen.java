package de.klierlinge.clear19.widgets;

import java.awt.Dimension;
import java.awt.Font;
import java.awt.Graphics2D;

import de.klierlinge.clear19.App;

public class MainScreen extends Screen
{
    final DateTimeWidget dateTimeWidget;
    //final AnalogClock analogClock;
    final DataUpdateTextWidget cpuWidget;
    
    public MainScreen(App parent, Graphics2D g)
    {
        super (parent);
        
        dateTimeWidget = new DateTimeWidget(this);
        //analogClock = new AnalogClock(dateTimeWidget);
        
        cpuWidget = new DataUpdateTextWidget(this, app.cpuUsage, (d) -> 
            String.format("IDL:%02.0f USR:%02.0f SYS:%02.0f IRQ:%02.0f",
                d.idle * 100,
                d.user * 100,
                d.system * 100,
                (d.irq + d.softirq) * 100));
        layout(g);
    }

    @Override
    void layout(Graphics2D g)
    {
        dateTimeWidget.setTopLeft(getTopLeft());
        dateTimeWidget.setSize(getSize());
        dateTimeWidget.fitFontSize(g, dateTimeWidget.getSize());
        dateTimeWidget.pack(g);
        dateTimeWidget.setBottom(getBottom());
        //analogClock.setSize(new Dimension(20, 20));
        //analogClock.setCenter(dateTimeWidget.getCenter());
        
        cpuWidget.setFont(new Font("Consolas", Font.PLAIN, 1));
        cpuWidget.fitFontSize(g, new Dimension(getWidth(), 40));
        cpuWidget.pack(g);
        cpuWidget.setTopLeft(getTopLeft());
    }
}
