from dataclasses import replace
from datetime import datetime
from typing import List, Optional

from cairocffi import Context, ImageSurface

from clear19.data.download_manager import DownloadManager
from clear19.data.wetter_com import WeatherPeriod
from clear19.widgets import load_svg
from clear19.widgets.geometry import Size, Rectangle, AnchoredPoint, Anchor
from clear19.widgets.text_widget import Font
from clear19.widgets.widget import Widget, ContainerWidget


class WeatherWidget(Widget):
    _weather_period: Optional[WeatherPeriod]
    _font: Font
    _download_manager: DownloadManager
    _icon: Optional[ImageSurface] = None

    def __init__(self, parent: ContainerWidget, weather_period: Optional[WeatherPeriod],
                 download_manager: DownloadManager, font: Font = Font(size=12)):
        super().__init__(parent)
        self._download_manager = download_manager
        self.weather_period = weather_period
        self.font = font

    def paint_foreground(self, ctx: Context):
        if self.weather_period:
            wp = self.weather_period
        else:
            wp = WeatherPeriod(start=datetime(2000, 1, 1), end=datetime(2000, 1, 1), temp=0, cloudiness=0,
                               rainfall=0, pop=0)

        if self._icon:
            ctx.save()
            ctx.set_source_surface(self._icon, self.size.width - self._icon.get_width(),
                                   (self.size.height - self._icon.get_height()) / 2)
            ctx.paint()
            ctx.restore()

        font = self.font
        big_font = replace(font, size=self.font.size * 1.5)
        x: float = 0
        font.set(ctx)
        x += font.font_extents().ascent
        ctx.move_to(0, x)
        ctx.show_text('{}-{}'.format(wp.start.strftime('%H:%M'),
                                     wp.end.strftime('%H:%M')))
        big_font.set(ctx)
        x += big_font.font_extents().ascent
        ctx.move_to(0, x)
        ctx.show_text('{:.0f}°C'.format(wp.temp))
        font.set(ctx)
        x += font.font_extents().ascent
        ctx.move_to(0, x)
        ctx.show_text('{:.0f}/8'.format(wp.cloudiness))
        x += font.font_extents().ascent
        ctx.move_to(0, x)
        ctx.show_text('{:.1f}mm {:.0f}%'.format(wp.rainfall, wp.pop))

    def _load_icon(self, icon_data: bytes):
        if icon_data:
            self._icon = load_svg(icon_data, *(self.size / 1.5))
        else:
            self._icon = None
        self.dirty = True

    @property
    def weather_period(self) -> WeatherPeriod:
        return self._weather_period

    @weather_period.setter
    def weather_period(self, weather_period: Optional[WeatherPeriod]):
        self._weather_period = weather_period
        if weather_period:
            self._load_icon(self._download_manager.get(weather_period.icon, self._load_icon))
        self.dirty = True

    @property
    def font(self) -> Font:
        return self._font

    @font.setter
    def font(self, font: Font):
        self._font = font
        self.dirty = True

    @property
    def preferred_size(self) -> Size:
        return Size(64, 64)


class WeatherWidgets(ContainerWidget):
    _weather_periods: List[WeatherPeriod]
    _font: Font

    def __init__(self, parent: ContainerWidget, weather_periods: Optional[List[WeatherPeriod]],
                 download_manager: DownloadManager, font: Font = Font(size=12)):
        super().__init__(parent)
        self._weather_periods = weather_periods
        self._font = font
        for i in range(5):
            w = WeatherWidget(self, None, download_manager)
            w.rectangle = Rectangle(AnchoredPoint(i * w.preferred_size.width, 0, Anchor.TOP_LEFT), w.preferred_size)
            self.children.append(w)
        self._update_children()

    def _update_children(self):
        if self.weather_periods:
            n = 0
            i = 0
            for w in self.children:
                m = i + 1
                combined = None
                for j in range(n, n + m):
                    if not combined:
                        combined = self.weather_periods[j]
                    else:
                        combined += self.weather_periods[j]
                n += m
                w.weather_period = combined
                i += 1
        else:
            for w in self.children:
                w.weather_period = None

    @property
    def preferred_size(self) -> Size:
        return Size(self.children[0].width * len(self.children), self.children[0].height)

    @property
    def weather_periods(self) -> Optional[List[WeatherPeriod]]:
        return self._weather_periods

    def set_weather_periods(self, wps: Optional[List[WeatherPeriod]]):
        self.weather_periods = wps

    @weather_periods.setter
    def weather_periods(self, weather_periods: Optional[List[WeatherPeriod]]):
        if self._weather_periods != weather_periods:
            self._weather_periods = weather_periods
            self._update_children()
