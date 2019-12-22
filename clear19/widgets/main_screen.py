from clear19.widgets.geometry.anchor import Anchor
from clear19.widgets.geometry.anchored_point import AnchoredPoint
from clear19.widgets.geometry.rectangle import Rectangle
from clear19.widgets.text_widget import TimeWidget
from clear19.widgets.widget import Screen, AppWidget


class MainScreen(Screen):
    t: TimeWidget

    def __init__(self, parent: AppWidget):
        super().__init__(parent, "Main")

        self.t = TimeWidget(self, "%a %d.%m.%Y\n%H:%M:%S")
        self.t.rectangle = Rectangle(AnchoredPoint(0, 0, Anchor.TOP_LEFT), self.size)
        self.t.fit_font_size()

        self.children.append(self.t)
