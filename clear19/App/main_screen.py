from clear19.App import Global
from clear19.App.screens import Screens
from clear19.data.wetter_com import WetterCom
from clear19.logitech.g19 import G19Key, DisplayKey
from clear19.widgets.geometry import Anchor, VAnchor, AnchoredPoint, Rectangle, Size
from clear19.widgets.line import Line
from clear19.widgets.text_widget import TimeWidget, TextWidget
from clear19.widgets.weather_widget import WeatherWidgets
from clear19.widgets.widget import Screen, AppWidget


class MainScreen(Screen):

    def __init__(self, parent: AppWidget):
        super().__init__(parent, "Main")

        lv3 = Line(self, Line.Orientation.VERTICAL)
        lv3.rectangle = Rectangle(AnchoredPoint(self.width / 4 * 3, 0, Anchor.TOP_LEFT),
                                  Size(lv3.preferred_size().width, self.height))
        self.children.append(lv3)

        d = TimeWidget(self, "%a %d.%m.%Y", h_alignment=TextWidget.HAlignment.CENTER)
        d.rectangle = Rectangle(lv3.position(Anchor.TOP_RIGHT).anchored(Anchor.TOP_LEFT),
                                lv3.position(Anchor.TOP_RIGHT) - self.position(Anchor.BOTTOM_RIGHT))
        d.fit_font_size()
        d.set_height(d.preferred_size.height, VAnchor.TOP)
        self.children.append(d)

        t = TimeWidget(self, "%H:%M:%S")
        t.rectangle = Rectangle(d.position(Anchor.BOTTOM_LEFT).anchored(Anchor.TOP_LEFT),
                                d.position(Anchor.BOTTOM_LEFT) - self.position(Anchor.BOTTOM_RIGHT))
        t.fit_font_size()
        t.set_height(t.preferred_size.height, VAnchor.TOP)
        self.children.append(t)

        lh = Line(self, Line.Orientation.HORIZONTAL)
        lh.rectangle = Rectangle(t.position(Anchor.BOTTOM_LEFT).anchored(Anchor.TOP_LEFT),
                                 Size(self.width - lv3.left, lh.preferred_size().height))
        self.children.append(lh)

        lv3.set_height(lh.bottom, VAnchor.TOP)

        wc = WetterCom('DE0008184003', Global.download_manager)
        wps = wc.load_weather(lambda wps2: ww.set_weather_periods(wps2))
        ww = WeatherWidgets(self, wps)
        ww.rectangle = Rectangle(self.position(Anchor.BOTTOM_LEFT), ww.preferred_size)
        self.children.append(ww)

    def on_key_down(self, key: G19Key):
        if super().on_key_down(key):
            return True
        if key == DisplayKey.UP:
            self.app.current_screen = Screens.TIME
            return True
