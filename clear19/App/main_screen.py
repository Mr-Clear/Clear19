import dataclasses
from datetime import timedelta
from typing import Optional

from clear19.App import Global
from clear19.App.screens import Screens
from clear19.data import Config
from clear19.data.fritzbox import FritzBox
from clear19.data.wetter_com import WetterCom, WeatherData
from clear19.logitech.g19 import G19Key, DisplayKey
from clear19.widgets.bar_widget import BarWidget
from clear19.widgets.color import Color
from clear19.widgets.fritz_box_widgets import FritzBoxConnectedWidget, FritzBoxIp6Widget, \
    FritzBoxIp4Widget, FritzBoxHostsWidget, FritzBoxTrafficGraphWidget, FritzBoxTrafficWidget
from clear19.widgets.geometry import Anchor, VAnchor, AnchoredPoint, Rectangle, Size, Point
from clear19.widgets.line import Line
from clear19.widgets.media_player_widgets import MediaPlayerTrackTitleWidget, MediaPlayerTrackPositionWidget, \
    MediaPlayerTrackDurationWidget, MediaPlayerTrackRemainingWidget
from clear19.widgets.system_stats_widgets import CpuLoadBarWidget, CpuLoadTextWidget, MemStatsBar, DiskStats, \
    ProcessList
from clear19.widgets.text_widget import TimeWidget, TextWidget, Font
from clear19.widgets.weather_widget import WeatherWidgets
from clear19.widgets.widget import Screen, AppWidget


class MainScreen(Screen):
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

        self.lh3 = Line(self, Line.Orientation.HORIZONTAL)
        self.lh3.rectangle = Rectangle(self.weather_widgets.position(Anchor.TOP_LEFT).anchored(Anchor.BOTTOM_LEFT)
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

        self.lh2 = Line(self, Line.Orientation.HORIZONTAL)
        self.lh2.rectangle = Rectangle(
            self.track_position.position(Anchor.TOP_LEFT).anchored(Anchor.BOTTOM_LEFT) + Point(0, -1),
            Size(self.width, self.lh2.preferred_size().height))

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

        self.disk_stats = DiskStats(Config.DiskStats.drives(), self, Font(size=12))
        self.disk_stats.rectangle = Rectangle(self.lv2_3.position(Anchor.BOTTOM_LEFT).anchored(Anchor.BOTTOM_RIGHT)
                                              + Point(0, -3), self.cpu_load_text.position(Anchor.TOP_RIGHT))
        self.disk_stats.h_alignment = TextWidget.HAlignment.CENTER

        self.lhs = Line(self, Line.Orientation.HORIZONTAL)
        self.lhs.rectangle = Rectangle(self.disk_stats.position(Anchor.TOP_LEFT).anchored(Anchor.BOTTOM_LEFT)
                                       + Point(0, -1), Size(self.disk_stats.width, self.lhs.preferred_size().height))
        self.lhs.foreground = Color.GRAY50

        self.processes = ProcessList(self, 6, Font(size=12))
        self.processes.rectangle = Rectangle(self.mem_stats_bar.position(Anchor.BOTTOM_LEFT).anchored(Anchor.TOP_LEFT)
                                             + Point(2, 5),
                                             self.lhs.position(Anchor.TOP_RIGHT))

        self.fritz_box = FritzBox(self.app.scheduler, Config.FritzBox.address(), Config.FritzBox.password())
        self.fritz_box_connected = FritzBoxConnectedWidget(self, self.fritz_box, Font(size=12))
        self.fritz_box_connected.rectangle = Rectangle(
            self.lh1.position(Anchor.BOTTOM_LEFT).anchored(Anchor.TOP_LEFT) + Point(1, 1),
            Size(self.lh1.width, self.fritz_box_connected.preferred_size.height))

        self.fritz_box_hosts = FritzBoxHostsWidget(self, self.fritz_box, Font(size=12))
        self.fritz_box_hosts.rectangle = Rectangle(
            self.fritz_box_connected.position(Anchor.BOTTOM_LEFT).anchored(Anchor.TOP_LEFT) + Point(0, 1),
            Size(self.fritz_box_connected.width, self.fritz_box_hosts.preferred_size.height))

        self.fritz_box_ip6 = FritzBoxIp6Widget(self, self.fritz_box, Font(size=12))
        self.fritz_box_ip6.rectangle = Rectangle(
            self.lv2_3.position(Anchor.BOTTOM_RIGHT).anchored(Anchor.BOTTOM_LEFT) + Point(1, -3),
            Size(self.fritz_box_connected.width, self.fritz_box_ip6.preferred_size.height))
        self.fritz_box_ip6.fit_font_size()
        self.fritz_box_ip6.set_height(self.fritz_box_ip6.preferred_size.height, VAnchor.BOTTOM)

        self.fritz_box_ip4 = FritzBoxIp4Widget(self, self.fritz_box, Font(size=12))
        self.fritz_box_ip4.rectangle = Rectangle(
            self.fritz_box_ip6.position(Anchor.TOP_LEFT).anchored(Anchor.BOTTOM_LEFT) + Point(0, -1),
            Size(self.fritz_box_connected.width, self.fritz_box_ip4.preferred_size.height))

        self.fritz_box_traffic_graph = FritzBoxTrafficGraphWidget(self, self.fritz_box)
        self.fritz_box_traffic_graph.rectangle = Rectangle(
            self.fritz_box_hosts.position(Anchor.BOTTOM_LEFT).anchored(Anchor.TOP_LEFT) + Point(0, 1),
            self.fritz_box_ip4.position(Anchor.TOP_RIGHT) + Point(0, -1))

        self.fritz_box_traffic = FritzBoxTrafficWidget(self, self.fritz_box, Font(size=12))
        self.fritz_box_traffic.rectangle = Rectangle(
            self.fritz_box_hosts.position(Anchor.BOTTOM_LEFT).anchored(Anchor.TOP_LEFT) + Point(0, 1),
            self.fritz_box_ip4.position(Anchor.TOP_RIGHT) + Point(0, -1))
        self.fritz_box_traffic.background = None

    def on_key_down(self, key: G19Key):
        if super().on_key_down(key):
            return True
        if key == DisplayKey.UP:
            self.app.current_screen = Screens.TIME
            return True
        if key == DisplayKey.LEFT:
            self.app.current_screen = Screens.WEATHER
            return True
        return False

    def load_weather(self, _=None) -> Optional[WeatherData]:
        return self.wetter_com.load_weather(lambda wps2: self.weather_widgets.set_weather_periods(wps2))
