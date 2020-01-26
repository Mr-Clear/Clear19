from datetime import timedelta
from typing import Optional

import psutil
from cairocffi import Context

from clear19.App import Global
from clear19.data.system_data import SystemData
from clear19.widgets import Rectangle
from clear19.widgets.bar_widget import BarWidget
from clear19.widgets.color import Color
from clear19.widgets.geometry import ZERO_TOP_LEFT
from clear19.widgets.text_widget import TextWidget, Font
from clear19.widgets.widget import ContainerWidget, Widget


class CpuLoadBarWidget (BarWidget):
    def __init__(self, parent: ContainerWidget, orientation: BarWidget.Orientation, border: Optional[Color] = None,
                 border_width: float = 1, border_corner: float = 5):
        super().__init__(parent, orientation, None, border, border_width, border_corner)
        Global.system_data.add_cpu_listener(self._update)

    def _update(self, load: SystemData.CpuTimes):
        system = load.system + load.irq + load.softirq + load.steal + load.guest + load.guest_nice
        self.values = [(system, Color.RED), (load.iowait, Color.YELLOW), (load.user, Color.BLUE),
                       (load.nice, Color.GREEN), (load.idle, None)]

    def paint_scale_background(self, ctx: Context):
        cpu_count = Global.system_data.cpu_count
        for i in range(cpu_count):
            if i % 2:
                ctx.set_source_rgba(*Color.GRAY33)
            else:
                ctx.set_source_rgba(*Color.GRAY50)
            ctx.move_to(0, self.height - self.height / cpu_count * i)
            ctx.line_to(self.width, self.height - self.height / cpu_count * i)
            ctx.stroke()


class CpuLoadTextWidget(TextWidget):
    def __init__(self, parent: ContainerWidget, font: Font = Font(),
                 h_alignment: TextWidget.HAlignment = TextWidget.HAlignment.LEFT):
        super().__init__(parent, "0.0", font, h_alignment)
        Global.system_data.add_cpu_listener(self._update)

    def _update(self, data: SystemData.CpuTimes):
        if data.idle > 90:
            self.text = '{:1.1f}'.format(100 - data.idle)
        elif data.idle < 1:
            self.text = "100"
        else:
            self.text = '{:2.0f}'.format(100 - data.idle)


class MemStatsBar(ContainerWidget):
    _bar: BarWidget
    _mem: SystemData.MemStats = None

    def __init__(self, parent: ContainerWidget, font: Font, border: Optional[Color] = None,
                 border_width: float = 1, border_corner: float = 5):
        super().__init__(parent)
        self._bar = BarWidget(self, BarWidget.Orientation.HORIZONTAL_LEFT_TO_RIGHT, None, border, border_width,
                              border_corner)
        self._text = TextWidget(self, '0000000000000000000000', font)
        self._text.background = None
        self._text.foreground = self.foreground
        self._text.h_alignment = TextWidget.HAlignment.CENTER
        self._text.v_alignment = TextWidget.VAlignment.CENTER
        Global.system_data.add_mem_listener(self._update)

    def do_layout(self):
        self._bar.rectangle = Rectangle(ZERO_TOP_LEFT, self.size)
        self._text.rectangle = Rectangle(ZERO_TOP_LEFT, self.size)

    def _update(self, mem: SystemData.MemStats):
        self._mem = mem
        buff = mem.buffers + mem.cached
        free = mem.total - mem.slab - mem.used - buff
        self._bar.values = [(mem.slab, Color.RED), (mem.buffers, Color.YELLOW), (mem.used, Color.BLUE),
                            (mem.cached, Color.GREEN / 2), (free, None)]
        self._text.text = '{}%  {:3.1f} GiB / {:3.1f} GiB'.format(mem.percent, (mem.total - mem.available) / 2**30,
                                                                  mem.total / 2**30)

    @Widget.foreground.setter
    def foreground(self, foreground: Color):
        self._text.foreground = foreground
        # noinspection PyArgumentList
        Widget.foreground.fset(self, foreground)


class DiskStats(TextWidget):
    def __init__(self, parent: ContainerWidget, font: Font = Font()):
        super().__init__(parent, '', font)
        self.app.scheduler.schedule_synchronous(timedelta(seconds=1), self._update)

    def _update(self, _):
        root = psutil.disk_usage('/')
        home = psutil.disk_usage('/home')
        self.text = '/: {}%, /home: {}%'.format(root.percent, home.percent)
