from typing import Tuple


class Point:
    __x: float
    __y: float

    def __init__(self, x: float, y: float):
        self.__x = x
        self.__y = y

    @property
    def x(self) -> float:
        return self.__x

    @property
    def y(self) -> float:
        return self.__y

    @property
    def tuple(self) -> Tuple[float, float]:
        return self.x, self.y


ZERO: Point = Point(0, 0)
