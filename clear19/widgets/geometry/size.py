from __future__ import annotations
from typing import Tuple

from dataclasses import dataclass


@dataclass(frozen=True)
class Size:
    width: float
    height: float

    @property
    def tuple(self) -> Tuple[float, float]:
        return self.width, self.height

    def fits_into(self, other: Size) -> bool:
        return self.width <= other.width and self.height <= other.height


ZERO: Size = Size(0, 0)
