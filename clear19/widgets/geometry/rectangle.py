from clear19.widgets.geometry import anchored_point, size
from clear19.widgets.geometry.anchor import Anchor
from clear19.widgets.geometry.anchored_point import AnchoredPoint
from clear19.widgets.geometry.size import Size
from clear19.widgets.geometry.point import Point


class Rectangle:
    __top_left: Point
    __size: Size

    def __init__(self, point: AnchoredPoint, size: Size):
        self.__size = size
        if point.anchor == Anchor.TOP_LEFT:
            self.__top_left = Point(point.x, point.y)
        elif point.anchor == Anchor.TOP_CENTER:
            self.__top_left = Point(point.x - size.width / 2, point.y)
        elif point.anchor == Anchor.TOP_RIGHT:
            self.__top_left = Point(point.x - size.width, point.y)
        elif point.anchor == Anchor.CENTER_LEFT:
            self.__top_left = Point(point.x, point.y - size.height / 2)
        elif point.anchor == Anchor.CENTER_CENTER:
            self.__top_left = Point(point.x - size.width / 2, point.y - size.height / 2)
        elif point.anchor == Anchor.CENTER_RIGHT:
            self.__top_left = Point(point.x - size.width, point.y - size.height / 2)
        elif point.anchor == Anchor.BOTTOM_LEFT:
            self.__top_left = Point(point.x, point.y - size.height)
        elif point.anchor == Anchor.BOTTOM_CENTER:
            self.__top_left = Point(point.x - size.width / 2, point.y - size.height)
        elif point.anchor == Anchor.BOTTOM_RIGHT:
            self.__top_left = Point(point.x - size.width, point.y - size.height)

    @property
    def size(self) -> Size:
        return self.__size

    def position(self, anchor: Anchor) -> AnchoredPoint:
        if anchor == Anchor.TOP_LEFT:
            return AnchoredPoint(self.__top_left.x, self.__top_left.y, anchor)
        elif anchor == Anchor.TOP_CENTER:
            return AnchoredPoint(self.__top_left.x + self.__size.width / 2, self.__top_left.y, anchor)
        elif anchor == Anchor.TOP_RIGHT:
            return AnchoredPoint(self.__top_left.x + self.__size.width, self.__top_left.y, anchor)
        elif anchor == Anchor.CENTER_LEFT:
            return AnchoredPoint(self.__top_left.x, self.__top_left.y + self.__size.height / 2, anchor)
        elif anchor == Anchor.CENTER_CENTER:
            return AnchoredPoint(self.__top_left.x + self.__size.width / 2, self.__top_left.y + self.__size.height / 2,
                                 anchor)
        elif anchor == Anchor.CENTER_RIGHT:
            return AnchoredPoint(self.__top_left.x + self.__size.width, self.__top_left.y + self.__size.height / 2,
                                 anchor)
        elif anchor == Anchor.BOTTOM_LEFT:
            return AnchoredPoint(self.__top_left.x, self.__top_left.y + self.__size.height, anchor)
        elif anchor == Anchor.BOTTOM_CENTER:
            return AnchoredPoint(self.__top_left.x + self.__size.width / 2, self.__top_left.y + self.__size.height,
                                 anchor)
        elif anchor == Anchor.BOTTOM_RIGHT:
            return AnchoredPoint(self.__top_left.x + self.__size.width, self.__top_left.y + self.__size.height, anchor)


ZERO: Rectangle = Rectangle(anchored_point.ZERO, size.ZERO)
