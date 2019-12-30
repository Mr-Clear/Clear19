from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

from clear19.logitech.g19 import G19Key, DisplayKey
from clear19.widgets.geometry.anchor import Anchor
from clear19.widgets.geometry.point import AnchoredPoint
from clear19.widgets.geometry.rectangle import Rectangle
from clear19.widgets.text_widget import Font, TextWidget
from clear19.widgets.widget import ContainerWidget


@dataclass()
class MenuWidgetEntry:
    text: str
    on_click: Callable[[MenuWidgetEntry], None]
    widget: TextWidget = None


class MenuWidget(ContainerWidget):
    _menu: List[MenuWidgetEntry]
    _font: Font
    _current_entry: int
    _widget: TextWidget = None

    def __init__(self, parent: ContainerWidget, menu: List[MenuWidgetEntry], font: Font, current_entry: int = 0):
        super().__init__(parent)
        self._menu = menu
        self._font = font
        self._current_entry = current_entry
        self.build_menu()

    def build_menu(self):
        self.children.clear()
        y = 0
        for i in range(len(self.menu)):
            entry = self.menu[i]
            a = TextWidget(self, entry.text, self.font)
            a.rectangle = Rectangle(AnchoredPoint(0, y, Anchor.TOP_LEFT), a.preferred_size)
            if i == self.current_entry:
                a.foreground = self.background
                a.background = self.foreground
            entry.widget = a
            self.children.append(a)

    @property
    def menu(self) -> List[MenuWidgetEntry]:
        return self._menu

    @menu.setter
    def menu(self, menu: List[MenuWidgetEntry]):
        self._menu = menu

    @property
    def font(self) -> Font:
        return self._font

    @font.setter
    def font(self, font: Font):
        self._font = font

    @property
    def current_entry(self) -> int:
        return self._current_entry

    @current_entry.setter
    def current_entry(self, current_entry: int):
        self._current_entry = current_entry

    def on_key_down(self, key: G19Key) -> bool:
        entry = self.menu[self.current_entry]
        if key == DisplayKey.OK:
            entry.on_click(entry)
            return True
        return False
