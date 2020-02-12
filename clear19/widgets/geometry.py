from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterator, Union

"""
Classes for widget geometry.
"""


class Anchor(Enum):
    """
    Position on a widgets border.
    """
    TOP_LEFT = 11
    TOP_CENTER = 12
    TOP_RIGHT = 13
    CENTER_LEFT = 21
    CENTER_CENTER = 22
    CENTER_RIGHT = 23
    BOTTOM_LEFT = 31
    BOTTOM_CENTER = 32
    BOTTOM_RIGHT = 33


class VAnchor(Enum):
    """
    Vertical position on a widget.
    """
    TOP = 1
    CENTER = 2
    BOTTOM = 3

    def __add__(self, h: HAnchor):
        return Anchor(self.value * 10 + h.value)


class HAnchor(Enum):
    """
    Horizontal position on a widget.
    """
    LEFT = 1
    Center = 2
    RIGHT = 3

    def __add__(self, v: VAnchor) -> Anchor:
        return Anchor(v.value * 10 + self.value)


@dataclass
class Point:
    """
    A 2D Point on the display.
    """
    x: float
    y: float

    def anchored(self, anchor: Anchor) -> AnchoredPoint:
        """
        :param anchor: Role of this Point on a widgets border.
        :return: An anchored version of this Point.
        """
        return AnchoredPoint(self.x, self.y, anchor)

    def __add__(self, other: Point) -> Point:
        """
        Vector-Like addition of points.
        :param other: Point to add.
        :return: New Point with added coordinates.
        """
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Point) -> Size:
        """
        Creates a Size between this Point and the Ohter Point.
        WARNING: This is not the inverse of the __add__ function!
        :param other: Other point.
        :return: Size between both points.
        """
        return Size(abs(self.x - other.x), abs(self.y - other.y))

    def __iter__(self) -> Iterator[float]:
        return iter((self.x, self.y))


class AnchoredPoint(Point):
    """
    Point with information on which position on an widgets border it is.
    """
    _anchor: Anchor

    def __init__(self, x: float, y: float, anchor: Anchor):
        super().__init__(x, y)
        self._anchor = anchor

    @property
    def anchor(self) -> Anchor:
        return self._anchor

    def __add__(self, other: Point) -> AnchoredPoint:
        return AnchoredPoint(self.x + other.x, self.y + other.y, self.anchor)


class Rectangle:
    """
    Combination of Point and Size which defined a rectangle.
    """
    _top_left: Point
    _size: Size

    def __init__(self, point: AnchoredPoint, size: Union[Size, Point]):
        """
        :param point: Point from which the rectangle is spanned.
        :param size: Size of the Rectangle.
        """
        if isinstance(size, Point):
            self._size = point - size
        else:
            self._size = size

        if point.anchor == Anchor.TOP_LEFT:
            self._top_left = Point(point.x, point.y)
        elif point.anchor == Anchor.TOP_CENTER:
            self._top_left = Point(point.x - self._size.width / 2, point.y)
        elif point.anchor == Anchor.TOP_RIGHT:
            self._top_left = Point(point.x - self._size.width, point.y)
        elif point.anchor == Anchor.CENTER_LEFT:
            self._top_left = Point(point.x, point.y - self._size.height / 2)
        elif point.anchor == Anchor.CENTER_CENTER:
            self._top_left = Point(point.x - self._size.width / 2, point.y - self._size.height / 2)
        elif point.anchor == Anchor.CENTER_RIGHT:
            self._top_left = Point(point.x - self._size.width, point.y - self._size.height / 2)
        elif point.anchor == Anchor.BOTTOM_LEFT:
            self._top_left = Point(point.x, point.y - self._size.height)
        elif point.anchor == Anchor.BOTTOM_CENTER:
            self._top_left = Point(point.x - self._size.width / 2, point.y - self._size.height)
        elif point.anchor == Anchor.BOTTOM_RIGHT:
            self._top_left = Point(point.x - self._size.width, point.y - self._size.height)

    @property
    def size(self) -> Size:
        return self._size

    def position(self, anchor: Anchor) -> AnchoredPoint:
        if anchor == Anchor.TOP_LEFT:
            return AnchoredPoint(self._top_left.x, self._top_left.y, anchor)
        elif anchor == Anchor.TOP_CENTER:
            return AnchoredPoint(self._top_left.x + self._size.width / 2, self._top_left.y, anchor)
        elif anchor == Anchor.TOP_RIGHT:
            return AnchoredPoint(self._top_left.x + self._size.width, self._top_left.y, anchor)
        elif anchor == Anchor.CENTER_LEFT:
            return AnchoredPoint(self._top_left.x, self._top_left.y + self._size.height / 2, anchor)
        elif anchor == Anchor.CENTER_CENTER:
            return AnchoredPoint(self._top_left.x + self._size.width / 2, self._top_left.y + self._size.height / 2,
                                 anchor)
        elif anchor == Anchor.CENTER_RIGHT:
            return AnchoredPoint(self._top_left.x + self._size.width, self._top_left.y + self._size.height / 2,
                                 anchor)
        elif anchor == Anchor.BOTTOM_LEFT:
            return AnchoredPoint(self._top_left.x, self._top_left.y + self._size.height, anchor)
        elif anchor == Anchor.BOTTOM_CENTER:
            return AnchoredPoint(self._top_left.x + self._size.width / 2, self._top_left.y + self._size.height,
                                 anchor)
        elif anchor == Anchor.BOTTOM_RIGHT:
            return AnchoredPoint(self._top_left.x + self._size.width, self._top_left.y + self._size.height, anchor)

    @property
    def left(self) -> float:
        return self._top_left.x

    @property
    def right(self) -> float:
        return self._top_left.x + self.size.width

    @property
    def top(self) -> float:
        return self._top_left.y

    @property
    def bottom(self) -> float:
        return self._top_left.y + self.size.height

    @property
    def width(self) -> float:
        return self._size.width

    @property
    def height(self) -> float:
        return self._size.height

    def __str__(self) -> str:
        return f"Rectangle(Top-Left={self.position(Anchor.TOP_LEFT)}, Size={self.size})"


@dataclass(frozen=True)
class Size:
    """
    Size of a widget.
    """
    width: float
    height: float

    def fits_into(self, other: Size) -> bool:
        """
        :param other:
        :return: True, if this Size is smaller then the other size in all dimensions.
        """
        return self.width <= other.width and self.height <= other.height

    def position(self, anchor: Anchor) -> AnchoredPoint:
        return Rectangle(ZERO_TOP_LEFT, self).position(anchor)

    def __add__(self, other: Size) -> Size:
        return Size(self.width + other.width, self.height + other.height)

    def __sub__(self, other: Size) -> Size:
        return Size(self.width - other.width, self.height - other.height)

    def __truediv__(self, divisor: float) -> Size:
        return Size(self.width / divisor, self.height / divisor)

    def __iter__(self) -> Iterator[float]:
        return iter((self.width, self.height))


ZERO_POINT: Point = Point(0, 0)
ZERO_TOP_LEFT: AnchoredPoint = AnchoredPoint(0, 0, Anchor.TOP_LEFT)
ZERO_SIZE: Size = Size(0, 0)
ZERO_RECT: Rectangle = Rectangle(ZERO_TOP_LEFT, ZERO_SIZE)
