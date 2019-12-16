from clear19.widgets.geometry.anchor import Anchor
from clear19.widgets.geometry.point import Point


class AnchoredPoint(Point):
    __anchor: Anchor

    def __init__(self, x: float, y: float, anchor: Anchor):
        super().__init__(x, y)
        self.__anchor = anchor

    @property
    def anchor(self) -> Anchor:
        return self.__anchor


ZERO: AnchoredPoint = AnchoredPoint(0, 0, Anchor.TOP_LEFT)
