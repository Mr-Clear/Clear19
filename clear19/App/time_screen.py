import math
from datetime import timedelta, datetime

from cairo import Context

from clear19.App.screens import Screens
from clear19.logitech.g19 import G19Key, DisplayKey
from clear19.widgets import color
from clear19.widgets.geometry.anchor import Anchor
from clear19.widgets.geometry.point import AnchoredPoint, ZERO_TOP_LEFT
from clear19.widgets.geometry.rectangle import Rectangle
from clear19.widgets.text_widget import TimeWidget
from clear19.widgets.widget import Screen, AppWidget, Widget, ContainerWidget


class SplitSecondSpinner(Widget):
    def __init__(self, parent: ContainerWidget):
        super().__init__(parent)
        self.app.scheduler.schedule_synchronous(timedelta(milliseconds=40), lambda _: self.repaint())

    def paint_foreground(self, ctx: Context):
        ctx.set_source_rgb(*color.GRAY40)
        rect = Rectangle(ZERO_TOP_LEFT, self.size)
        center = rect.position(Anchor.CENTER_CENTER)
        r = min(*self.size) / 2
        ctx.move_to(center.x, center.y)
        φ = 2 * math.pi * datetime.now().microsecond / 1000000
        ctx.arc(*center, r, -math.pi / 2, φ - math.pi / 2)
        ctx.line_to(center.x, center.y)
        ctx.fill()

        ctx.move_to(center.x, center.y)
        ctx.line_to(center.x + r * math.sin(φ), center.y - r * math.cos(φ))
        ctx.set_line_width(2)
        ctx.set_source_rgb(*color.WHITE)
        ctx.stroke()


class TimeScreen(Screen):
    def __init__(self, parent: AppWidget):
        super().__init__(parent, "Time")

        d = TimeWidget(self, "%a %d.%m.%Y")
        d.rectangle = Rectangle(AnchoredPoint(0, 0, Anchor.TOP_LEFT), self.size)
        d.fit_font_size()
        d.set_size(d.preferred_size, Anchor.TOP_LEFT)
        self.children.append(d)

        t = TimeWidget(self, "%H:%M:%S")
        t.rectangle = Rectangle(d.position(Anchor.BOTTOM_LEFT).anchored(Anchor.TOP_LEFT), self.size)
        t.fit_font_size()
        t.set_size(t.preferred_size, Anchor.TOP_LEFT)
        self.children.append(t)

        s = SplitSecondSpinner(self)
        s.rectangle = Rectangle(t.position(Anchor.BOTTOM_LEFT).anchored(Anchor.TOP_LEFT),
                                t.position(Anchor.BOTTOM_LEFT) - self.position(Anchor.BOTTOM_RIGHT))
        self.children.append(s)

    def on_key_down(self, key: G19Key):
        if super().on_key_down(key):
            return True
        if key == DisplayKey.DOWN:
            self.app.current_screen = Screens.MAIN
            return True
