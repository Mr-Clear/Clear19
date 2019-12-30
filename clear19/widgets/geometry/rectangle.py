from clear19.widgets.geometry import size
from clear19.widgets.geometry.anchor import Anchor
from clear19.widgets.geometry.point import AnchoredPoint, ZERO_TOP_LEFT
from clear19.widgets.geometry.point import Point
from clear19.widgets.geometry.size import Size


class Rectangle:
    _top_left: Point
    _size: Size

    def __init__(self, point: AnchoredPoint, size: Size):
        self._size = size
        if point.anchor == Anchor.TOP_LEFT:
            self._top_left = Point(point.x, point.y)
        elif point.anchor == Anchor.TOP_CENTER:
            self._top_left = Point(point.x - size.width / 2, point.y)
        elif point.anchor == Anchor.TOP_RIGHT:
            self._top_left = Point(point.x - size.width, point.y)
        elif point.anchor == Anchor.CENTER_LEFT:
            self._top_left = Point(point.x, point.y - size.height / 2)
        elif point.anchor == Anchor.CENTER_CENTER:
            self._top_left = Point(point.x - size.width / 2, point.y - size.height / 2)
        elif point.anchor == Anchor.CENTER_RIGHT:
            self._top_left = Point(point.x - size.width, point.y - size.height / 2)
        elif point.anchor == Anchor.BOTTOM_LEFT:
            self._top_left = Point(point.x, point.y - size.height)
        elif point.anchor == Anchor.BOTTOM_CENTER:
            self._top_left = Point(point.x - size.width / 2, point.y - size.height)
        elif point.anchor == Anchor.BOTTOM_RIGHT:
            self._top_left = Point(point.x - size.width, point.y - size.height)

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

    def __str__(self) -> str:
        return "Rectangle(Top-Left={}, Size={})".format(self.position(Anchor.TOP_LEFT), self.size)


ZERO: Rectangle = Rectangle(ZERO_TOP_LEFT, size.ZERO)
