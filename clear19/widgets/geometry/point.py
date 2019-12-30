from __future__ import annotations

from builtins import abs
from dataclasses import dataclass
from typing import Iterator

from clear19.widgets.geometry.anchor import Anchor
from clear19.widgets.geometry.size import Size


@dataclass
class Point:
    x: float
    y: float

    def anchored(self, anchor: Anchor) -> AnchoredPoint:
        return AnchoredPoint(self.x, self.y, anchor)

    def __sub__(self, other: Point) -> Size:
        return Size(abs(self.x - other.x), abs(self.y - other.y))

    def __iter__(self) -> Iterator[float]:
        return iter((self.x, self.y))


class AnchoredPoint(Point):
    _anchor: Anchor

    def __init__(self, x: float, y: float, anchor: Anchor):
        super().__init__(x, y)
        self._anchor = anchor

    @property
    def anchor(self) -> Anchor:
        return self._anchor


ZERO: Point = Point(0, 0)
ZERO_TOP_LEFT: AnchoredPoint = AnchoredPoint(0, 0, Anchor.TOP_LEFT)
