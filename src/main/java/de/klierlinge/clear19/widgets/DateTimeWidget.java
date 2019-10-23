package de.klierlinge.clear19.widgets;

import java.awt.Color;
import java.awt.Font;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Objects;
import java.util.concurrent.TimeUnit;

public class DateTimeWidget extends TextWidget
{
    private DateFormat format;
    private final Runnable tt = () -> setText(getFormat().format(new Date(System.currentTimeMillis() + 500)));

    public DateTimeWidget(Widget parent)
    {
        this(parent, "dd.MM.YYYY\nHH:mm:ss");
    }
    
    public DateTimeWidget(Widget parent, String format)
    {
        this(parent, new SimpleDateFormat(format));
    }
    
    public DateTimeWidget(Widget parent, DateFormat format)
    {
        super(parent, format.format(new Date()));
        this.format = format;
        setFont(new Font("Consolas", Font.BOLD, 29));
        setHAllignment(HAllignment.CENTER);
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
        if (!Objects.equals(this.format, format))
        {
            this.format = format;
            setDirty();
        }
    }
}
