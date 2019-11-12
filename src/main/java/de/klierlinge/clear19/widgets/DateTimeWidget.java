package de.klierlinge.clear19.widgets;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Objects;

public class DateTimeWidget extends TextWidget
{
    private DateFormat format;
    private final Runnable tt = () -> setText(getFormat().format(new Date(System.currentTimeMillis() + 500)));

    public DateTimeWidget(ContainerWidget parent)
    {
        this(parent, "dd.MM.YYYY\nHH:mm:ss");
    }
    
    public DateTimeWidget(ContainerWidget parent, String format)
    {
        this(parent, new SimpleDateFormat(format));
    }
    
    public DateTimeWidget(ContainerWidget parent, DateFormat format)
    {
        super(parent, format.format(new Date()));
        this.format = format;
        setHAllignment(HAllignment.CENTER);
        tt.run();
        getApp().getScheduler().schedule(1000, tt);
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
