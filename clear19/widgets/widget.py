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
    __background: Color
    __foreground: Color

    def __init__(self, parent: ContainerWidget):
        self.__rectangle = rectangle.ZERO
        self.__dirty = True
        self.__background = color.BLACK
        self. __foreground = color.WHITE
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

    @property
    def size(self) -> Size:
        return self.rectangle.size

    @property
    def background(self) -> Color:
        return self.__background

    @background.setter
    def background(self, background: Color):
        self.__background = background
        self.dirty = True

    @property
    def foreground(self) -> Color:
        return self.__foreground

    @foreground.setter
    def foreground(self, foreground: Color):
        self.__foreground = foreground
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

    def on_key_down(self, key: G19Key):
        pass

    def on_key_up(self, key: G19Key):
        pass


class AppWidget(ContainerWidget):
    __metaclass__ = abc.ABCMeta

    __current_screen: Optional[Screen]
    __scheduler: Scheduler

    def __init__(self, parent):
        self.__scheduler = Scheduler()
        self.__current_screen = None
        super().__init__(parent)

    def paint(self, ctx: Context):
        self.current_screen.paint(ctx)
        self.dirty = False

    @property
    def screen_size(self) -> Size:
        return size.ZERO

    @property
    def rectangle(self) -> Rectangle:
        return Rectangle(anchored_point.ZERO, self.screen_size)

    @property
    def current_screen(self) -> Optional[Screen]:
        return self.__current_screen

    @current_screen.setter
    def current_screen(self, current_screen: Screen):
        self.__current_screen = current_screen
        self.__current_screen.repaint()
        self.dirty = True
        logging.info("Screen changed to {}.".format(self.__current_screen.name))

    @abstractmethod
    def set_screen(self, screen: Enum):
        pass

    @property
    def scheduler(self) -> Scheduler:
        return self.__scheduler

    @property
    def app(self) -> AppWidget:
        return self

    @abstractmethod
    def screens(self) -> Type[Enum]:
        pass
