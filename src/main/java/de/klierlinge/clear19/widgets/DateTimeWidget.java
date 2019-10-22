package de.klierlinge.clear19.widgets;

import java.awt.Color;
import java.awt.Font;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Timer;
import java.util.TimerTask;

public class DateTimeWidget extends TextWidget
{
    private DateFormat format = new SimpleDateFormat("dd.MM.YYYY\nHH:mm:ss");
    private final Timer timer = new Timer();
    private final TimerTask tt = new TimerTask()
    {
        @Override
        public void run()
        {
            setText(getFormat().format(new Date()));
        }
    };
    
    public DateTimeWidget(Widget parent)
    {
        super(parent, "00.00.0000\n00:00:00");
        setFont(new Font("Consolas", Font.BOLD, 29));
        setTextAllignment(TextAllignment.CENTER);
        tt.run();
        timer.scheduleAtFixedRate(tt, new Date((new Date().getTime() / 1000 + 1) * 1000), 1000);
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
