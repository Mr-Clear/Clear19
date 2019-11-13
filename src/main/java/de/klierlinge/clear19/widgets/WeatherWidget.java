package de.klierlinge.clear19.widgets;

import static de.klierlinge.clear19.widgets.geometry.Anchor.BOTTOM_LEFT;
import static de.klierlinge.clear19.widgets.geometry.Anchor.BOTTOM_RIGHT;
import static de.klierlinge.clear19.widgets.geometry.Anchor.TOP_LEFT;

import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics2D;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.List;

import org.apache.commons.io.FilenameUtils;

import de.klierlinge.clear19.data.web.ImageDownloader;
import de.klierlinge.clear19.data.web.Wetter_com;
import de.klierlinge.clear19.data.web.Wetter_com.WeatherPeriod;
import de.klierlinge.clear19.widgets.Border.Orientation;
import de.klierlinge.clear19.widgets.TextWidget.HAllignment;
import de.klierlinge.clear19.widgets.geometry.AnchoredPoint;
import de.klierlinge.clear19.widgets.geometry.Rectangle;
import de.klierlinge.clear19.widgets.geometry.Size;
import de.klierlinge.clear19.widgets.geometry.Point;

public class WeatherWidget extends ContainerWidget
{
    private boolean layoutCorrect = false;
    private int columns = 5;
    @SuppressWarnings("unused")
    private final ImageDownloader imageDownloader;
    List<WeatherPeriod> weatherPeriods = null;

    public WeatherWidget(ContainerWidget parent) throws IOException
    {
        super(parent);
        
        setForeground(Color.WHITE);
        
        getApp().getScheduler().schedule(1000, () -> setDirty());
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

    void layout(Graphics2D g)
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
                border.setRectangle(new Rectangle(getWidth() / columns * (i + 1) - width / 2, 0, width, getHeight(), TOP_LEFT));
                right = border.getLeft();
            }
            else
            {
                border = null;
                right = getWidth();
            }
            
            if (lastBorder == null)
                left = 0;
            else
                left = lastBorder.getRight();
            
            System.out.println("LEFT: " + left + "  RIGHT: " + right);
            
            final var period = new PeriodWidget(this, weatherPeriods.get(i));
            period.setRectangle(new AnchoredPoint(left, 0, TOP_LEFT), new Point(right, getHeight()));
            period.layout(g);
            period.setRectangle(new AnchoredPoint(left, 0, TOP_LEFT), new Point(right, period.getPreferedSize(g).getHeight()));
            
            lastBorder = border;
        }
    }

    @Override
    public void paint(Graphics2D g)
    {
        if(!layoutCorrect)
            layout(g);
        super.paint(g);
    }

    @Override
    public Size getPreferedSize(Graphics2D g)
    {
        final Screen screen = getScreen();
        return new Size(screen.getWidth(), screen.getWidth() / columns);
    }

    private class PeriodWidget extends ContainerWidget
    {
        @SuppressWarnings("unused")
        WeatherPeriod period;
        final TextWidget periodWidget;
        final TextWidget tempWidget;
        final TextWidget rainWidget;
        final Widget imageWidget;
        final TextWidget textWidget;

        PeriodWidget(ContainerWidget parent, WeatherPeriod period)
        {
            super(parent);
            this.period = period;
            
            final var font = new Font("Arial", 0, 10);
            periodWidget = new TextWidget(this, "00:00-00:00");
            periodWidget.setHAllignment(HAllignment.CENTER);
            periodWidget.setFont(font);
            
            tempWidget = new TextWidget(this, "10°C 1/8");
            tempWidget.setHAllignment(HAllignment.CENTER);
            periodWidget.setFont(font);
            
            rainWidget = new TextWidget(this, "100% 0.0mm");
            rainWidget.setHAllignment(HAllignment.CENTER);
            periodWidget.setFont(font);
            
            imageWidget = new TextWidget(this, "XXX");
            
            textWidget = new TextWidget(this, "Unbekannt");
            textWidget.setHAllignment(HAllignment.CENTER);
            periodWidget.setFont(font);
        }

        public void layout(Graphics2D g)
        {
            System.out.println(getWidth());
            periodWidget.setRectangle(Point.ZERO.anchored(TOP_LEFT), new Size(getWidth(), periodWidget.getPreferedSize(g).getHeight()));
            System.out.println(periodWidget.getRectangle());
            tempWidget.setRectangle(periodWidget.getPosition(BOTTOM_LEFT).anchored(TOP_LEFT), new Size(getWidth(), tempWidget.getPreferedSize(g).getHeight()));
            rainWidget.setRectangle(tempWidget.getPosition(BOTTOM_LEFT).anchored(TOP_LEFT), new Size(getWidth(), rainWidget.getPreferedSize(g).getHeight()));
            imageWidget.setRectangle(rainWidget.getPosition(BOTTOM_LEFT).anchored(TOP_LEFT), new Size(getWidth(), getWidth() * 122 / 143));
            textWidget.setRectangle(imageWidget.getPosition(BOTTOM_LEFT).anchored(TOP_LEFT), new Size(getWidth(), textWidget.getPreferedSize(g).getHeight()));
            System.out.println(textWidget.getRectangle());
        }
        

        @Override
        public void paintForeground(Graphics2D g)
        {
          g.setColor(Color.RED);
          g.drawLine(0, 0, getWidth(), getHeight());
          g.drawLine(0, getHeight(), getWidth(), 0);
        }

//        @Override
//        public void paintForeground(Graphics2D g)
//        {
//            layout(g);
//            g.setFont(new Font("Arial", 0, 10));
//            if(period != null)
//            {
//                var image = imageDownloader.getImage(period.getIcon(), (i) -> setDirty());
//                if(image != null)
//                {
//                    RescaleOp op = new RescaleOp(.5f, 0, null);
//                    image = op.filter(image, null);
//                    g.drawImage(image, 0, 0,getWidth(), getHeight(), null);
//                }
//                
//                g.drawString(String.format("%2d:00-%2d:00", period.getStart().getHour(), period.getStart().getHour() + 1), 0, 10);
//                g.drawString(String.format("%2d°C %d/8", period.getTemp(), period.getCloudiness()), 0, 20);
//                g.drawString(String.format("%2d%% %.1fmm", period.getPop(), period.getRainfall()), 0, 30);
//                
//                g.drawString(period.getShortText(), 0, getHeight());
//            }
//            else
//            {
//                g.setColor(Color.RED);
//                g.drawLine(0, 0, getWidth(), getHeight());
//                g.drawLine(0, getHeight(), getWidth(), 0);
//            }
//        }
        
        @Override
        public Size getPreferedSize(Graphics2D g)
        {
            return textWidget.getPosition(BOTTOM_RIGHT).toSize();
        }
    }
}
