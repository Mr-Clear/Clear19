from dataclasses import dataclass
from typing import Tuple


@dataclass
class Point:
    x: float
    y: float

    @property
    def tuple(self) -> Tuple[float, float]:
        return self.x, self.y


ZERO: Point = Point(0, 0)
