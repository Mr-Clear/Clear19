from __future__ import annotations

from enum import Enum
from typing import Tuple

from cairocffi import ImageSurface
from cairosvg.parser import Tree
from cairosvg.surface import PNGSurface


def load_svg(svg: bytes, width: float = None, height: float = None) -> ImageSurface:
    return PNGSurface(Tree(bytestring=svg), None, 1, parent_width=width, parent_height=height).cairo


def _clip(v: float, v_min: float = 0, v_max: float = 1) -> float:
    if v < v_min:
        return v_min
    elif v > v_max:
        return v_max
    else:
        return v


class Color(Tuple[float, float, float], Enum):
    BLACK: Color = (0, 0, 0)
    WHITE: Color = (1, 1, 1)
    RED: Color = (1, 0, 0)
    GREEN: Color = (0, 1, 0)
    BLUE: Color = (0, 0, 1)
    YELLOW: Color = (1, 1, 0)
    MAGENTA: Color = (1, 0, 1)
    CYAN: Color = (0, 1, 1)
    GRAY0: Color = BLACK
    GRAY10: Color = (0.1, 0.1, 0.1)
    GRAY20: Color = (0.2, 0.2, 0.2)
    GRAY25: Color = (0.25, 0.25, 0.25)
    GRAY30: Color = (0.3, 0.3, 0.3)
    GRAY33: Color = (1 / 3, 1 / 3, 1 / 3)
    GRAY40: Color = (0.4, 0.4, 0.4)
    GRAY50: Color = (0.5, 0.5, 0.5)
    GRAY60: Color = (0.6, 0.6, 0.6)
    GRAY67: Color = (2 / 3, 2 / 3, 2 / 3)
    GRAY70: Color = (0.7, 0.7, 0.7)
    GRAY75: Color = (0.75, 0.75, 0.75)
    GRAY80: Color = (0.8, 0.8, 0.8)
    GRAY90: Color = (0.9, 0.9, 0.9)
    GRAY100: Color = WHITE

    def __truediv__(self, divisor: float) -> Color:
        return Color((_clip(self[0] / divisor), _clip(self[1] / divisor), _clip(self[2] / divisor)))

    def __mul__(self, factor) -> Color:
        return Color((_clip(self[0] * factor), _clip(self[1] * factor), _clip(self[2] * factor)))
