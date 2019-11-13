package de.klierlinge.clear19.widgets;

import static de.klierlinge.clear19.widgets.geometry.Anchor.BOTTOM_LEFT;
import static de.klierlinge.clear19.widgets.geometry.Anchor.BOTTOM_RIGHT;
import static de.klierlinge.clear19.widgets.geometry.Anchor.TOP_LEFT;
import static de.klierlinge.clear19.widgets.geometry.Anchor.TOP_RIGHT;
import static de.klierlinge.clear19.widgets.geometry.AnchorV.TOP;

import java.awt.Font;
import java.awt.Graphics2D;
import java.io.IOException;
import java.util.ArrayList;

import de.klierlinge.clear19.App;
import de.klierlinge.clear19.App.Button;
import de.klierlinge.clear19.data.system.Memory;
import de.klierlinge.clear19.widgets.Border.Orientation;
import de.klierlinge.clear19.widgets.TextWidget.HAllignment;
import de.klierlinge.clear19.widgets.geometry.Rectangle;
import de.klierlinge.clear19.widgets.geometry.Point;

public class MainScreen extends Screen
{
    final DateTimeWidget dateTimeWidget;
    final DataUpdateTextWidget cpuWidget;
    final DataUpdateTextWidget memoryWidget;
    final DataUpdateTextWidget processesWidget;
    final WeatherWidget weatherWidget;

    public MainScreen(App parent, Graphics2D g) throws IOException
    {
        super(parent, g, "Main Screen");

        dateTimeWidget = new DateTimeWidget(this);

        cpuWidget = new DataUpdateTextWidget(this, getApp().getSystemData().cpuLoad,
                (d) -> String.format("IDL:%02.0f USR:%02.0f SYS:%02.0f IRQ:%02.0f",
                        d.idle * 100,
                        d.user * 100,
                        d.sys * 100,
                        (d.irq + d.softIrq) * 100));

        memoryWidget = new DataUpdateTextWidget(this, getApp().getSystemData().memory,
                (d) -> String.format("%s / %s (%02d%%)",
                        Memory.humanReadableByteCount(d.total - d.free), 
                        Memory.humanReadableByteCount(d.total), 
                        (int)((1 - (double)d.free / d.total) * 100)));
        
        weatherWidget = new WeatherWidget(this);
        
        processesWidget = new DataUpdateTextWidget(this, getApp().getSystemData().processes,  (d) -> {
                    final var<ProcessData> ps = new ArrayList<>((d.values()));
                    ps.sort((a, b) -> Double.valueOf(b.totalLoad()).compareTo(a.totalLoad()));
                    final var<String> lines = new ArrayList<String>(4);
                    for(var i = 0; i < 4; i++)
                    {
                        if (i < ps.size())
                        {
                            final var p = ps.get(i);
                            lines.add(String.format("%02.0f %s", (p.totalLoad()) * 100, 
                                                                 p.name));
                        }
                        else
                        {
                            lines.add("00 ------------------------------------");
                        }
                    }
                    return  String.join("\n", lines);
                });
        
        layout(g);
    }

    public void layout(Graphics2D g)
    {
        final var w4 = getWidth() / 4;
        final var font = new Font("Consolas", Font.PLAIN, 10);
        
        final var bV3 = new Border(this, Orientation.VERTICAL);
        bV3.setRectangle(new Rectangle(w4 * 3 - 1, 0, 3, 100, TOP_LEFT));
        
        final var bH1 = new Border(this, Orientation.HORIZONTAL);
        
        dateTimeWidget.setRectangle(new Rectangle(bV3.getPosition(TOP_RIGHT).anchored(TOP_LEFT), getPosition(BOTTOM_RIGHT)));
        dateTimeWidget.setFont(font);
        dateTimeWidget.fitFontSize(g);
        dateTimeWidget.pack(g, TOP_LEFT);
        
        bV3.setRectangle(bV3.getRectangle().withHeight(dateTimeWidget.getHeight() + 1, TOP));

        cpuWidget.setRectangle(getPosition(TOP_LEFT), new Point(bV3.getLeft(), dateTimeWidget.getBottom() / 2));
        cpuWidget.setFont(font);
        cpuWidget.setHAllignment(HAllignment.CENTER);
        cpuWidget.fitFontSize(g);

        memoryWidget.setFont(cpuWidget.getFont());
        memoryWidget.setHAllignment(HAllignment.CENTER);
        memoryWidget.setRectangle(cpuWidget.getPosition(BOTTOM_LEFT).anchored(TOP_LEFT), cpuWidget.getSize());
        
        bH1.setRectangle(memoryWidget.getPosition(BOTTOM_LEFT).anchored(TOP_LEFT), new Point(getWidth(), dateTimeWidget.getBottom() + 3));

        weatherWidget.layout(g);
        weatherWidget.setRectangle(getPosition(BOTTOM_LEFT), weatherWidget.getPreferedSize(g));
        
        processesWidget.setFont(new Font("Consolas", Font.PLAIN, 10));
        processesWidget.setRectangle(bH1.getPosition(BOTTOM_LEFT).anchored(TOP_LEFT), weatherWidget.getPosition(TOP_RIGHT));
        processesWidget.fitFontSize(g);
    }

    @Override
    public void onButtonDown(Button button)
    {
        switch(button)
        {
            case UP -> 
            {
                ((App)getApp()).setCurrentScreen(App.Screens.SYSTEM);
            }
            default -> { /* Do nothing. */}
        }
    }
}
