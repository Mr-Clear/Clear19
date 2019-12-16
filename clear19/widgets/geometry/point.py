from typing import Tuple


class Point:
    _x: float
    _y: float

    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def tuple(self) -> Tuple[float, float]:
        return self.x, self.y


ZERO: Point = Point(0, 0)
