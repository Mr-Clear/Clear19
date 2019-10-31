package de.klierlinge.clear19.data.web;

import java.io.File;
import java.io.IOException;
import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.Set;
import java.util.TreeMap;
import java.util.regex.Pattern;

import org.jsoup.Jsoup;

import de.klierlinge.clear19.App;
import de.klierlinge.clear19.data.DataProvider;

public class Wetter_com extends DataProvider<Wetter_com.WeatherData>
{
    protected Wetter_com(App app)
    {
        super(new WeatherData());
        app.scheduler.schedule(1000 * 60 * 5, this::update);
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
    
    public static void main(String... args) throws IOException
    {
        final var url = "https://www.wetter.com/deutschland/kolbermoor/pullach/DE0008435.html";
        final var file = "/home/thomas/wetter.com.html";
        //final var s = Jsoup.connect(url).get();
        final var doc = Jsoup.parse(new File(file), "UTF-8", url);
        final var classes = Set.of("hwg-col-period", "hwg-col-icon", "hwg-col-temperature", "hwg-col-rain-icon",
                                   "hwg-col-rain-text", "hwg-col-wind-icon", "hwg-col-wind-text");
        final var ignored = Set.of("hwg-row-sunset", "hwg-row-sunrise", "hwg-row-date", "hwg-row-video",
                                  "hwg-row-ad", "hwg-row-button");
        final var periods = new TreeMap<Integer, Period>();
        var date = LocalDate.of(2019, 10, 30); // TODO: Replace this with current date;
        for(final var div : doc.getElementsByClass("hourly-weather-grid").get(0).children())
        {
            boolean found = false;
            for(final var c : classes)
            {
                final var dataNumString = div.attr("data-num");
                if (!dataNumString.isEmpty() && div.classNames().contains(c))
                {
                    final Period period;
                    final var dataNum = Integer.parseInt(dataNumString);
                    if (periods.containsKey(dataNum))
                    {
                        period = periods.get(dataNum);
                    }
                    else
                    {
                        period = new Period();
                        periods.put(dataNum, period);
                    }
                    
                    switch(c)
                    {
                        case "hwg-col-period" ->
                        {
                            final var dString = div.getElementsByClass("delta").get(0).text();
                            period.start = LocalDateTime.of(date, LocalTime.of(Integer.parseInt(dString.substring(0, 2)), Integer.parseInt(dString.substring(3, 5))));
                            period.end = LocalDateTime.of(date, LocalTime.of(Integer.parseInt(dString.substring(8, 10)), Integer.parseInt(dString.substring(11, 13))));
                            if(period.end.getHour() == 0)
                            {
                                period.end = period.end.plusDays(1);
                                date = date.plusDays(1);
                            }
                            period.text = div.getElementsByClass("vhs-text--small").get(0).text();
                        }
                        case "hwg-col-icon" ->
                        {
                            final var img = div.getElementsByTag("img").get(0);
                            period.icon = img.attr("data-single-src");
                            period.iconAlt = img.attr("alt");
                            period.iconText = img.attr("title");
                            
                        }
                        case "hwg-col-temperature" ->
                        {
                            //inal var img = div.getElementsByTag("img").get(0);
                            period.temp = Integer.parseInt(div.text().replace("°C", ""));
                        }
                        case "hwg-col-rain-icon" ->
                        {
                            final var cs = div.getElementsByClass("icon--x-large").get(0).classNames();
                            cs.remove("icon--x-large");
                            period.rainIcon = cs.iterator().next();
                        }
                        case "hwg-col-rain-text" ->
                        {
                            final var regEx = Pattern.compile("(\\d+) %( (<)?(\\d+(,\\d*)?) l/m²)?");
                            final var matcher = regEx.matcher(div.text());
                            if(matcher.matches())
                            {
                                period.pop = Integer.parseInt(matcher.group(1));
                                if(matcher.group(4) != null)
                                    period.rainfall = Double.parseDouble(matcher.group(4).replace(',', '.'));
                                else
                                    period.rainfall = 0;
                                period.rainfallSmallerThan = matcher.group(4) != null;
                            }
                            else
                                System.out.println("Failed to parse rain.");
                        }
                        case "hwg-col-wind-text" ->
                        {
                            final var regEx = Pattern.compile("(\\w+) (\\d+) km/h");
                            final var matcher = regEx.matcher(div.text());
                            if(matcher.matches())
                            {
                                period.windDirection = matcher.group(1);
                                period.windSpeed = Integer.parseInt(matcher.group(2));
                            }
                            else
                                System.out.println("Failed to parse wind.");
                        }
                        case "hwg-col-wind-icon" ->
                        {
                            /* Ignore this. */
                        }
                        default -> 
                        {
                            System.out.println("Unimplemented element: " + div);
                        }
                    }
                    found = true;
                }
            }
            for(final var c : ignored)
            {
                if (div.classNames().contains(c))
                {
                    found = true;
                    break;
                }
            }
            
            if(!found)
                System.out.println("UNKNOWN: " + div.siblingIndex() + div);
        }
        for(final var p : periods.values())
            System.out.println("P: " + p);
    }
    
    public static class Period
    {
        private LocalDateTime start;
        private LocalDateTime end;
        private String text;
        private String icon;
        private String iconAlt;
        private String iconText;
        private int temp;
        private String rainIcon;
        private int pop; /* Probability of precipitation */
        private double rainfall;
        private boolean rainfallSmallerThan;
        private String windDirection;
        private int windSpeed;
        
        public LocalDateTime getStart()
        {
            return start;
        }
        
        public LocalDateTime getEnd()
        {
            return end;
        }
        
        public Duration getDuration()
        {
            return Duration.between(start, end);
        }
        
        public String getText()
        {
            return text;
        }

        public String getIcon()
        {
            return icon;
        }

        public String getIconAlt()
        {
            return iconAlt;
        }

        public String getIconText()
        {
            return iconText;
        }

        public int getTemp()
        {
            return temp;
        }

        public String getRainIcon()
        {
            return rainIcon;
        }

        public int getPop()
        {
            return pop;
        }

        public double getRainfall()
        {
            return rainfall;
        }

        public boolean isRainfallSmallerThan()
        {
            return rainfallSmallerThan;
        }

        public String getWindDirection()
        {
            return windDirection;
        }

        public int getWindSpeed()
        {
            return windSpeed;
        }

        public boolean isValid()
        {
            return start != null && end != null;
        }
        
        @Override
        public String toString()
        {
            if(!isValid())
                return "INVALID";
            final var sb = new StringBuilder();
            if (getDuration().getSeconds() == 3600)
                sb.append(String.format("%02d:%02d", start.getHour(), start.getMinute()));
            else
                sb.append(String.format("%02d:%02d - %02d:%02d", start.getHour(), start.getMinute(), end.getHour(), end.getMinute()));
            
            sb.append(" ");
            sb.append(temp);
            sb.append("°C ");
            
            sb.append(text);
            sb.append(" ");
            
            sb.append(pop);
            sb.append("% ");
            if(rainfallSmallerThan)
                sb.append('<');
            sb.append(rainfall);
            sb.append(" l/m² ");
            
            sb.append(windDirection);
            sb.append(" ");
            sb.append(windSpeed);
            sb.append(" km/h ");
            
            return sb.toString();
        }
    }
    
    
}
