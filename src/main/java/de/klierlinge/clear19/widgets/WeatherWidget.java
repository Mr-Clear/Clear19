package de.klierlinge.clear19.widgets;

import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics2D;
import java.awt.image.RescaleOp;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.List;

import org.apache.commons.io.FilenameUtils;

import de.klierlinge.clear19.data.web.ImageDownloader;
import de.klierlinge.clear19.data.web.Wetter_com;
import de.klierlinge.clear19.data.web.Wetter_com.WeatherPeriod;
import de.klierlinge.clear19.widgets.Border.Orientation;
import de.klierlinge.clear19.widgets.geometry.Anchor;
import de.klierlinge.clear19.widgets.geometry.AnchoredPoint;
import de.klierlinge.clear19.widgets.geometry.Rectangle;
import de.klierlinge.clear19.widgets.geometry.Size;
import de.klierlinge.clear19.widgets.geometry.Vector;

public class WeatherWidget extends Widget
{
    private boolean layoutCorrect = false;
    private int columns = 5;
    private final ImageDownloader imageDownloader;
    List<WeatherPeriod> weatherPeriods = null;

    public WeatherWidget(Widget parent) throws IOException
    {
        super(parent);
        
        setForeground(Color.WHITE);
        
        getApp().scheduler.schedule(1000, () -> setDirty());
        imageDownloader = new ImageDownloader("imageCache", 1, (f) -> {
                try
                {
                    return FilenameUtils.getName(new URL(f).getPath());
                }
                catch(MalformedURLException e)
                {
                    e.printStackTrace();
                    return null;
                }
        });
        try
        {
            weatherPeriods = Wetter_com.getWeather("DE0008184003");
        }
        catch(IOException e)
        {
            e.printStackTrace();
        }
    }

    private void relayout(Graphics2D g)
    {
        layoutCorrect = true;
        getChildren().clear();

        Border lastBorder = null;
        for(var i = 0; i < columns; i++)
        {
            final Border border;
            final int left;
            final int right;
            if (i < columns - 1)
            {
                border = new Border(this, Orientation.VERTICAL);
                final var width = border.getPreferedSize(g).getWidth();
                border.setRelRect(new Rectangle(getWidth() / columns * (i + 1) - width / 2, 0, width, getHeight(), Anchor.TOP_LEFT));
                right = border.getRelLeft();
            }
            else
            {
                border = null;
                right = getWidth();
            }
            
            if (lastBorder == null)
                left = 0;
            else
                left = lastBorder.getRelRight();
            
            final var period = new PeriodWidget(this, weatherPeriods.get(i));
            period.setRelRect(new AnchoredPoint(left, 0, Anchor.TOP_LEFT), new Vector(right, getHeight()));
            
            lastBorder = border;
        }
    }

    @Override
    public void paintForeground(Graphics2D g)
    {
        if(!layoutCorrect)
            relayout(g);
    }

    @Override
    protected void paintBackground(Graphics2D g)
    {
        /* Don't paint background. */
    }

    @Override
    public Size getPreferedSize(Graphics2D g)
    {
        final Screen screen = getScreen();
        return new Size(screen.getWidth(), screen.getWidth() / columns);
    }

    private class PeriodWidget extends Widget
    {
        WeatherPeriod period;

        PeriodWidget(Widget parent, WeatherPeriod period)
        {
            super(parent);
            this.period = period;
        }

        @Override
        public void paintForeground(Graphics2D g)
        {
            g.setFont(new Font("Arial", 0, 10));
            if(period != null)
            {
                var image = imageDownloader.getImage(period.getIcon(), (i) -> setDirty());
                if(image != null)
                {
                    RescaleOp op = new RescaleOp(.5f, 0, null);
                    image = op.filter(image, null);
                    g.drawImage(image, 0, 0,getWidth(), getHeight(), null);
                }
                
                g.drawString(String.format("%2d:00-%2d:00", period.getStart().getHour(), period.getStart().getHour() + 1), 0, 10);
                g.drawString(String.format("%2d°C %d/8", period.getTemp(), period.getCloudiness()), 0, 20);
                g.drawString(String.format("%2d%% %.1fmm", period.getPop(), period.getRainfall()), 0, 30);
                
                g.drawString(period.getShortText(), 0, getHeight());
            }
            else
            {
                g.setColor(Color.RED);
                g.drawLine(0, 0, getWidth(), getHeight());
                g.drawLine(0, getHeight(), getWidth(), 0);
            }
        }
    }
}
