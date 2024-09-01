import logging
from abc import ABC, ABCMeta, abstractmethod
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import Lock
from typing import Optional

import humanize
from cairocffi import Context

from clear19.data.fritzbox import FritzBox, FritzBoxData
from clear19.widgets.color import Color
from clear19.widgets.text_widget import TextWidget, Font
from clear19.widgets.widget import Widget, ContainerWidget

log = logging.getLogger(__name__)

class FritzBoxWidget(Widget, ABC):
    """
    Base class for all media player widgets.
    """
    __metaclass__ = ABCMeta

    _fritz_box_data_provider: FritzBox

    def __init__(self, parent: ContainerWidget, fritz_box_data_provider: FritzBox):
        self._data_mutex = Lock()
        super().__init__(parent)
        self._fritz_box_data_provider = fritz_box_data_provider
        fritz_box_data_provider.add_listener(self.update)
        self.update(fritz_box_data_provider.current_data)

    @abstractmethod
    def update(self, data: FritzBoxData):
        pass

    def paint_foreground(self, ctx: Context):
        with self._data_mutex:
            super().paint_foreground(ctx)

    @property
    def fritz_box_data_provider(self) -> FritzBox:
        return self._fritz_box_data_provider


class FritzBoxConnectedWidget(FritzBoxWidget, TextWidget):
    def __init__(self, parent: ContainerWidget, fritz_box_data_provider: FritzBox, font: Font = Font()):
        FritzBoxWidget.__init__(self, parent, fritz_box_data_provider)
        TextWidget.__init__(self, parent, "DSL Status", font)
        self.update(None)

    def update(self, data: Optional[FritzBoxData]):
        with self._data_mutex:
            if data:
                if not data.is_linked:
                    self.text = "Not Linked"
                    self.foreground = Color.RED
                elif not data.is_connected:
                    self.text = "Connecting"
                    self.foreground = Color.YELLOW
                else:
                    self.text = "Connected"
                    self.foreground = self.parent.foreground
            else:
                self.text = "Unknown"
                self.foreground = Color.GRAY50


class FritzBoxSpeedWidget(FritzBoxWidget, TextWidget):
    def __init__(self, parent: ContainerWidget, fritz_box_data_provider: FritzBox, font: Font = Font()):
        FritzBoxWidget.__init__(self, parent, fritz_box_data_provider)
        TextWidget.__init__(self, parent, '🠕 20Mb 🠗 100Mb', font)
        self.update(None)

    def update(self, data: Optional[FritzBoxData]):
        with self._data_mutex:
            if data:
                up = f'{round(data.max_bit_rate[0] / 1000000)}Mb'
                down = f'{round(data.max_bit_rate[1] / 1000000)}Mb'
                self.text = f'🠕 {up} 🠗 {down}'
                self.foreground = self.parent.foreground
            else:
                self.text = "🠕 Unknown 🠗"
                self.foreground = Color.GRAY50


class FritzBoxIp4Widget(FritzBoxWidget, TextWidget):
    def __init__(self, parent: ContainerWidget, fritz_box_data_provider: FritzBox, font: Font = Font()):
        FritzBoxWidget.__init__(self, parent, fritz_box_data_provider)
        TextWidget.__init__(self, parent, '000.000.000.000', font)
        self.update(None)

    def update(self, data: Optional[FritzBoxData]):
        with self._data_mutex:
            if data and data.external_ip:
                self.text = data.external_ip
                self.foreground = self.parent.foreground
            else:
                self.text = '0.0.0.0'
                self.foreground = Color.GRAY50


class FritzBoxIp6Widget(FritzBoxWidget, TextWidget):
    def __init__(self, parent: ContainerWidget, fritz_box_data_provider: FritzBox, font: Font = Font()):
        FritzBoxWidget.__init__(self, parent, fritz_box_data_provider)
        TextWidget.__init__(self, parent, '000:000:000:000:000:000:000:000', font)
        self.update(None)

    def update(self, data: Optional[FritzBoxData]):
        with self._data_mutex:
            if data and data.external_ipv6:
                self.text = data.external_ipv6
                self.foreground = self.parent.foreground
            else:
                self.text = '::0'
                self.foreground = Color.GRAY50


