from dataclasses import replace
from typing import List

from cairo import Context

from clear19.data.wetter_com import WeatherPeriod
from clear19.widgets.geometry import Size, Rectangle, AnchoredPoint, Anchor
from clear19.widgets.text_widget import Font
from clear19.widgets.widget import Widget, ContainerWidget


class WeatherWidget(Widget):
    _weather_period: WeatherPeriod
    _font: Font

    def __init__(self, parent: ContainerWidget, weather_period: WeatherPeriod, font: Font = Font(size=12)):
        super().__init__(parent)
        self._weather_period = weather_period
        self._font = font

    def paint_foreground(self, ctx: Context):
        font = self.font
        big_font = replace(font, size=self.font.size * 1.5)
        x: float = 0
        font.set(ctx)
        x += font.font_extents().ascent
        ctx.move_to(0, x)
        ctx.show_text('{}-{}'.format(self.weather_period.start.strftime('%H:%M'),
                                     self.weather_period.end.strftime('%H:%M')))
        big_font.set(ctx)
        x += big_font.font_extents().ascent
        ctx.move_to(0, x)
        ctx.show_text('{:.0f}°C'.format(self.weather_period.temp))
        font.set(ctx)
        x += font.font_extents().ascent
        ctx.move_to(0, x)
        ctx.show_text('{:.0f}/8'.format(self.weather_period.cloudiness))
        x += font.font_extents().ascent
        ctx.move_to(0, x)
        ctx.show_text('{:.1f}mm {:.0f}%'.format(self.weather_period.rainfall, self.weather_period.pop))

    @property
    def weather_period(self) -> WeatherPeriod:
        return self._weather_period

    @weather_period.setter
    def weather_period(self, weather_period: WeatherPeriod):
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

    def __init__(self, parent: ContainerWidget, weather_periods: List[WeatherPeriod], font: Font = Font(size=12)):
        super().__init__(parent)
        self._weather_periods = weather_periods
        self._font = font

        n = 0
        for i in range(5):
            m = 1 if i < 2 else i
            combined = None
            for j in range(n, n + m):
                if not combined:
                    combined = weather_periods[j]
                else:
                    combined += weather_periods[j]
            n += m
            w = WeatherWidget(self, combined)
            w.rectangle = Rectangle(AnchoredPoint(i * w.preferred_size.width, 0, Anchor.TOP_LEFT), w.preferred_size)
            self.children.append(w)

    @property
    def preferred_size(self) -> Size:
        return Size(64 * 5, 64)
