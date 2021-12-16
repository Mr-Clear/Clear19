from abc import ABC, ABCMeta, abstractmethod
from typing import Optional

import humanize

from clear19.data.fritzbox import FritzBox, FritzBoxData
from clear19.widgets.color import Color
from clear19.widgets.text_widget import TextWidget, Font
from clear19.widgets.widget import Widget, ContainerWidget


class FritzBoxWidget(Widget, ABC):
    """
    Base class for all media player widgets.
    """
    __metaclass__ = ABCMeta

    _fritz_box_data_provider: FritzBox

    def __init__(self, parent: ContainerWidget, fritz_box_data_provider: FritzBox):
        super().__init__(parent)
        self._fritz_box_data_provider = fritz_box_data_provider
        fritz_box_data_provider.add_listener(self.update)
        self.update(fritz_box_data_provider.current_data)

    @abstractmethod
    def update(self, data: FritzBoxData):
        pass

    @property
    def fritz_box_data_provider(self) -> FritzBox:
        return self._fritz_box_data_provider


class FritzBoxConnectedWidget(FritzBoxWidget, TextWidget):
    def __init__(self, parent: ContainerWidget, fritz_box_data_provider: FritzBox, font: Font = Font()):
        FritzBoxWidget.__init__(self, parent, fritz_box_data_provider)
        TextWidget.__init__(self, parent, "DSL Status", font)
        self.update(None)

    def update(self, data: Optional[FritzBoxData]):
        if data and data.status:
            if not data.status.is_linked:
                self.text = "Not Linked"
                self.foreground = Color.RED
            elif not data.status.is_connected:
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
        if data and data.status:
            up = f'{round(data.status.max_bit_rate[0] / 1000000)}Mb'
            down = f'{round(data.status.max_bit_rate[1] / 1000000)}Mb'
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
        if data and data.status:
            self.text = data.status.external_ip
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
        if data and data.status:
            self.text = data.status.external_ipv6
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
        if data and data.hosts and data.wlan:
            total = len(list(filter(lambda d: d['status'], data.hosts.get_hosts_info())))
            self.text = f'{total - data.wlan.total_host_number} LAN, {data.wlan.total_host_number} WLAN'
            self.foreground = self.parent.foreground
        else:
            self.text = '? LAN, ? WLAN'
            self.foreground = Color.GRAY50


class FritzBoxTrafficWidget(FritzBoxWidget, TextWidget):
    def __init__(self, parent: ContainerWidget, fritz_box_data_provider: FritzBox, font: Font = Font()):
        FritzBoxWidget.__init__(self, parent, fritz_box_data_provider)
        TextWidget.__init__(self, parent, '🠕 00Mb 🠗 00Mb', font)
        self.update(None)

    # noinspection PyUnresolvedReferences
    def update(self, data: Optional[FritzBoxData]):
        if data and data.hosts and data.wlan:
            up = humanize.naturalsize(data.status.transmission_rate[0],
                                      binary=True, gnu=True, format='%.0f')
            down = humanize.naturalsize(data.status.transmission_rate[1],
                                        binary=True, gnu=True, format='%.0f')
            self.text = f'🠕 {up} 🠗 {down}'
            self.foreground = self.parent.foreground
        else:
            self.text = "🠕 Unknown 🠗"
            self.foreground = Color.GRAY50
