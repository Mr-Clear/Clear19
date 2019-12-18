from datetime import timedelta, datetime

from clear19.scheduler import TaskParameters
from clear19.widgets.geometry.anchor import Anchor
from clear19.widgets.geometry.anchored_point import AnchoredPoint
from clear19.widgets.geometry.rectangle import Rectangle
from clear19.widgets.geometry.size import Size
from clear19.widgets.text_widget import TextWidget, Font
from clear19.widgets.widget import Screen, AppWidget


class MainScreen(Screen):
    t: TextWidget

    def __init__(self, parent: AppWidget):
        super().__init__(parent, "Main")

        self.t = TextWidget(self, "Servus", Font(size=60))
        self.t.rectangle = Rectangle(AnchoredPoint(0, 0, Anchor.TOP_LEFT), Size(100, 100))

        self.app.scheduler.schedule_synchronous(timedelta(seconds=1), self.bla)

        self.children.append(self.t)

    def bla(self, t: TaskParameters):
        self.t.text = datetime.now().strftime("%H:%M:%S")
