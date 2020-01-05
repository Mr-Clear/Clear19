from dataclasses import replace
from datetime import datetime
from typing import List, Optional

from cairo import Context

from clear19.data.wetter_com import WeatherPeriod
from clear19.widgets.geometry import Size, Rectangle, AnchoredPoint, Anchor
from clear19.widgets.text_widget import Font
from clear19.widgets.widget import Widget, ContainerWidget


class WeatherWidget(Widget):
    _weather_period: Optional[WeatherPeriod]
    _font: Font

    def __init__(self, parent: ContainerWidget, weather_period: Optional[WeatherPeriod], font: Font = Font(size=12)):
        super().__init__(parent)
        self._weather_period = weather_period
        self._font = font

    def paint_foreground(self, ctx: Context):
        if self.weather_period:
            wp = self.weather_period
        else:
            wp = WeatherPeriod(start=datetime(2000, 1, 1), end=datetime(2000, 1, 1), temp=0, cloudiness=0,
                               rainfall=0, pop=0)
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

    @property
    def weather_period(self) -> WeatherPeriod:
        return self._weather_period

    @weather_period.setter
    def weather_period(self, weather_period: Optional[WeatherPeriod]):
        self._weather_period = weather_period
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
                 font: Font = Font(size=12)):
        super().__init__(parent)
        self._weather_periods = weather_periods
        self._font = font
        for i in range(5):
            w = WeatherWidget(self, None)
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
        self._weather_periods = weather_periods
        self._update_children()
