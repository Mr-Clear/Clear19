import dataclasses
from typing import List, Optional

from clear19.data.download_manager import DownloadManager
from clear19.data.wetter_com import WeatherPeriod
from clear19.widgets.color import Color
from clear19.widgets.geometry import Size, Rectangle, AnchoredPoint, Anchor, Point
from clear19.widgets.image_widget import ImageWidget
from clear19.widgets.line import Line
from clear19.widgets.text_widget import Font, TextWidget
from clear19.widgets.widget import ContainerWidget


class WeatherWidget(ContainerWidget):
    _weather_period: Optional[WeatherPeriod]
    _font: Font
    _download_manager: DownloadManager

    _from_to_widget: TextWidget
    _temp_widget: TextWidget
    _cloudiness_widget: TextWidget
    _rain_widget: TextWidget
    _icon_widget: ImageWidget

    temp_color_gradient = {
        40: Color(0, 0, 0),
        25: Color(1, 0, 0),
        18: Color(1, 1, 0),
        9.5: Color(0.5, 0.5, 1),
        1: Color(0, 0, 1),
        -1: Color(0, 1, 1),
        -20: Color(1, 1, 1)}

    cloudiness_color_gradient = {
        0: Color(0.5, 0.5, 1),
        3: Color(0.2, 0.2, 1),
        8: Color.GRAY50}

    rain_color_gradient = {
        0: Color.GRAY75,
        3: Color(0.5, 0.5, 1),
        8: Color.BLUE,
        10: Color.RED}

    def __init__(self, parent: ContainerWidget, weather_period: Optional[WeatherPeriod],
                 download_manager: DownloadManager, font: Font = Font(size=9, bold=True)):
        super().__init__(parent)
        self._download_manager = download_manager
        self.font = font

        self._icon_widget = ImageWidget(self)
        self._icon_widget.rectangle = Rectangle(self.size.position(Anchor.CENTER_RIGHT), self.size / 1.5)

        self._from_to_widget: TextWidget = TextWidget(self, '00:00-00:00', self.font)
        self._from_to_widget.rectangle = Rectangle(AnchoredPoint(0, 1, Anchor.TOP_LEFT),
                                                   self._from_to_widget.preferred_size)
        self._from_to_widget.h_alignment = TextWidget.HAlignment.CENTER
        self._from_to_widget.background = None

        self._temp_widget = TextWidget(self, '-11.3°C', dataclasses.replace(self.font, size=self.font.size * 1.5))
        self._temp_widget.rectangle = Rectangle(self._from_to_widget.position(Anchor.BOTTOM_LEFT)
                                                .anchored(Anchor.TOP_LEFT) + Point(0, 4),
                                                self._temp_widget.preferred_size)
        self._temp_widget.foreground = Color.RED
        self._temp_widget.background = None

        self._cloudiness_widget = TextWidget(self, '0/0', self.font)
        self._cloudiness_widget.rectangle = Rectangle(self._temp_widget.position(Anchor.BOTTOM_LEFT)
                                                      .anchored(Anchor.TOP_LEFT) + Point(0, 4),
                                                      self._cloudiness_widget.preferred_size)
        self._cloudiness_widget.background = None

        self._rain_widget = TextWidget(self, '22.3mm 100%', self.font)
        self._rain_widget.rectangle = Rectangle(self._cloudiness_widget.position(Anchor.BOTTOM_LEFT)
                                                .anchored(Anchor.TOP_LEFT) + Point(0, 4),
                                                self._rain_widget.preferred_size)
        self._rain_widget.background = None

        self.weather_period = weather_period

    def do_layout(self):
        for child in self.children:
            if isinstance(child, TextWidget):
                child.set_size(Size(self.width, child.height), Anchor.TOP_LEFT)
        self._icon_widget.rectangle = Rectangle(self.size.position(Anchor.CENTER_RIGHT) + Point(5, 0), self.size / 1.5)

    @property
    def weather_period(self) -> WeatherPeriod:
        return self._weather_period

    @weather_period.setter
    def weather_period(self, weather_period: Optional[WeatherPeriod]):
        self._weather_period = weather_period
        if weather_period:
            self._from_to_widget.foreground = Color.GRAY90
            self._from_to_widget.text = '{}-{}'.format(weather_period.start.strftime('%H:%M'),
                                                       weather_period.end.strftime('%H:%M'))
            self._temp_widget.foreground = Color.interpolate(weather_period.temp, self.temp_color_gradient)
            self._temp_widget.text = '{:.0f}°C'.format(weather_period.temp)
            self._cloudiness_widget.foreground = Color.interpolate(weather_period.cloudiness,
                                                                   self.cloudiness_color_gradient)
            self._cloudiness_widget.text = '{:.0f}/8'.format(weather_period.cloudiness)
            self._rain_widget.foreground = Color.interpolate(
                weather_period.rainfall * (1 - (1 - weather_period.pop) ** 2), self.rain_color_gradient)
            self._rain_widget.text = '{:.1f}mm {:.0f}%'.format(weather_period.rainfall, weather_period.pop)
            self._icon_widget.load_image(self._download_manager.get(weather_period.icon, self._icon_widget.load_image))
        else:
            self._from_to_widget.foreground = Color.GRAY90
            self._from_to_widget.text = '00:00-00:00'
            self._temp_widget.foreground = Color.GRAY50
            self._temp_widget.text = '---°C'
            self._cloudiness_widget.foreground = Color.GRAY50
            self._cloudiness_widget.text = '0/0'
            self._rain_widget.foreground = Color.GRAY50
            self._rain_widget.text = '--mm --%'
            self._icon_widget.load_image(None)
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
        return Size(64 - 3 * 4 / 5, self._rain_widget.bottom)


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
            w.rectangle = Rectangle(AnchoredPoint(i * (w.preferred_size.width + 3), 0, Anchor.TOP_LEFT),
                                    w.preferred_size)

            l: Line = Line(self, Line.Orientation.VERTICAL)
            l.foreground = Color.GRAY67
            l.rectangle = Rectangle(w.position(Anchor.TOP_RIGHT).anchored(Anchor.TOP_LEFT),
                                    Size(l.preferred_size().width, w.height))
        self._update_children()

    def _update_children(self):
        if self.weather_periods:
            n = 0
            i = 0
            for w in self.children:
                if isinstance(w, WeatherWidget):
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
                if isinstance(w, WeatherWidget):
                    w.weather_period = None

    @property
    def preferred_size(self) -> Size:
        return Size(self.children[-1].right, self.children[0].bottom)

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
