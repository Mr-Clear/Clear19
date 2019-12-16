from typing import Tuple


class Size:
    _width: float
    _height: float

    def __init__(self, width: float, height: float):
        self._width = width
        self._height = height

    @property
    def width(self) -> float:
        return self._width

    @property
    def height(self) -> float:
        return self._height

    @property
    def tuple(self) -> Tuple[float, float]:
        return self.width, self.height


ZERO: Size = Size(0, 0)
