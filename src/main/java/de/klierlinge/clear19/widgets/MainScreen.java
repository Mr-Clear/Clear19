package de.klierlinge.clear19.widgets;

import java.awt.Dimension;
import java.awt.Font;
import java.awt.Graphics2D;
import java.util.ArrayList;

import de.klierlinge.clear19.App;
import de.klierlinge.clear19.data.system.Memory;
import de.klierlinge.clear19.widgets.TextWidget.HAllignment;

public class MainScreen extends Screen
{
    final DateTimeWidget dateTimeWidget;
    final DataUpdateTextWidget cpuWidget;
    final DataUpdateTextWidget memoryWidget;
    final DataUpdateTextWidget processesWidget;

    public MainScreen(App parent, Graphics2D g)
    {
        super(parent);

        dateTimeWidget = new DateTimeWidget(this);

        cpuWidget = new DataUpdateTextWidget(this, app.cpuLoad,
                (d) -> String.format("IDL:%02.0f USR:%02.0f SYS:%02.0f IRQ:%02.0f",
                        d.idle * 100,
                        d.user * 100,
                        d.system * 100,
                        (d.irq + d.softirq) * 100));

        memoryWidget = new DataUpdateTextWidget(this, app.memory,
                (d) -> String.format("%s / %s (%02d%%)",
                        Memory.humanReadableByteCount(d.total - d.free), 
                        Memory.humanReadableByteCount(d.total), 
                        (int)((1 - (double)d.free / d.total) * 100)));

        
        processesWidget = new DataUpdateTextWidget(this, app.processes,  (d) -> {
                    final var ps = new ArrayList<>((d.values()));
                    ps.sort((a, b) -> Double.valueOf(b.totalLoad()).compareTo(a.totalLoad()));
                    final var lines = new ArrayList<String>(4);
                    for(var i = 0; i < 5; i++)
                    {
                        if (i < ps.size())
                        {
                            final var p = ps.get(i);
                            lines.add(String.format("%02.0f %s", (p.totalLoad()) * 100 /
                                                                 app.si.getHardware().getProcessor().getLogicalProcessorCount(), 
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
        dateTimeWidget.setTopLeft(getTopLeft());
        dateTimeWidget.setSize(getSize());
        dateTimeWidget.fitFontSize(g);
        dateTimeWidget.pack(g);
        dateTimeWidget.setBottom(getBottom());

        cpuWidget.setFont(new Font("Consolas", Font.PLAIN, 10));
        cpuWidget.fitFontSize(g, new Dimension(getWidth(), 40));
        cpuWidget.pack(g);
        cpuWidget.setTopLeft(getTopLeft());

        memoryWidget.setFont(cpuWidget.getFont());
        memoryWidget.setSize(getWidth(), cpuWidget.getHeigth());
        memoryWidget.setHAllignment(HAllignment.CENTER);
        memoryWidget.setTopLeft(cpuWidget.getBottomLeft());

        processesWidget.setFont(new Font("Consolas", Font.PLAIN, 10));
        processesWidget.setSize(getWidth(), dateTimeWidget.getTop() - memoryWidget.getBottom());
        processesWidget.setTopLeft(memoryWidget.getBottomLeft());
        processesWidget.fitFontSize(g);
    }
}
