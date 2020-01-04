from dataclasses import replace

from cairo import Context

from clear19.data.wetter_com import WeatherPeriod
from clear19.widgets import color
from clear19.widgets.geometry import Size
from clear19.widgets.text_widget import Font
from clear19.widgets.widget import Widget, ContainerWidget


class WeatherWidget(Widget):
    _weather_period: WeatherPeriod
    _font: Font

    def __init__(self, parent: ContainerWidget, weather_period: WeatherPeriod, font: Font = Font(size=12)):
        super(WeatherWidget, self).__init__(parent)
        self._weather_period = weather_period
        self._font = font

    def paint_foreground(self, ctx: Context):
        ctx.set_source_rgb(*color.RED)
        ctx.rectangle(0, 0, *self.size)
        ctx.stroke()
        ctx.set_source_rgb(*self.foreground)

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
        ctx.show_text('{}°C'.format(self.weather_period.temp))
        font.set(ctx)
        x += font.font_extents().ascent
        ctx.move_to(0, x)
        ctx.show_text('{}/8'.format(self.weather_period.cloudiness))
        x += font.font_extents().ascent
        ctx.move_to(0, x)
        ctx.show_text('{}mm {}%'.format(self.weather_period.rainfall, self.weather_period.pop))

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

    def preferred_size(self) -> Size:
        return Size(64, 64)
