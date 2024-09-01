from __future__ import annotations

import logging
from abc import ABC, abstractmethod, ABCMeta
from enum import Enum
from typing import List, Type, Optional

from cairocffi import Context

import clear19.widgets.geometry
from clear19.logitech.g19 import G19Key
from clear19.scheduler import Scheduler
from clear19.widgets.color import Color
from clear19.widgets.geometry import Anchor, VAnchor, HAnchor, AnchoredPoint, ZERO_TOP_LEFT, Rectangle, Size

log = logging.getLogger(__name__)


class Widget(ABC):
    """ Base class for all widgets. """
    __metaclass__ = ABCMeta
    _parent: ContainerWidget
    _rectangle: Rectangle = clear19.widgets.geometry.ZERO_RECT
    _dirty: bool = True
    _background: Optional[Color]
    _foreground: Color

    def __init__(self, parent: ContainerWidget):
        """
        :param parent: The container which holds this widget.
        """
        self._background = parent.background
        self._foreground = parent.foreground
        self._parent = parent
        if parent is not self:
            parent.children.append(self)

    @property
    def parent(self) -> ContainerWidget:
        return self._parent

    @property
    def dirty(self) -> bool:
        """
        :return: If true, this widget will be rendered soon.
        """
        return self._dirty

    @dirty.setter
    def dirty(self, dirty: bool):
        """ If set to True, the parent is also set to dirty. """
        if dirty != self._dirty:
            self._dirty = dirty
            if dirty and self.parent is not None:
                self.parent.dirty = True

    @property
    def rectangle(self) -> Rectangle:
        """
        :return: The position of this widget in it's parent coordinates.
        """
        return self._rectangle

    @rectangle.setter
    def rectangle(self, rectangle: Rectangle):
        self._rectangle = rectangle

    def position(self, anchor: Anchor) -> AnchoredPoint:
        """
        :return: The position of the specified point in the parent's coordinates.
        """
        return self._rectangle.position(anchor)

    def set_position(self, point: AnchoredPoint):
        """
        Moves this widget while retaining it's size.
        """
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
        """
        Renders this widget.
        :param ctx: Cairo context.
        """
        if self.background:
            ctx.set_source_rgba(*self.background)
            self.paint_background(ctx)
        ctx.set_source_rgba(*self.foreground)
        self.paint_foreground(ctx)
        self.dirty = False

    @abstractmethod
    def paint_foreground(self, ctx: Context):
        """
        Renders this widget. Is called by Widget.paint.
        """

    def paint_background(self, ctx: Context):
        """
        Renders the background of this widget. Is called by Widget.paint.
        """
        ctx.rectangle(0, 0, *self.size)
        ctx.fill()

    @property
    def app(self) -> AppWidget:
        """
        :return: The App object which is the root of the widget hierarchy.
        """
        return self.parent.app

    def repaint(self):
        """
        Sets the dirty flag.
        """
        self.dirty = True

    @property
    def preferred_size(self) -> Size:
        """
        :return: If overridden, the Size this widget should have to fit all it's content.
        """
        return self.size

    def on_key_down(self, key: G19Key) -> bool:
        """
        Receives key down events.
        :param key: The pressed key.
        :return: If True, the event will not be received by further widgets.
        """
        return False

    def on_key_up(self, key: G19Key) -> bool:
        """
        Receives key up events.
        :param key: The released key.
        :return: If True, the event will not be received by further widgets.
        """
        return False

    @property
    def left(self) -> float:
        """
        :return: Left edge of this widget in the parent's coordinates.
        """
        return self._rectangle.left

    @property
    def right(self) -> float:
        """
        :return: Right edge of this widget in the parent's coordinates.
        """
        return self._rectangle.right

    @property
    def top(self) -> float:
        """
        :return: Top edge of this widget in the parent's coordinates.
        """
        return self._rectangle.top

    @property
    def bottom(self) -> float:
        """
        :return: Bottom edge of this widget in the parent's coordinates.
        """
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
        return f"{self.__class__.__name__}(rectangle={self.rectangle}, background={self.background}, " \
               f"foreground={self.foreground})"


class ContainerWidget(Widget):
    """
    Widget that contains other widgets as children.
    """
    __metaclass__ = ABCMeta
    _children: List[Widget]

    def __init__(self, parent: ContainerWidget):
        self._children = []
        super().__init__(parent)

    def do_layout(self):
        """
        Called when the size of this ContainerWidget changes to rearrange children.
        """
        pass

    @property
    def children(self) -> List[Widget]:
        return self._children

    @Widget.rectangle.setter
    def rectangle(self, rectangle: Rectangle):
        # noinspection PyArgumentList
        Widget.rectangle.fset(self, rectangle)
        self.do_layout()

    def paint_foreground(self, ctx: Context):
        """
        Paints all the children.
        """
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
        """
        Sets the dirty flag of this ContainerWidget and all its direct and indirect children.
        """
        self.dirty = True
        for child in self.children:
            child.repaint()


class Screen(ContainerWidget):
    """
    A ContainerWidget which fills the whole screen.
    """
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
    """
    The root of the widget hierarchy. Shall only contain Screen widgets.
    """
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

    # noinspection PyMethodOverriding
    @property
    def rectangle(self) -> Rectangle:
        return Rectangle(ZERO_TOP_LEFT, self.screen_size)

    @property
    def current_screen(self) -> Optional[Enum]:
        """
        :return: The currently displayed screen.
        """
        return self._current_screen

    @current_screen.setter
    def current_screen(self, current_screen: Enum):
        """
        Sets the currently displayed screen.
        :param current_screen: Identifier for the screen.
        """
        if self._current_screen != current_screen:
            if self._current_screen:
                if self._last_screens and self._last_screens[-1] == current_screen:
                    del self._last_screens[-1]
                else:
                    self._last_screens.append(self.current_screen)
            self._current_screen = current_screen
            self.repaint()
            log.info(f"Screen changed to {self._current_screen.name}.")

    @property
    def _current_screen_object(self) -> Screen:
        return self._screen_object(self._current_screen)

    def navigate_back(self):
        """
        Change current screen to previous screen.
        """
        if self._last_screens:
            self.app.current_screen = self._last_screens[-1]

    @property
    def scheduler(self) -> Scheduler:
        return self._scheduler

    @property
    def app(self) -> AppWidget:
        return self

    @property
    def screen_size(self) -> Size:
        """
        Needs to be overridden by App implementation!
        :return: The size of the display.
        """
        return clear19.widgets.geometry.ZERO_SIZE

    @abstractmethod
    def screens(self) -> Type[Enum]:
        """
        :return: List of known screens.
        """
        pass

    @abstractmethod
    def _screen_object(self, screen: Enum) -> Screen:
        """
        :param screen: Value that identifies a screen.
        :return: Screen instance for the given screen Enum.
        """
        pass

    @abstractmethod
    def exit(self, exit_code: int = 0):
        """
        Closes the app.
        :param exit_code: Exit code given ro the parent process.
        """
        pass
