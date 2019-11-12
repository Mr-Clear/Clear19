package de.klierlinge.clear19.data.web;

import java.io.IOException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.Arrays;
import java.util.List;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Element;

import de.klierlinge.clear19.App;
import de.klierlinge.clear19.data.DataProvider;

public class Wetter_com extends DataProvider<Wetter_com.WeatherData>
{
    protected Wetter_com(App app)
    {
        super(new WeatherData());
        app.getScheduler().schedule(1000 * 60 * 5, this::update);
    }
    
    private void update()
    {
        updateData(null);
    }

    public static class WeatherData
    {
        public final double currentTemp;

        public WeatherData(double currentTemp)
        {
            this.currentTemp = currentTemp;
        }
        
        public WeatherData()
        {
            currentTemp = 0;
        }
    }
    
    @FunctionalInterface
    private interface colJob 
    {
        void doIt(int col, Element td);
    }
    
    private static void handleRow(Element tr, colJob job)
    {
        int col = 0;
        for(final var td : tr.children())
        {
            job.doIt(col, td);
            col++;
        }
    }
    
    public static List<WeatherPeriod> getWeather(String location) throws IOException
    {
        final var url = "https://www.wetter.com/deutschland/" + location + ".html";
        final var doc = Jsoup.connect(url).get();
        final var periods = new WeatherPeriod[24];
        for(int i = 0; i < periods.length; i++)
            periods[i] = new WeatherPeriod();
 
        final var tbody = doc.getElementById("vhs-detail-diagram").child(0);
        var tr = tbody.children().first();
        /* Sunrise/Sunset row */
        
        tr = tr.nextElementSibling();
        /* Line */
        
        tr = tr.nextElementSibling();
        /* Time */
        var time = LocalDateTime.of(LocalDate.now(), LocalTime.of(Integer.parseInt(tr.getElementsByTag("div").first().text().substring(0, 2)) - 1, 0));
        for(var i = 0; i < periods.length; i++)
        {
            periods[i].start = time;
            time = time.plusHours(1);
        }

        tr = tr.nextElementSibling();
        /* Weather title */

        tr = tr.nextElementSibling();
        /* Weather */
        handleRow(tr, (col, td) -> {
            final var img = td.children().first();
            periods[col].icon = img.attr("data-single-src");
            periods[col].shortText = img.attr("alt");
            periods[col].longText = img.attr("title");
        });

        tr = tr.nextElementSibling();
        /* Temperature title */

        tr = tr.nextElementSibling();
        /* Temperature */
        handleRow(tr, (col, td) -> periods[col].temp = Integer.parseInt(td.children().first().children().first().text()));

        tr = tr.nextElementSibling();
        /* POP title */

        tr = tr.nextElementSibling();
        /* POP */
        handleRow(tr, (col, td) -> periods[col].pop = Integer.parseInt(td.text()));

        tr = tr.nextElementSibling();
        /* Rainfall title */

        tr = tr.nextElementSibling();
        /* Rainfall */
        handleRow(tr, (col, td) -> periods[col].rainfall = Double.parseDouble(td.text()));

        tr = tr.nextElementSibling();
        /* Wind title */

        tr = tr.nextElementSibling();
        /* Wind direction */
        handleRow(tr, (col, td) -> periods[col].windDirection = td.text());

        tr = tr.nextElementSibling();
        /* Wind speed */
        handleRow(tr, (col, td) -> periods[col].windSpeed = Integer.parseInt(td.text()));

        tr = tr.nextElementSibling();
        /* Pressure title */

        tr = tr.nextElementSibling();
        /* Pressure */
        handleRow(tr, (col, td) -> periods[col].pressure = Integer.parseInt(td.text()));

        tr = tr.nextElementSibling();
        /* Humidity title */

        tr = tr.nextElementSibling();
        /* Humidity */
        handleRow(tr, (col, td) -> periods[col].humidity = Integer.parseInt(td.text()));

        tr = tr.nextElementSibling();
        /* Cloudiness title */

        tr = tr.nextElementSibling();
        /* Cloudiness */
        handleRow(tr, (col, td) -> periods[col].cloudiness = Integer.parseInt(td.text().substring(0, 1)));

        return Arrays.asList(periods);
    }
    
    public static void main(String... args) throws IOException
    {
        for(final var p : getWeather("DE0008184003"))
            System.out.println("P: " + p);
    }
    
    public static class WeatherPeriod
    {
        private LocalDateTime start;
        private String shortText;
        private String longText;
        private String icon;
        private int temp;
        private int pop; /* Probability of precipitation */
        private double rainfall;
        private String windDirection;
        private int windSpeed;
        private int pressure;
        private int humidity;
        private int cloudiness;
        
        public LocalDateTime getStart()
        {
            return start;
        }
        
        public String getLongText()
        {
            return longText;
        }

        public String getIcon()
        {
            return icon;
        }

        public String getShortText()
        {
            return shortText;
        }

        public int getTemp()
        {
            return temp;
        }

        public int getPop()
        {
            return pop;
        }

        public double getRainfall()
        {
            return rainfall;
        }

        public String getWindDirection()
        {
            return windDirection;
        }

        public int getWindSpeed()
        {
            return windSpeed;
        }
        
        public int getPressure()
        {
            return pressure;
        }

        public int getHumidity()
        {
            return humidity;
        }

        public int getCloudiness()
        {
            return cloudiness;
        }

        @Override
        public String toString()
        {
            return String.format("%02d:%02d %2d°C %2d%% %.2f l/m² %2s %d km/h %4d hPa %2d %% %d/8 %s",
                    start.getHour(), start.getMinute(), temp, pop, rainfall, windDirection, windSpeed,
                    pressure, humidity, cloudiness, shortText);
        }
    }
    
    
}
