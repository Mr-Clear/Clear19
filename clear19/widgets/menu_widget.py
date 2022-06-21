from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

from clear19.logitech.g19 import G19Key, DisplayKey
from clear19.widgets.geometry import Anchor, AnchoredPoint, Rectangle
from clear19.widgets.text_widget import Font, TextWidget
from clear19.widgets.widget import ContainerWidget

log = logging.getLogger(__name__)


@dataclass()
class MenuWidgetEntry:
    text: str
    on_click: Callable[[MenuWidgetEntry], None]
    widget: Optional[TextWidget] = None
    children: Optional[List[MenuWidgetEntry]] = None


class MenuWidget(ContainerWidget):
    """
    Widget that offers a menu for user selection.
    """
    _menu: List[MenuWidgetEntry]
    _font: Font
    _current_index: int
    _widget: Optional[TextWidget] = None
    _menu_stack: [List[Tuple[List[MenuWidgetEntry, int]]]] = []

    def __init__(self, parent: ContainerWidget, menu: List[MenuWidgetEntry], font: Font, current_index: int = 0):
        super().__init__(parent)
        self._menu = menu
        self._font = font
        self._current_index = current_index
        self.build_menu()

    def build_menu(self):
        self.children.clear()
        y = 0
        for i in range(len(self._menu)):
            entry = self._menu[i]
            a = TextWidget(self, entry.text, self.font)
            a.rectangle = Rectangle(AnchoredPoint(0, y, Anchor.TOP_LEFT), a.preferred_size)
            if i == self._current_index:
                a.foreground = self.background
                a.background = self.foreground
            entry.widget = a
            y += a.preferred_size.height

    def _update(self):
        self.build_menu()
        self.dirty = True

    def enter_submenu(self, menu: List[MenuWidgetEntry], index: int = 0):
        self._menu_stack.append((self._menu, self._current_index))
        self._menu = menu
        self._current_index = index
        self._update()

    def leave_submenu(self):
        self._menu, self._current_index = self._menu_stack.pop()
        self._update()

    @property
    def font(self) -> Font:
        return self._font

    @font.setter
    def font(self, font: Font):
        self._font = font

    def on_key_down(self, key: G19Key) -> bool:
        entry = self._menu[self._current_index]
        if key == DisplayKey.OK:
            log.info(f'Selected menu entry "{entry.text}"')
            entry.on_click(entry)
            return True
        if key == DisplayKey.DOWN:
            self._current_index += 1
            if self._current_index >= len(self._menu):
                self._current_index = 0
            self._update()
            return True
        if key == DisplayKey.UP:
            self._current_index -= 1
            if self._current_index < 0:
                self._current_index = len(self._menu) - 1
            self._update()
            return True
        if key == DisplayKey.BACK:
            if self._menu_stack:
                self.leave_submenu()
                return True
            else:
                return False
        return False
