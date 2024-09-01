from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Callable, Optional, Union

# noinspection PyUnresolvedReferences
from bs4 import BeautifulSoup, Tag

from clear19.data.download_manager import DownloadManager

log = logging.getLogger(__name__)


@dataclass
class WeatherPeriod:
    """
    Contains forecast data for a defined period from wetter.com.
    """
    start: datetime = datetime.fromtimestamp(0)
    end: datetime = datetime.fromtimestamp(0)
    short_text: str = ''
    long_text: str = ''
    icon: str = ''
    temp: int = 0
    pop: int = 0  # Probability of precipitation
    rainfall: float = 0
    wind_direction: str = ''
    wind_speed: int = 0
    wind_squall_speed: int = 0
    pressure: int = 0
    humidity: int = 0
    cloudiness: int = 0

    @property
    def duration(self) -> timedelta:
        return self.end - self.start

    def __add__(self, other: WeatherPeriod) -> WeatherPeriod:
        if self.start > other.start:
            a = other
            b = self
        else:
            a = self
            b = other
        if a.end != b.start:
            raise ValueError(f'Weather periods cannot be connected: {a}, {b}')

        c = WeatherPeriod(a.start, b.end, a.short_text, a.long_text, a.icon)
        ads = a.duration.seconds
        bds = b.duration.seconds
        cds = c.duration.seconds
        c.temp = (a.temp * ads + b.temp * bds) / cds
        c.pop = 100 - (100 - a.pop) * (100 - b.pop) / 100
        c.rainfall = a.rainfall + b.rainfall
        c.wind_direction = a.wind_direction if a.wind_speed > b.wind_speed else b.wind_speed
        c.wind_speed = (a.wind_speed * ads + b.wind_speed * bds) / cds
        c.wind_squall_speed = max(a.wind_squall_speed, b.wind_squall_speed)
        c.pressure = (a.pressure * ads + b.pressure * bds) / cds
        c.humidity = (a.humidity * ads + b.humidity * bds) / cds
        c.cloudiness = (a.cloudiness * ads + b.cloudiness * bds) / cds
        return c


@dataclass
class WeatherData:
    """
    Contains forecast data from wetter.com.
    """
    location: str = ''
    periods: List[WeatherPeriod] = field(default_factory=list)


class WetterCom:
    _location_id: str
    _download_manager: DownloadManager

    def __init__(self, location_id: str, download_manager: DownloadManager):
        self._location_id = location_id
        self._download_manager = download_manager

    def load_weather(self, callback: Optional[Callable[[WeatherData], None]]) -> Optional[WeatherData]:
        url = f'https://www.wetter.com/deutschland/{self._location_id}.html'
        wps = self._download_manager.get(url, lambda content: callback(self.parse_html(content) if callback else None),
                                         timedelta(minutes=9))
        try:
            return self.parse_html(wps)
        except ValueError as e:
            log.error("Error when parsing Wetter.com.", exc_info=True)

    # noinspection PyTypeChecker
    @staticmethod
    def parse_html(html: Union[str, bytes]) -> Optional[WeatherData]:
        if not html:
            return None
        if isinstance(html, bytes):
            html = html.decode('utf-8')
        s = BeautifulSoup(html, 'html.parser')

        data = WeatherData()

        try:
            data.location = s.findAll('h2', {'class': 'delta text--white mb--'})[0].text
        except IndexError:
            log.error("Failed to parse location.", exc_info=True)

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

        # noinspection PyUnresolvedReferences
        start_hours = int(t_body.contents[5].contents[1].text.strip()[0:2])
        t = datetime(date.year, date.month, date.day, start_hours, 0, 0)
        t -= timedelta(hours=1)
        for wp in wps:
            wp.start = t
            t += timedelta(hours=1)
            wp.end = t

        _parse_row(wps, t_body.contents[9], _parse_weather)
        _parse_row(wps, t_body.contents[13], _parse_temp)
        _parse_row(wps, t_body.contents[17], _parse_pop)
        _parse_row(wps, t_body.contents[21], _parse_rainfall)
        _parse_row(wps, t_body.contents[27], _parse_wind_speed)
        _parse_row(wps, t_body.contents[25], _parse_wind_direction)
        _parse_row(wps, t_body.contents[31], _parse_pressure)
        _parse_row(wps, t_body.contents[35], _parse_humidity)
        _parse_row(wps, t_body.contents[39], _parse_cloudiness)
        data.periods = wps

        return data


def _parse_row(wps: List[WeatherPeriod], tr: Tag, job: Callable[[List[WeatherPeriod], int, Tag], None]):
    i = 0
    for td in tr.contents:
        if td.name == 'td' and i < len(wps):
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
        try:
            wps[i].wind_squall_speed = int(td.contents[3].contents[1].text.strip())
        except ValueError as e:
            log.warning("Failed to parse wind squall speed: " + str(e))
            wps[i].wind_squall_speed = 0
    else:
        wps[i].wind_squall_speed = wps[i].wind_speed


def _parse_wind_speed(wps: List[WeatherPeriod], i: int, td: Tag):
    wps[i].wind_speed = int(td.text)


def _parse_pressure(wps: List[WeatherPeriod], i: int, td: Tag):
    wps[i].pressure = int(td.text)


def _parse_humidity(wps: List[WeatherPeriod], i: int, td: Tag):
    wps[i].humidity = int(td.text)


def _parse_cloudiness(wps: List[WeatherPeriod], i: int, td: Tag):
    wps[i].cloudiness = int(td.text.strip()[0])
