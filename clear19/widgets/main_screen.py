from clear19.widgets.geometry.anchor import Anchor
from clear19.widgets.geometry.anchored_point import AnchoredPoint
from clear19.widgets.geometry.rectangle import Rectangle
from clear19.widgets.geometry.size import Size
from clear19.widgets.text_widget import TextWidget, Font
from clear19.widgets.widget import Screen, AppWidget, Widget


class MainScreen(Screen):
    t: Widget

    def __init__(self, parent: AppWidget):
        super().__init__(parent, "Main")

        w = TextWidget(self, "Servus", Font(size=80))
        w.rectangle = Rectangle(AnchoredPoint(0, 0, Anchor.TOP_LEFT), Size(100, 100))

        self.children.append(w)
