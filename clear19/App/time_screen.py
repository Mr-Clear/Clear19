import math
from datetime import timedelta, datetime

from cairo import Context

from clear19 import App
from clear19.App.screens import Screens
from clear19.logitech.g19 import G19Key, DisplayKey
from clear19.widgets import Color
from clear19.widgets.geometry import Anchor, AnchoredPoint, ZERO_TOP_LEFT, Rectangle, Size
from clear19.widgets.text_widget import TimeWidget, TextWidget
from clear19.widgets.widget import Screen, AppWidget, Widget, ContainerWidget


class SplitSecondSpinner(Widget):
    def __init__(self, parent: ContainerWidget):
        super().__init__(parent)
        self.app.scheduler.schedule_synchronous(timedelta(milliseconds=40), lambda _: self.repaint())

    def paint_foreground(self, ctx: Context):
        ctx.set_source_rgb(*Color.GRAY40)
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
        ctx.set_source_rgb(*Color.WHITE)
        ctx.stroke()


class TimeScreen(Screen):
    uptime: datetime
    uptime_widget: TextWidget

    def __init__(self, parent: AppWidget):
        super().__init__(parent, "Time")

        d = TimeWidget(self, '%a %d.%m.%Y', h_alignment=TextWidget.HAlignment.CENTER)
        d.rectangle = Rectangle(AnchoredPoint(0, 0, Anchor.TOP_LEFT), self.size)
        d.fit_font_size()
        d.set_size(d.preferred_size, Anchor.TOP_LEFT)

        t = TimeWidget(self, '%H:%M:%S')
        t.rectangle = Rectangle(d.position(Anchor.BOTTOM_LEFT).anchored(Anchor.TOP_LEFT), self.size)
        t.fit_font_size()
        t.set_size(t.preferred_size, Anchor.TOP_LEFT)

        h = self.height - t.bottom
        s = SplitSecondSpinner(self)
        s.rectangle = Rectangle(t.position(Anchor.BOTTOM_RIGHT).anchored(Anchor.TOP_RIGHT),
                                Size(h, h))

        self.uptime = App.uptime()
        self.uptime_widget = TextWidget(self, self.uptime.strftime('%H:%M:%S'))
        self.uptime_widget.rectangle = Rectangle(self.position(Anchor.BOTTOM_LEFT),
                                                 Size(s.left, self.uptime_widget.preferred_size.height))
        self.app.scheduler.schedule_synchronous(timedelta(minutes=1), self._update_uptime)
        self._update_uptime()

    def on_key_down(self, key: G19Key):
        if super().on_key_down(key):
            return True
        if key == DisplayKey.DOWN:
            self.app.current_screen = Screens.MAIN
            return True

    def _update_uptime(self, _=None):
        now = datetime.now()
        if self.uptime.day == now.day:
            f = '%H:%M:%S'
        else:
            f = '%Y-%m-%d %H:%M:%S'
        passed = now - self.uptime
        hours, remainder = divmod(passed.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if passed.days > 0:
            p = '{}d {:02}:{:02}h'.format(passed.days, hours, minutes)
        elif hours > 0:
            p = '{:02}:{:02}h'.format(hours, minutes)
        else:
            p = '{:02}min'.format(minutes)
        self.uptime_widget.text = 'Up {} since {}'.format(p, self.uptime.strftime(f))
