from clear19.App.screens import Screens
from clear19.logitech.g19 import G19Key, DisplayKey
from clear19.widgets.geometry.anchor import Anchor
from clear19.widgets.geometry.point import AnchoredPoint
from clear19.widgets.geometry.rectangle import Rectangle
from clear19.widgets.text_widget import TimeWidget, TextWidget
from clear19.widgets.widget import Screen, AppWidget


class MainScreen(Screen):
    t: TimeWidget

    def __init__(self, parent: AppWidget):
        super().__init__(parent, "Main")

        self.t = TimeWidget(self, "%a %d.%m.%Y\n%H:%M:%S",
                            h_alignment=TextWidget.HAlignment.CENTER,
                            v_alignment=TextWidget.VAlignment.CENTER)
        self.t.rectangle = Rectangle(AnchoredPoint(0, 0, Anchor.TOP_LEFT), self.size)
        self.t.fit_font_size()

        self.children.append(self.t)

    def on_key_down(self, key: G19Key):
        if super().on_key_down(key):
            return True
        if key == DisplayKey.UP:
            self.app.current_screen = Screens.TIME
            return True
