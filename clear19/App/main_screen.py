import dataclasses
import json
from datetime import timedelta, datetime
from typing import Optional, List, Any, Dict
from xml.sax.saxutils import quoteattr

from clear19.App import Global
from clear19.App.screens import Screens
from clear19.data import Config
from clear19.data.wetter_com import WetterCom, WeatherPeriod
from clear19.logitech.g19 import G19Key, DisplayKey
from clear19.widgets.color import Color
from clear19.widgets.bar_widget import BarWidget
from clear19.widgets.geometry import Anchor, VAnchor, AnchoredPoint, Rectangle, Size, Point
from clear19.widgets.line import Line
from clear19.widgets.media_player_widgets import MediaPlayerTrackTitleWidget, MediaPlayerTrackPositionWidget, \
    MediaPlayerTrackDurationWidget, MediaPlayerTrackRemainingWidget, MediaPlayerAlbumArt
from clear19.widgets.system_stats_widgets import CpuLoadBarWidget, CpuLoadTextWidget, MemStatsBar, DiskStats, \
    ProcessList
from clear19.widgets.text_widget import TimeWidget, TextWidget, Font
from clear19.widgets.weather_widget import WeatherWidgets, WeatherWidget
from clear19.widgets.widget import Screen, AppWidget


class MainScreen(Screen):
    wetter_com: WetterCom
    weather_widgets: WeatherWidgets = None

    def __init__(self, parent: AppWidget):
        super().__init__(parent, "Main")

        self.lv2_3 = Line(self, Line.Orientation.VERTICAL)
        self.lv2_3.rectangle = Rectangle(AnchoredPoint(self.width / 3 * 2, 0, Anchor.TOP_LEFT),
                                         Size(self.lv2_3.preferred_size().width, self.height))

        self.date = TimeWidget(self, Config.DateTime.date_format(), h_alignment=TextWidget.HAlignment.CENTER)
        self.date.rectangle = Rectangle(self.lv2_3.position(Anchor.TOP_RIGHT).anchored(Anchor.TOP_LEFT),
                                        self.position(Anchor.BOTTOM_RIGHT))
        self.date.font = dataclasses.replace(self.date.font, bold=True)
        self.date.fit_font_size()
        self.date.set_height(self.date.preferred_size.height, VAnchor.TOP)
        self.date.foreground = Color.GRAY75

        self.time = TimeWidget(self, Config.DateTime.time_format())
        self.time.rectangle = Rectangle(self.date.position(Anchor.BOTTOM_LEFT).anchored(Anchor.TOP_LEFT) + Point(0, 2),
                                        self.position(Anchor.BOTTOM_RIGHT))
        self.time.fit_font_size()
        self.time.set_height(self.time.preferred_size.height, VAnchor.TOP)
        self.time.foreground = self.date.foreground

        self.lh1 = Line(self, Line.Orientation.HORIZONTAL)
        self.lh1.rectangle = Rectangle(self.time.position(Anchor.BOTTOM_LEFT).anchored(Anchor.TOP_LEFT),
                                       Size(self.width - self.lv2_3.left, self.lh1.preferred_size().height))

        self.wetter_com = WetterCom(Config.Weather.city_code(), Global.download_manager)
        self.weather_widgets = WeatherWidgets(self, None, Global.download_manager)
        self.weather_widgets.rectangle = Rectangle(self.position(Anchor.BOTTOM_LEFT),
                                                   self.weather_widgets.preferred_size)
        self.load_weather()
        self.app.scheduler.schedule_synchronous(timedelta(minutes=10), self.load_weather)

        temp_font = Font(size=11, bold=True)
        self.out_temp = TextWidget(self, 'Out: -00.0° - -00.0°', temp_font)
        self.out_temp.rectangle = Rectangle(self.weather_widgets.position(Anchor.TOP_LEFT).anchored(Anchor.BOTTOM_LEFT)
                                            + Point(0, -1),
                                            self.out_temp.preferred_size + Size(0, 2))
        self.out_temp.foreground = Color.GRAY80
        self.out_temp.escape = False

        self.in_temp = TextWidget(self, 'In: -00.0° - -00.0°', temp_font)
        self.in_temp.rectangle = Rectangle(AnchoredPoint(self.width, self.out_temp.top, Anchor.TOP_RIGHT),
                                           self.in_temp.preferred_size)
        self.in_temp.foreground = Color.GRAY80
        self.in_temp.escape = False
        self.in_temp.h_alignment = TextWidget.HAlignment.RIGHT

        self.balcony_temp = TextWidget(self, 'Blk: -00.0°', temp_font)
        self.balcony_temp.rectangle = Rectangle(AnchoredPoint((self.out_temp.right + self.in_temp.left) / 2,
                                                              self.out_temp.top, Anchor.TOP_CENTER),
                                                self.balcony_temp.preferred_size)
        self.balcony_temp.foreground = Color.GRAY80
        self.balcony_temp.escape = False
        self.balcony_temp.h_alignment = TextWidget.HAlignment.CENTER

        def get_temp_values(_): Global.download_manager.get(Config.Weather.temp_values_url(),
                                                            self.load_temp_values,
                                                            timedelta(seconds=29))

        get_temp_values(None)
        self.app.scheduler.schedule_synchronous(timedelta(minutes=1), get_temp_values)

        self.lh3 = Line(self, Line.Orientation.HORIZONTAL)
        self.lh3.rectangle = Rectangle(self.out_temp.position(Anchor.TOP_LEFT).anchored(Anchor.BOTTOM_LEFT)
                                       + Point(0, -1),
                                       Size(self.width, self.lh3.preferred_size().height))

        self.track_title = MediaPlayerTrackTitleWidget(self, Global.media_player, Font(size=14))
        self.track_title.rectangle = Rectangle(self.lh3.position(Anchor.TOP_LEFT).anchored(Anchor.BOTTOM_LEFT),
                                               Size(self.width, self.track_title.font.font_extents().height))

        track_position_font = Font(size=11, bold=True)
        self.track_position = MediaPlayerTrackPositionWidget(self, Global.media_player, track_position_font)
        self.track_position.rectangle = Rectangle(
            self.track_title.position(Anchor.TOP_LEFT).anchored(Anchor.BOTTOM_LEFT),
            Size(self.width / 3, self.track_position.font.font_extents().height))

        self.track_duration = MediaPlayerTrackDurationWidget(self, Global.media_player, track_position_font)
        self.track_duration.rectangle = Rectangle(
            self.track_title.position(Anchor.TOP_CENTER).anchored(Anchor.BOTTOM_CENTER),
            Size(self.width / 3, self.track_duration.font.font_extents().height))
        self.track_duration.h_alignment = TextWidget.HAlignment.CENTER

        self.track_remaining = MediaPlayerTrackRemainingWidget(self, Global.media_player, track_position_font)
        self.track_remaining.rectangle = Rectangle(
            self.track_title.position(Anchor.TOP_RIGHT).anchored(Anchor.BOTTOM_RIGHT),
            Size(self.width / 3, self.track_remaining.font.font_extents().height))
        self.track_remaining.h_alignment = TextWidget.HAlignment.RIGHT

        self.album_art = MediaPlayerAlbumArt(self, Global.media_player, Anchor.CENTER_CENTER)
        self.album_art.rectangle = Rectangle(
            self.lh1.position(Anchor.BOTTOM_LEFT).anchored(Anchor.TOP_LEFT) + Point(0, 1),
            self.track_remaining.position(Anchor.TOP_RIGHT) + Point(0, -3))

        self.lh2 = Line(self, Line.Orientation.HORIZONTAL)
        self.lh2.rectangle = Rectangle(
            self.track_position.position(Anchor.TOP_LEFT).anchored(Anchor.BOTTOM_LEFT) + Point(0, -1),
            Size(self.lv2_3.left, self.lh2.preferred_size().height))

        self.lv2_3.set_height(self.lh2.bottom, VAnchor.TOP)

        self.cpu_load_text = CpuLoadTextWidget(self, Font(size=12), h_alignment=TextWidget.HAlignment.CENTER)
        self.cpu_load_text.rectangle = Rectangle(self.lh2.position(Anchor.TOP_LEFT).anchored(Anchor.BOTTOM_LEFT)
                                                 + Point(0, -1), self.cpu_load_text.preferred_size)
        self.cpu_load_text.foreground = Color.GRAY90

        self.cpu_load_bar = CpuLoadBarWidget(self, BarWidget.Orientation.VERTICAL_UP, Color.GRAY75)
        self.cpu_load_bar.rectangle = Rectangle(
            self.cpu_load_text.position(Anchor.TOP_LEFT).anchored(Anchor.BOTTOM_LEFT),
            Size(self.cpu_load_text.width, self.cpu_load_text.top))

        self.mem_stats_bar = MemStatsBar(self, Font(size=12), Color.GRAY75)
        self.mem_stats_bar.rectangle = \
            Rectangle(AnchoredPoint(self.cpu_load_bar.right, 0, Anchor.TOP_LEFT) + Point(1, 0),
                      Size(self.lv2_3.left - self.cpu_load_bar.right - 2, self.cpu_load_bar.width))
        self.mem_stats_bar.foreground = Color.WHITE.with_value(alpha=0.9)

        self.disk_stats = DiskStats(self, Font(size=12))
        self.disk_stats.rectangle = Rectangle(self.lh2.position(Anchor.TOP_RIGHT).anchored(Anchor.BOTTOM_RIGHT),
                                              self.cpu_load_text.position(Anchor.TOP_RIGHT))
        self.disk_stats.h_alignment = TextWidget.HAlignment.CENTER

        self.lhs = Line(self, Line.Orientation.HORIZONTAL)
        self.lhs.rectangle = Rectangle(self.disk_stats.position(Anchor.TOP_LEFT).anchored(Anchor.BOTTOM_LEFT)
                                       + Point(0, -1), Size(self.disk_stats.width, self.lhs.preferred_size().height))
        self.lhs.foreground = Color.GRAY50

        self.processes = ProcessList(self, 5, Font(size=12))
        self.processes.rectangle = Rectangle(self.mem_stats_bar.position(Anchor.BOTTOM_LEFT).anchored(Anchor.TOP_LEFT)
                                             + Point(2, 5),
                                             self.lhs.position(Anchor.TOP_RIGHT))

    def on_key_down(self, key: G19Key):
        if super().on_key_down(key):
            return True
        if key == DisplayKey.UP:
            self.app.current_screen = Screens.TIME
            return True

    def load_weather(self, _=None) -> Optional[List[WeatherPeriod]]:
        return self.wetter_com.load_weather(lambda wps2: self.weather_widgets.set_weather_periods(wps2))

    def load_temp_values(self, values: bytes):
        data = json.loads(values.decode('UTF-8'))
        temp_out: List[float] = []
        temp_out_date = [datetime.now()]
        self._add_temp_value(data, '062419C2687B.TEMP2', temp_out, temp_out_date)
        self._add_temp_value(data, '0674ED7469BD.TEMP', temp_out, temp_out_date)
        self._add_temp_value(data, '0674ED7469BD.TEMP2', temp_out, temp_out_date)
        temp_in: List[float] = []
        temp_in_date = [datetime.now()]
        self._add_temp_value(data, '030A84D918DC.TEMP', temp_in, temp_in_date)
        self._add_temp_value(data, '031B99C87CEE.TEMP', temp_in, temp_in_date)
        self._add_temp_value(data, '032602645A7F.TEMP', temp_in, temp_in_date)
        self._add_temp_value(data, 'PI_TEMP', temp_in, temp_in_date)
        self.out_temp.text = 'Out: <span foreground={}>{:2.1f}°</span> - <span foreground={}>{:2.1f}°</span>' \
            .format(quoteattr(Color.interpolate(min(temp_out), WeatherWidget.temp_color_gradient).to_hex()),
                    min(temp_out),
                    quoteattr(Color.interpolate(max(temp_out), WeatherWidget.temp_color_gradient).to_hex()),
                    max(temp_out))
        self.in_temp.text = 'In: <span foreground={}>{:2.1f}°</span> - <span foreground={}>{:2.1f}°</span>' \
            .format(quoteattr(Color.interpolate(min(temp_in), WeatherWidget.temp_color_gradient).to_hex()),
                    min(temp_in),
                    quoteattr(Color.interpolate(min(temp_in), WeatherWidget.temp_color_gradient).to_hex()),
                    max(temp_in))
        self.balcony_temp.text = 'Blk: <span foreground={}>{:2.1f}°</span>' \
            .format(quoteattr(Color.interpolate(float(data['062419C2687B.TEMP']['Value']),
                                                WeatherWidget.temp_color_gradient).to_hex()),
                    float(data['062419C2687B.TEMP']['Value']))

    @staticmethod
    def _add_temp_value(data: Dict[str, Dict[str, Any]], name: str, values: List[Any], max_age: List[datetime]):
        values.append(float(data[name]['Value']))
        date = datetime.strptime(data[name]['Time'], '%Y-%m-%d %H:%M:%S')
        if max_age[0] > date:
            max_age[0] = date
