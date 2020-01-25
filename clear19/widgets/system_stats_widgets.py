from datetime import timedelta

from cairocffi import Context

from clear19.App import Global
from clear19.widgets import Color, draw_rounded_rectangle, Rectangle
from clear19.widgets.geometry import ZERO_TOP_LEFT
from clear19.widgets.widget import Widget, ContainerWidget


class CpuLoadWidget (Widget):
    def __init__(self, parent: ContainerWidget):
        super().__init__(parent)
        self.app.scheduler.schedule_synchronous(timedelta(seconds=1), self._update)

    def _update(self, _):
        self.dirty = True

    def paint_foreground(self, ctx: Context):
        ctx.set_line_width(1)
        ctx.set_source_rgb(*Color.GRAY75)
        draw_rounded_rectangle(ctx, Rectangle(ZERO_TOP_LEFT, self.size), 10)
        ctx.clip_preserve()
        ctx.stroke()
        cpu_count = Global.system_data.cpu_count
        for i in range(cpu_count):
            if i % 2:
                ctx.set_source_rgb(*Color.GRAY33)
            else:
                ctx.set_source_rgb(*Color.GRAY50)
            ctx.move_to(0, self.height - self.height / cpu_count * i)
            ctx.line_to(self.width, self.height - self.height / cpu_count * i)
            ctx.stroke()

        cpu_times_percent = Global.system_data.cpu_times_percent
        if cpu_times_percent:
            system = cpu_times_percent.system + cpu_times_percent.irq + cpu_times_percent.softirq + \
                     cpu_times_percent.steal + cpu_times_percent.guest + cpu_times_percent.guest_nice
            system_h = self.height / 100 * system if system > 0 else 0
            io_h = self.height / 100 * cpu_times_percent.iowait if cpu_times_percent.iowait > 0 else 0
            user_h = self.height / 100 * cpu_times_percent.user if cpu_times_percent.user > 0 else 0
            nice_h = self.height / 100 * cpu_times_percent.nice if cpu_times_percent.nice > 0 else 0
            ctx.set_source_rgb(*Color.RED)
            ctx.rectangle(0, self.height, self.width, -system_h)
            ctx.fill()
            ctx.set_source_rgb(*Color.YELLOW)
            ctx.rectangle(0, self.height - system_h, self.width, -io_h)
            ctx.fill()
            ctx.set_source_rgb(*Color.BLUE)
            ctx.rectangle(0, self.height - system_h - io_h, self.width, -user_h)
            ctx.fill()
            ctx.set_source_rgb(*Color.GREEN)
            ctx.rectangle(0, self.height - system_h - io_h - user_h, self.width, -nice_h)
            ctx.fill()
