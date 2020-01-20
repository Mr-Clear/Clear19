import dataclasses
from datetime import timedelta
from typing import Optional, List

from clear19.App import Global
from clear19.App.screens import Screens
from clear19.data.media_player import MediaPlayer
from clear19.data.wetter_com import WetterCom, WeatherPeriod
from clear19.logitech.g19 import G19Key, DisplayKey
from clear19.widgets.geometry import Anchor, VAnchor, AnchoredPoint, Rectangle, Size, Point
from clear19.widgets.line import Line
from clear19.widgets.media_player_widgets import MediaPlayerTrackTitleWidget, MediaPlayerTrackPositionWidget, \
    MediaPlayerTrackDurationWidget, MediaPlayerTrackRemainingWidget, MediaPlayerAlbumArt
from clear19.widgets.text_widget import TimeWidget, TextWidget, Font
from clear19.widgets.weather_widget import WeatherWidgets
from clear19.widgets.widget import Screen, AppWidget


class MainScreen(Screen):
    wetter_com: WetterCom
    weather_widgets: WeatherWidgets = None

    def __init__(self, parent: AppWidget):
        super().__init__(parent, "Main")

        lv3 = Line(self, Line.Orientation.VERTICAL)
        lv3.rectangle = Rectangle(AnchoredPoint(self.width / 4 * 3, 0, Anchor.TOP_LEFT),
                                  Size(lv3.preferred_size().width, self.height))
        self.children.append(lv3)

        d = TimeWidget(self, '%a %d.%m.%Y', h_alignment=TextWidget.HAlignment.CENTER)
        d.rectangle = Rectangle(lv3.position(Anchor.TOP_RIGHT).anchored(Anchor.TOP_LEFT),
                                lv3.position(Anchor.TOP_RIGHT) - self.position(Anchor.BOTTOM_RIGHT))
        d.font = dataclasses.replace(d.font, bold=True)
        d.fit_font_size()
        d.set_height(d.preferred_size.height, VAnchor.TOP)
        self.children.append(d)

        t = TimeWidget(self, '%H:%M:%S')
        t.rectangle = Rectangle(d.position(Anchor.BOTTOM_LEFT).anchored(Anchor.TOP_LEFT) + Point(0, 1),
                                d.position(Anchor.BOTTOM_LEFT) - self.position(Anchor.BOTTOM_RIGHT))
        t.fit_font_size()
        t.set_height(t.preferred_size.height, VAnchor.TOP)
        self.children.append(t)

        lh1 = Line(self, Line.Orientation.HORIZONTAL)
        lh1.rectangle = Rectangle(t.position(Anchor.BOTTOM_LEFT).anchored(Anchor.TOP_LEFT),
                                  Size(self.width - lv3.left, lh1.preferred_size().height))
        self.children.append(lh1)

        lv3.set_height(lh1.bottom, VAnchor.TOP)

        self.wetter_com = WetterCom('DE0008184003', Global.download_manager)
        self.weather_widgets = WeatherWidgets(self, None, Global.download_manager)
        self.weather_widgets.rectangle = Rectangle(self.position(Anchor.BOTTOM_LEFT),
                                                   self.weather_widgets.preferred_size)
        self.load_weather()
        self.app.scheduler.schedule_synchronous(timedelta(minutes=10), self.load_weather)
        self.children.append(self.weather_widgets)

        lh2 = Line(self, Line.Orientation.HORIZONTAL)
        lh2.rectangle = Rectangle(self.weather_widgets.position(Anchor.TOP_LEFT).anchored(Anchor.BOTTOM_LEFT),
                                  Size(self.width, lh2.preferred_size().height))
        self.children.append(lh2)

        mp = MediaPlayer(self.app)
        tt = MediaPlayerTrackTitleWidget(self, mp, Font(size=14))
        tt.rectangle = Rectangle(lh2.position(Anchor.TOP_LEFT).anchored(Anchor.BOTTOM_LEFT),
                                 Size(self.width, tt.font.font_extents().height))
        self.children.append(tt)

        ttf = Font(size=11)
        tp = MediaPlayerTrackPositionWidget(self, mp, ttf)
        tp.rectangle = Rectangle(tt.position(Anchor.TOP_LEFT).anchored(Anchor.BOTTOM_LEFT),
                                 Size(self.width / 3, tp.font.font_extents().height))
        self.children.append(tp)

        td = MediaPlayerTrackDurationWidget(self, mp, ttf)
        td.rectangle = Rectangle(tt.position(Anchor.TOP_CENTER).anchored(Anchor.BOTTOM_CENTER),
                                 Size(self.width / 3, td.font.font_extents().height))
        td.h_alignment = TextWidget.HAlignment.CENTER
        self.children.append(td)

        tr = MediaPlayerTrackRemainingWidget(self, mp, ttf)
        tr.rectangle = Rectangle(tt.position(Anchor.TOP_RIGHT).anchored(Anchor.BOTTOM_RIGHT),
                                 Size(self.width / 3, tr.font.font_extents().height))
        tr.h_alignment = TextWidget.HAlignment.RIGHT
        self.children.append(tr)

        aa = MediaPlayerAlbumArt(self, mp, Anchor.BOTTOM_RIGHT)
        aa.rectangle = Rectangle(lh1.position(Anchor.BOTTOM_RIGHT).anchored(Anchor.TOP_RIGHT) + Point(0, 1),
                                 lh1.position(Anchor.BOTTOM_RIGHT) - tp.position(Anchor.TOP_LEFT) - Size(0, 2))
        self.children.append(aa)

    def on_key_down(self, key: G19Key):
        if super().on_key_down(key):
            return True
        if key == DisplayKey.UP:
            self.app.current_screen = Screens.TIME
            return True

    def load_weather(self, _=None) -> Optional[List[WeatherPeriod]]:
        return self.wetter_com.load_weather(lambda wps2: self.weather_widgets.set_weather_periods(wps2))