class FritzBoxHostsWidget(FritzBoxWidget, TextWidget):
    def __init__(self, parent: ContainerWidget, fritz_box_data_provider: FritzBox, font: Font = Font()):
        FritzBoxWidget.__init__(self, parent, fritz_box_data_provider)
        TextWidget.__init__(self, parent, '0/00', font)
        self.update(None)

    def update(self, data: Optional[FritzBoxData]):
        with self._data_mutex:
            if data:
                self.text = f'{data.lan_hosts} LAN, {data.wifi_hosts} WLAN'
                self.foreground = self.parent.foreground
            else:
                self.text = '? LAN, ? WLAN'
                self.foreground = Color.GRAY50


class FritzBoxTrafficWidget(FritzBoxWidget, TextWidget):
    def __init__(self, parent: ContainerWidget, fritz_box_data_provider: FritzBox, font: Font = Font()):
        FritzBoxWidget.__init__(self, parent, fritz_box_data_provider)
        TextWidget.__init__(self, parent, '🠕 00Mb 🠗 00Mb', font)
        self.update(None)

    def update(self, data: Optional[FritzBoxData]):
        with self._data_mutex:
            if data and data.transmission_rate:
                up = humanize.naturalsize(data.transmission_rate[0],
                                          binary=True, gnu=True, format='%.0f')
                down = humanize.naturalsize(data.transmission_rate[1],
                                            binary=True, gnu=True, format='%.0f')
                self.text = f'🠕 {up} 🠗 {down}'
                self.foreground = self.parent.foreground
            else:
                self.text = "🠕 Unknown 🠗"
                self.foreground = Color.GRAY50


class FritzBoxTrafficGraphWidget(FritzBoxWidget):
    @dataclass
    class Measurement:
        time: datetime
        up: int
        down: int

        def __getitem__(self, key: int) -> int:
            if key == 0:
                return self.up
            if key == 1:
                return self.down
            raise IndexError('Index must be 0 for UP or 1 for DOWN.')

    def __init__(self, parent: ContainerWidget, fritz_box_data_provider: FritzBox,
                 time_span: timedelta = timedelta(minutes=1)):
        self._measurements: deque[FritzBoxTrafficGraphWidget.Measurement] = deque()
        self._measurements_mutex = Lock()
        self._time_span = time_span
        self._max = (0., 0.)
        self._bar_width = 20
        self._last_time: datetime = datetime(1, 1, 1)
        self._last_up = -1
        self._last_down = -1
        FritzBoxWidget.__init__(self, parent, fritz_box_data_provider)

    def update(self, data: Optional[FritzBoxData]):
        with self._data_mutex:
            if data:
                now = datetime.now()
                if self._last_up and self._last_up >= 0:
                    time_diff = (now - self._last_time).total_seconds()
                    up = int((data.bytes_sent - self._last_up) / time_diff * 8)
                    down = int((data.bytes_received - self._last_down) / time_diff * 8)
                    # noinspection PyCallByClass
                    with self._measurements_mutex:
                        self._measurements.append(
                            FritzBoxTrafficGraphWidget.Measurement(now, up, down))
                        while self._measurements and self._measurements[-1].time < now - self._time_span:
                            self._measurements.popleft()
                    self._max = data.max_bit_rate

                self._last_time = now
                self._last_up = data.bytes_sent
                self._last_down = data.bytes_received

    def paint_foreground(self, ctx: Context):
        with self._data_mutex:
            if self._measurements and self._max:
                sx = (self.width - self._bar_width) / self._time_span.total_seconds()
                sy = (self.height / self._max[0], self.height / self._max[1])
                colors = (Color.GREEN, Color.RED)
                current = self._measurements[-1]

                for i in (1, 0):
                    current_y = current[i] * sy[i]
                    ctx.set_source_rgba(*colors[i])
                    ctx.rectangle(self.width - self._bar_width, self.height - current_y,
                                  self._bar_width / (2 - i), current_y)
                    ctx.fill()

                    first = True
                    with self._measurements_mutex:
                        for m in self._measurements:
                            m_x = (self.width - self._bar_width) - (current.time - m.time).total_seconds() * sx
                            m_y = self.height - m[i] * sy[i]
                            if first:
                                ctx.move_to(m_x, m_y)
                                first = False
                            else:
                                ctx.line_to(m_x, m_y)

                    ctx.set_source_rgba(*colors[i])
                    ctx.stroke()
