from __future__ import annotations

import abc
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Type, Optional

from cairo import Context

from clear19.logitech.g19 import G19Key
from clear19.scheduler import Scheduler
from clear19.widgets import color
from clear19.widgets.color import Color
from clear19.widgets.geometry import rectangle, size, anchored_point
from clear19.widgets.geometry.anchor import Anchor
from clear19.widgets.geometry.anchored_point import AnchoredPoint
from clear19.widgets.geometry.rectangle import Rectangle
from clear19.widgets.geometry.size import Size


class Widget(ABC):
    __metaclass__ = abc.ABCMeta
    __parent: ContainerWidget
    __rectangle: Rectangle
    __dirty: bool
    _background: Color
    _foreground: Color

    def __init__(self, parent: ContainerWidget):
        self.__rectangle = rectangle.ZERO
        self.__dirty = True
        self._background = parent.background
        self. _foreground = parent.foreground
        self.__parent = parent

    @property
    def parent(self) -> ContainerWidget:
        return self.__parent

    @property
    def dirty(self) -> bool:
        return self.__dirty

    @dirty.setter
    def dirty(self, dirty: bool):
        if dirty != self.__dirty:
            self.__dirty = dirty
            if dirty and self.parent is not None:
                self.parent.dirty = True
        
    @property
    def rectangle(self) -> Rectangle:
        return self.__rectangle
    
    @rectangle.setter
    def rectangle(self, rectangle: Rectangle):
        self.__rectangle = rectangle

    def position(self, anchor: Anchor) -> AnchoredPoint:
        return self.__rectangle.position(anchor)

    def set_position(self, point: AnchoredPoint):
        self.rectangle = Rectangle(point, self.size)

    @property
    def size(self) -> Size:
        return self.rectangle.size

    def set_size(self, size: Size, anchor: Anchor):
        self.rectangle = Rectangle(self.rectangle.position(anchor), size)

    @property
    def background(self) -> Color:
        return self._background

    @background.setter
    def background(self, background: Color):
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
        ctx.set_source_rgb(*self.background)
        self.paint_background(ctx)
        ctx.set_source_rgb(*self.foreground)
        self.paint_foreground(ctx)
        self.dirty = False

    @abstractmethod
    def paint_foreground(self, ctx: Context):
        return

    def paint_background(self, ctx: Context):
        ctx.rectangle(0, 0, *self.size.tuple)
        ctx.fill()

    @property
    def app(self) -> AppWidget:
        return self.parent.app

    def repaint(self):
        self.dirty = True

    def preferred_size(self) -> Size:
        return self.size

    def on_key_down(self, key: G19Key) -> bool:
        return False

    def on_key_up(self, key: G19Key) -> bool:
        return False

    def __str__(self) -> str:
        return "{}(rectangle={}, background={}, foreground={})".format(self.__class__.__name__, self.rectangle,
                                                                       self.background, self.foreground)


class ContainerWidget(Widget):
    __metaclass__ = abc.ABCMeta
    __children: List[Widget]

    def __init__(self, parent: ContainerWidget):
        self.__children = []
        super().__init__(parent)
    
    @property
    def children(self) -> List[Widget]:
        return self.__children

    def paint_foreground(self, ctx: Context):
        self.paint_children(ctx)
        self.dirty = False

    def paint_children(self, ctx: Context):
        for child in self.children:
            ctx.save()
            ctx.translate(*child.position(Anchor.TOP_LEFT).tuple)
            ctx.rectangle(0, 0, *self.size.tuple)
            ctx.clip()
            child.paint(ctx)
            ctx.restore()

    def repaint(self):
        self.dirty = True
        for child in self.children:
            child.repaint()


class Screen(ContainerWidget):
    __metaclass__ = abc.ABCMeta
    __name: str

    def __init__(self, parent: AppWidget, name: str):
        super().__init__(parent)
        self.rectangle = parent.rectangle
        self.__name = name

    @property
    def name(self) -> str:
        return self.__name

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
    __metaclass__ = abc.ABCMeta

    __current_screen: Optional[Enum]
    __scheduler: Scheduler
    __last_screens: List[Enum]

    def __init__(self):
        self.__scheduler = Scheduler()
        self.__current_screen = None
        self.__last_screens = []
        self._background = color.BLACK
        self._foreground = color.WHITE
        super().__init__(self)

    def paint(self, ctx: Context):
        self._current_screen_object.paint(ctx)
        self.dirty = False

    @property
    def screen_size(self) -> Size:
        return size.ZERO

    @property
    def rectangle(self) -> Rectangle:
        return Rectangle(anchored_point.ZERO, self.screen_size)

    @property
    def current_screen(self) -> Optional[Enum]:
        return self.__current_screen

    @current_screen.setter
    def current_screen(self, current_screen: Enum):
        if self.__current_screen != current_screen:
            if self.__current_screen:
                if self.__last_screens and self.__last_screens[-1] == current_screen:
                    del self.__last_screens[-1]
                else:
                    self.__last_screens.append(self.current_screen)
            self.__current_screen = current_screen
            self.repaint()
            logging.info("Screen changed to {}.".format(self.__current_screen.name))

    @property
    def _current_screen_object(self) -> Screen:
        return self._screen_object(self.__current_screen)

    @abstractmethod
    def _screen_object(self, screen: Enum) -> Screen:
        pass

    def navigate_back(self):
        if self.__last_screens:
            self.app.current_screen = self.__last_screens[-1]

    @property
    def scheduler(self) -> Scheduler:
        return self.__scheduler

    @property
    def app(self) -> AppWidget:
        return self

    @abstractmethod
    def screens(self) -> Type[Enum]:
        pass

    @abstractmethod
    def exit(self, exit_code: int = 0):
        pass
