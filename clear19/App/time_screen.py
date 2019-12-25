from clear19.App.screens import Screens
from clear19.logitech.g19 import G19Key, DisplayKey
from clear19.widgets.geometry.anchor import Anchor
from clear19.widgets.geometry.anchored_point import AnchoredPoint
from clear19.widgets.geometry.rectangle import Rectangle
from clear19.widgets.text_widget import TextWidget, Font
from clear19.widgets.widget import Screen, AppWidget


class TimeScreen(Screen):
    def __init__(self, parent: AppWidget):
        super().__init__(parent, "Time")

        w = TextWidget(self, "Time Screen", Font(size=32), h_alignment=TextWidget.HAlignment.CENTER)
        w.rectangle = Rectangle(AnchoredPoint(0, 0, Anchor.TOP_LEFT), self.size)
        self.children.append(w)

    def on_key_down(self, key: G19Key):
        if key == DisplayKey.DOWN:
            self.app.set_screen(Screens.MAIN)
