package de.klierlinge.clear19.widgets;

import java.awt.Color;
import java.awt.Font;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.concurrent.TimeUnit;

public class DateTimeWidget extends TextWidget
{
    private DateFormat format = new SimpleDateFormat("dd.MM.YYYY\nHH:mm:ss");
    private final Runnable tt = () -> setText(getFormat().format(new Date(System.currentTimeMillis() + 500)));
    
    public DateTimeWidget(Widget parent)
    {
        super(parent, "00.00.0000\n00:00:00");
        setFont(new Font("Consolas", Font.BOLD, 29));
        setTextAllignment(TextAllignment.CENTER);
        tt.run();
        final long ctm = System.currentTimeMillis();
        final long delay = (ctm / 1000 + 1) * 1000 - ctm - 3;
        app.scheduler.scheduleAtFixedRate(tt, delay, 1000, TimeUnit.MILLISECONDS);
        setBackground(Color.DARK_GRAY);
    }

    public DateFormat getFormat()
    {
        return format;
    }

    public void setFormat(DateFormat format)
    {
        this.format = format;
    }
}
