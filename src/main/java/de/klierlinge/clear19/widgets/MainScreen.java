package de.klierlinge.clear19.widgets;

import java.awt.Font;
import java.awt.Graphics2D;
import java.util.ArrayList;

import de.klierlinge.clear19.App;
import de.klierlinge.clear19.data.system.Memory;
import de.klierlinge.clear19.widgets.Border.Orientation;
import de.klierlinge.clear19.widgets.TextWidget.HAllignment;
import de.klierlinge.clear19.widgets.geometry.Anchor;
import de.klierlinge.clear19.widgets.geometry.AnchorH;
import de.klierlinge.clear19.widgets.geometry.Vector;
import de.klierlinge.clear19.widgets.geometry.Rectangle;

public class MainScreen extends Screen
{
    final DateTimeWidget dateTimeWidget;
    final DataUpdateTextWidget cpuWidget;
    final DataUpdateTextWidget memoryWidget;
    final DataUpdateTextWidget processesWidget;
    final WeatherWidget weatherWidget;

    public MainScreen(App parent, Graphics2D g)
    {
        super(parent);

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
        
        weatherWidget = new WeatherWidget(this);

        
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
                            lines.add("00 ----------------------");
                        }
                    }
                    return  String.join("\n", lines);
                });
        
        layout(g);
    }

    @Override
    void layout(Graphics2D g)
    {
        final var w4 = getWidth() / 4;
        final var font = new Font("Consolas", Font.PLAIN, 10);
        
        final var bV3 = new Border(this, Orientation.VERTICAL);
        bV3.setAbsRect(new Rectangle(w4 * 3 - 1, 0, 3, 100, Anchor.TOP_LEFT));
        
        final var bH1 = new Border(this, Orientation.HORIZONTAL);
        
        dateTimeWidget.setAbsRect(new Rectangle(bV3.getAbsPos(Anchor.TOP_RIGHT).anchored(Anchor.TOP_LEFT), getAbsPos(Anchor.BOTTOM_RIGHT)));
        dateTimeWidget.setFont(font);
        dateTimeWidget.fitFontSize(g);
        dateTimeWidget.pack(g, Anchor.TOP_LEFT);
        
        bV3.setAbsRect(bV3.getAbsRect().withHeight(dateTimeWidget.getHeight() + 1, AnchorH.TOP));

        cpuWidget.setAbsRect(getAbsPos(Anchor.TOP_LEFT), new Vector(bV3.getAbsLeft(), dateTimeWidget.getAbsBottom() / 2));
        cpuWidget.setFont(font);
        cpuWidget.setHAllignment(HAllignment.CENTER);
        cpuWidget.fitFontSize(g);

        memoryWidget.setFont(cpuWidget.getFont());
        memoryWidget.setHAllignment(HAllignment.CENTER);
        memoryWidget.setAbsRect(cpuWidget.getAbsPos(Anchor.BOTTOM_LEFT).anchored(Anchor.TOP_LEFT), cpuWidget.getSize());
        
        bH1.setAbsRect(memoryWidget.getAbsPos(Anchor.BOTTOM_LEFT).anchored(Anchor.TOP_LEFT), new Vector(getWidth(), dateTimeWidget.getAbsBottom() + 3));

        weatherWidget.setAbsRect(getAbsPos(Anchor.BOTTOM_LEFT), weatherWidget.getPreferedSize(g));
        
        processesWidget.setFont(new Font("Consolas", Font.PLAIN, 10));
        processesWidget.setAbsRect(bH1.getAbsPos(Anchor.BOTTOM_LEFT).anchored(Anchor.TOP_LEFT), weatherWidget.getAbsPos(Anchor.TOP_RIGHT));
        processesWidget.fitFontSize(g);
    }
}
