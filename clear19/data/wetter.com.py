import datetime
import logging

import urllib.request
from dataclasses import dataclass
from typing import List

from bs4 import BeautifulSoup, Tag


@dataclass
class WeatherPeriod:
    start: datetime = None
    short_text: str = None
    long_text: str = None
    icon: str = None
    temp: int = None
    pop: int = None  # Probability of precipitation
    rainfall: float = None
    wind_direction: str = None
    wind_speed: int = None
    pressure: int = None
    humidity: int = None
    cloudiness: int = None


class WetterCom:
    location_id: str

    def __init__(self, location_id: str):
        self.location_id = location_id

    def load_weather(self):
        #url = 'https://www.wetter.com/deutschland/{}.html'.format(self.location_id)
        url = 'file:test.html'
        html = urllib.request.urlopen(url).read()
        s = BeautifulSoup(html, 'html.parser')
        t_body: Tag = s.select('#vhs-detail-diagram')[0]

        wp: List[WeatherPeriod] = []
        for i in range(24):
            wp.append(WeatherPeriod())

        tr_sunset = t_body.contents[1]
        tr_time = t_body.contents[5]
        tr_weather = t_body.contents[9]

        i = 0
        for td in tr_weather.contents:
            if td.name == 'td':
                for img in td.contents:
                    if img.name == 'img':
                        wp[i].icon = img.attrs['data-single-src']
                        wp[i].short_text = img.attrs['alt']
                        wp[i].long_text = img.attrs['title']
                        i += 1

        for w in wp:
            print(w)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s [%(levelname)-8s] %(message)s", level=logging.DEBUG, force=True)
    w = WetterCom('DE0008184003')
    w.load_weather()
