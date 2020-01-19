from __future__ import annotations

import logging
from abc import ABC, abstractmethod, ABCMeta
from enum import Enum
from typing import List, Type, Optional

from cairocffi import Context

import clear19.widgets.geometry
from clear19.logitech.g19 import G19Key
from clear19.scheduler import Scheduler
from clear19.widgets import Color
from clear19.widgets.geometry import Anchor, VAnchor, HAnchor, AnchoredPoint, ZERO_TOP_LEFT, Rectangle, Size


class Widget(ABC):
    __metaclass__ = ABCMeta
    _parent: ContainerWidget
    _rectangle: Rectangle = clear19.widgets.geometry.ZERO_RECT
    _dirty: bool = True
    _background: Optional[Color]
    _foreground: Color

    def __init__(self, parent: ContainerWidget):
        self._background = parent.background
        self._foreground = parent.foreground
        self._parent = parent

    @property
    def parent(self) -> ContainerWidget:
        return self._parent

    @property
    def dirty(self) -> bool:
        return self._dirty

    @dirty.setter
    def dirty(self, dirty: bool):
        if dirty != self._dirty:
            self._dirty = dirty
            if dirty and self.parent is not None:
                self.parent.dirty = True

    @property
    def rectangle(self) -> Rectangle:
        return self._rectangle

    @rectangle.setter
    def rectangle(self, rectangle: Rectangle):
        self._rectangle = rectangle

    def position(self, anchor: Anchor) -> AnchoredPoint:
        return self._rectangle.position(anchor)

    def set_position(self, point: AnchoredPoint):
        self.rectangle = Rectangle(point, self.size)

    @property
    def size(self) -> Size:
        return self.rectangle.size

    def set_size(self, size: Size, anchor: Anchor):
        self.rectangle = Rectangle(self.rectangle.position(anchor), size)

    @property
    def background(self) -> Optional[Color]:
        return self._background

    @background.setter
    def background(self, background: Optional[Color]):
        self._background = background
        self.dirty = True

    @property
    def foreground(self) -> Color:
        return self._foreground

    @foreground.setter
    def foreground(self, foreground: Color):
        self._foreground = foreground
        self.dirty = True

    def paint(self, ctx: Context):
        if self.background:
            ctx.set_source_rgb(*self.background)
            self.paint_background(ctx)
        ctx.set_source_rgb(*self.foreground)
        self.paint_foreground(ctx)
        self.dirty = False

    @abstractmethod
    def paint_foreground(self, ctx: Context):
        return

    def paint_background(self, ctx: Context):
        ctx.rectangle(0, 0, *self.size)
        ctx.fill()

    @property
    def app(self) -> AppWidget:
        return self.parent.app

    def repaint(self):
        self.dirty = True

    @property
    def preferred_size(self) -> Size:
        return self.size

    def on_key_down(self, key: G19Key) -> bool:
        return False

    def on_key_up(self, key: G19Key) -> bool:
        return False

    @property
    def left(self) -> float:
        return self._rectangle.left

    @property
    def right(self) -> float:
        return self._rectangle.right

    @property
    def top(self) -> float:
        return self._rectangle.top

    @property
    def bottom(self) -> float:
        return self._rectangle.bottom

    @property
    def width(self) -> float:
        return self._rectangle.width

    def set_width(self, width: float, anchor: HAnchor):
        self.rectangle = Rectangle(self.position(VAnchor.TOP + anchor), Size(width, self.width))

    @property
    def height(self) -> float:
        return self._rectangle.height

    def set_height(self, height: float, anchor: VAnchor):
        self.rectangle = Rectangle(self.position(anchor + HAnchor.LEFT), Size(self.width, height))
        self.dirty = True

    def __str__(self) -> str:
        return "{}(rectangle={}, background={}, foreground={})".format(self.__class__.__name__, self.rectangle,
                                                                       self.background, self.foreground)


class ContainerWidget(Widget):
    __metaclass__ = ABCMeta
    _children: List[Widget]

    def __init__(self, parent: ContainerWidget):
        self._children = []
        super().__init__(parent)

    def do_layout(self):
        pass

    @property
    def children(self) -> List[Widget]:
        return self._children

    @property
    def rectangle(self) -> Rectangle:
        return self._rectangle

    @rectangle.setter
    def rectangle(self, rectangle: Rectangle):
        self._rectangle = rectangle
        self.do_layout()

    def paint_foreground(self, ctx: Context):
        self.paint_children(ctx)
        self.dirty = False

    def paint_children(self, ctx: Context):
        for child in self.children:
            ctx.save()
            ctx.translate(*child.position(Anchor.TOP_LEFT))
            ctx.rectangle(0, 0, *child.size)
            ctx.clip()
            child.paint(ctx)
            ctx.restore()

    def repaint(self):
        self.dirty = True
        for child in self.children:
            child.repaint()


class Screen(ContainerWidget):
    __metaclass__ = ABCMeta
    _name: str

    def __init__(self, parent: AppWidget, name: str):
        super().__init__(parent)
        self.rectangle = parent.rectangle
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def on_key_down(self, key: G19Key) -> bool:
        for child in self.children:
            if child.on_key_down(key):
                return True
        return False

    def on_key_up(self, key: G19Key) -> bool:
        for child in self.children:
            if child.on_key_up(key):
                return True
        return False


class AppWidget(ContainerWidget):
    __metaclass__ = ABCMeta

    _current_screen: Optional[Enum] = None
    _scheduler: Scheduler
    _last_screens: List[Enum]

    def __init__(self):
        self._scheduler = Scheduler()
        self._last_screens = []
        self._background = Color.BLACK
        self._foreground = Color.WHITE
        super().__init__(self)

    def paint(self, ctx: Context):
        self._current_screen_object.paint(ctx)
        self.dirty = False

    @property
    def screen_size(self) -> Size:
        return clear19.widgets.geometry.ZERO_SIZE

    @property
    def rectangle(self) -> Rectangle:
        return Rectangle(ZERO_TOP_LEFT, self.screen_size)

    @property
    def current_screen(self) -> Optional[Enum]:
        return self._current_screen

    @current_screen.setter
    def current_screen(self, current_screen: Enum):
        if self._current_screen != current_screen:
            if self._current_screen:
                if self._last_screens and self._last_screens[-1] == current_screen:
                    del self._last_screens[-1]
                else:
                    self._last_screens.append(self.current_screen)
            self._current_screen = current_screen
            self.repaint()
            logging.info("Screen changed to {}.".format(self._current_screen.name))

    @property
    def _current_screen_object(self) -> Screen:
        return self._screen_object(self._current_screen)

    @abstractmethod
    def _screen_object(self, screen: Enum) -> Screen:
        pass

    def navigate_back(self):
        if self._last_screens:
            self.app.current_screen = self._last_screens[-1]

    @property
    def scheduler(self) -> Scheduler:
        return self._scheduler

    @property
    def app(self) -> AppWidget:
        return self

    @abstractmethod
    def screens(self) -> Type[Enum]:
        pass

    @abstractmethod
    def exit(self, exit_code: int = 0):
        pass
