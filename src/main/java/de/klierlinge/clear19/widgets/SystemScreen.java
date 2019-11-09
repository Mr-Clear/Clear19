package de.klierlinge.clear19.widgets;

import java.awt.Font;
import java.awt.Graphics2D;
import java.util.ArrayList;

import de.klierlinge.clear19.App;
import de.klierlinge.clear19.App.Button;
import de.klierlinge.clear19.data.system.Memory;
import de.klierlinge.clear19.widgets.Border.Orientation;
import de.klierlinge.clear19.widgets.TextWidget.HAllignment;
import static  de.klierlinge.clear19.widgets.geometry.Anchor.*;
import de.klierlinge.clear19.widgets.geometry.AnchorV;
import de.klierlinge.clear19.widgets.geometry.Rectangle;
import de.klierlinge.clear19.widgets.geometry.Vector;

public class SystemScreen extends Screen
{
    final DateTimeWidget dateTimeWidget;
    final DataUpdateTextWidget cpuWidget;
    final DataUpdateTextWidget memoryWidget;
    final DataUpdateTextWidget processesWidget;

    public SystemScreen(App parent, Graphics2D g)
    {
        super(parent, g, "System");

        dateTimeWidget = new DateTimeWidget(this);

        cpuWidget = new DataUpdateTextWidget(this, app.systemData.cpuLoad,
                (d) -> String.format("IDL:%02.0f USR:%02.0f SYS:%02.0f IRQ:%02.0f",
                        d.idle * 100,
                        d.user * 100,
                        d.sys * 100,
                        (d.irq + d.softIrq) * 100));

        memoryWidget = new DataUpdateTextWidget(this, app.systemData.memory,
                (d) -> String.format("%s / %s (%02d%%)",
                        Memory.humanReadableByteCount(d.total - d.free), 
                        Memory.humanReadableByteCount(d.total), 
                        (int)((1 - (double)d.free / d.total) * 100)));

        
        processesWidget = new DataUpdateTextWidget(this, app.systemData.processes,  (d) -> {
                    final var ps = new ArrayList<>((d.values()));
                    ps.sort((a, b) -> Double.valueOf(b.totalLoad()).compareTo(a.totalLoad()));
                    final var lines = new ArrayList<String>(4);
                    for(var i = 0; i < 10; i++)
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
        bV3.setAbsRect(new Rectangle(w4 * 3 - 1, 0, 3, 100, TOP_LEFT));
        
        final var bH1 = new Border(this, Orientation.HORIZONTAL);
        
        dateTimeWidget.setAbsRect(bV3.getAbsPos(TOP_RIGHT).anchored(TOP_LEFT), getAbsPos(BOTTOM_RIGHT));
        dateTimeWidget.setFont(font);
        dateTimeWidget.fitFontSize(g);
        dateTimeWidget.pack(g, TOP_LEFT);
        
        bV3.setHeight(dateTimeWidget.getHeight() + 1, AnchorV.TOP);

        cpuWidget.setRelRect(getRelPos(TOP_LEFT), new Vector(bV3.getRelLeft(), dateTimeWidget.getRelBottom() / 2));
        cpuWidget.setFont(font);
        cpuWidget.setHAllignment(HAllignment.CENTER);
        cpuWidget.fitFontSize(g);

        memoryWidget.setFont(cpuWidget.getFont());
        memoryWidget.setHAllignment(HAllignment.CENTER);
        memoryWidget.setRelRect(cpuWidget.getRelPos(BOTTOM_LEFT).anchored(TOP_LEFT), cpuWidget.getSize());

        bH1.setRelRect(memoryWidget.getRelPos(BOTTOM_LEFT).anchored(TOP_LEFT), new Vector(getWidth(), dateTimeWidget.getRelBottom() + 3));

        processesWidget.setFont(new Font("Consolas", Font.PLAIN, 10));
        processesWidget.setRelRect(bH1.getRelPos(BOTTOM_LEFT).anchored(TOP_LEFT), getSize().toVector());
        processesWidget.fitFontSize(g);
    }

    @Override
    public void onButtonDown(Button button)
    {
        switch(button)
        {
            case DOWN -> 
            {
                app.setCurrentScreen(app.mainScreen);
            }
            default -> { /* Do nothing. */}
        }
    }
}
