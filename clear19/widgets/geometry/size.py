from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class Size:
    width: float
    height: float

    def fits_into(self, other: Size) -> bool:
        return self.width <= other.width and self.height <= other.height

    def __truediv__(self, divisor: float) -> Size:
        return Size(self.width / divisor, self.height / divisor)

    def __iter__(self) -> Iterator[float]:
        return iter((self.width, self.height))


ZERO: Size = Size(0, 0)
