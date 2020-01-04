import logging
import re

import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Callable

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
    wind_squall_speed: int = None
    pressure: int = None
    humidity: int = None
    cloudiness: int = None


class WetterCom:
    location_id: str

    def __init__(self, location_id: str):
        self.location_id = location_id

    def load_weather(self) -> List[WeatherPeriod]:
        #url = 'https://www.wetter.com/deutschland/{}.html'.format(self.location_id)
        url = 'file:test.html'
        html = urllib.request.urlopen(url).read()
        s = BeautifulSoup(html, 'html.parser')
        t_body: Tag = s.select('#vhs-detail-diagram')[0]

        wps: List[WeatherPeriod] = []
        for _ in range(24):
            wps.append(WeatherPeriod())

        date = None
        for t in s.find_all('h3'):
            match = re.search('[0-3][0-9]\\.[0-1][0-9]\\.20[0-9][0-9]', t.text)
            if match:
                date = datetime.strptime(match[0], "%d.%m.%Y")
                break
        if not date:
            date = datetime.now()

        start_hours = int(t_body.contents[5].contents[1].text.strip()[0:2])
        t = datetime(date.year, date.month, date.day, start_hours, 0, 0)
        t -= timedelta(hours=1)
        for wp in wps:
            wp.start = t
            t += timedelta(hours=1)

        _parse_row(wps, t_body.contents[9], _parse_weather)
        _parse_row(wps, t_body.contents[13], _parse_temp)
        _parse_row(wps, t_body.contents[17], _parse_pop)
        _parse_row(wps, t_body.contents[21], _parse_rainfall)
        _parse_row(wps, t_body.contents[25], _parse_wind_direction)
        _parse_row(wps, t_body.contents[27], _parse_wind_speed)
        _parse_row(wps, t_body.contents[31], _parse_pressure)
        _parse_row(wps, t_body.contents[35], _parse_humidity)
        _parse_row(wps, t_body.contents[39], _parse_cloudiness)

        return wps


def _parse_row(wps: List[WeatherPeriod], tr: Tag, job: Callable[[List[WeatherPeriod], int, Tag], None]):
    i = 0
    for td in tr.contents:
        if td.name == 'td':
            job(wps, i, td)
            i += 1


def _parse_weather(wps: List[WeatherPeriod], i: int, td: Tag):
    for img in td.contents:
        if img.name == 'img':
            wps[i].icon = img.attrs['data-single-src']
            wps[i].short_text = img.attrs['alt']
            wps[i].long_text = img.attrs['title']


def _parse_temp(wps: List[WeatherPeriod], i: int, td: Tag):
    wps[i].temp = int(td.contents[1].contents[1].text)


def _parse_pop(wps: List[WeatherPeriod], i: int, td: Tag):
    wps[i].pop = int(td.text)


def _parse_rainfall(wps: List[WeatherPeriod], i: int, td: Tag):
    wps[i].rainfall = float(td.text)


def _parse_wind_direction(wps: List[WeatherPeriod], i: int, td: Tag):
    wps[i].wind_direction = td.contents[2].strip()
    if len(td.contents) > 3:
        wps[i].wind_squall_speed = int(td.contents[3].contents[1].text.strip())


def _parse_wind_speed(wps: List[WeatherPeriod], i: int, td: Tag):
    wps[i].wind_speed = int(td.text)


def _parse_pressure(wps: List[WeatherPeriod], i: int, td: Tag):
    wps[i].pressure = int(td.text)


def _parse_humidity(wps: List[WeatherPeriod], i: int, td: Tag):
    wps[i].humidity = int(td.text)


def _parse_cloudiness(wps: List[WeatherPeriod], i: int, td: Tag):
    wps[i].cloudiness = int(td.text.strip()[0])


if __name__ == "__main__":
    """ Test it """
    logging.basicConfig(format="%(asctime)s [%(levelname)-8s] %(message)s", level=logging.DEBUG, force=True)
    w = WetterCom('DE0008184003')
    for wp in w.load_weather():
        print(wp)
