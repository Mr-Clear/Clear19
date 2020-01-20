from __future__ import annotations

from typing import Dict, Optional

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


class Color:
    BLACK: Color
    WHITE: Color
    RED: Color
    GREEN: Color
    BLUE: Color
    YELLOW: Color
    MAGENTA: Color
    CYAN: Color
    GRAY0: Color
    GRAY10: Color
    GRAY20: Color
    GRAY25: Color
    GRAY30: Color
    GRAY33: Color
    GRAY40: Color
    GRAY50: Color
    GRAY60: Color
    GRAY67: Color
    GRAY70: Color
    GRAY75: Color
    GRAY80: Color
    GRAY90: Color
    GRAY100: Color

    _red: float
    _green: float
    _blue: float

    def __init__(self, red: float, green: float, blue: float):
        self._red = red
        self._green = green
        self._blue = blue

    @property
    def red(self) -> float:
        return self._red

    @property
    def green(self) -> float:
        return self._green

    @property
    def blue(self) -> float:
        return self._blue

    @property
    def red_255(self) -> int:
        return int(self.red * 255)

    @property
    def green_255(self) -> int:
        return int(self.green * 255)

    @property
    def blue_255(self) -> int:
        return int(self.blue * 255)

    def to_hex(self) -> str:
        return '#{:02x}{:02x}{:02x}'.format(self.red_255, self.green_255, self.blue_255)

    def __truediv__(self, divisor: float) -> Color:
        return Color(_clip(self.red / divisor), _clip(self.green / divisor), _clip(self.blue / divisor))

    def __mul__(self, factor) -> Color:
        return Color(_clip(self.red * factor), _clip(self.green * factor), _clip(self.blue * factor))

    def __iter__(self):
        return (self.red, self.green, self.blue).__iter__()

    @staticmethod
    def interpolate(value: float, gradient: Dict[float, Color]) -> Optional[Color]:
        if not gradient:
            return None
        s = sorted(gradient)
        if value < s[0]:
            return gradient[s[0]]
        for i in range(1, len(s)):
            key = s[i]
            if value == key:
                return gradient[value]
            if value < key:
                if i == len(s):
                    return gradient[s[i]]
                lo_val = s[i - 1]
                lo_col = gradient[lo_val]
                hi_val = s[i]
                hi_col = gradient[hi_val]
                quot_hi = (value - lo_val) / (hi_val - lo_val)
                quot_lo = 1 - quot_hi
                return Color(lo_col.red * quot_lo + hi_col.red * quot_hi,
                             lo_col.green * quot_lo + hi_col.green * quot_hi,
                             lo_col.blue * quot_lo + hi_col.blue * quot_hi)
        return gradient[s[-1]]


Color.BLACK = Color(0, 0, 0)
Color.WHITE = Color(1, 1, 1)
Color.RED = Color(1, 0, 0)
Color.GREEN = Color(0, 1, 0)
Color.BLUE = Color(0, 0, 1)
Color.YELLOW = Color(1, 1, 0)
Color.MAGENTA = Color(1, 0, 1)
Color.CYAN = Color(0, 1, 1)
Color.GRAY0 = Color.BLACK
Color.GRAY10 = Color(0.1, 0.1, 0.1)
Color.GRAY20 = Color(0.2, 0.2, 0.2)
Color.GRAY25 = Color(0.25, 0.25, 0.25)
Color.GRAY30 = Color(0.3, 0.3, 0.3)
Color.GRAY33 = Color(1 / 3, 1 / 3, 1 / 3)
Color.GRAY40 = Color(0.4, 0.4, 0.4)
Color.GRAY50 = Color(0.5, 0.5, 0.5)
Color.GRAY60 = Color(0.6, 0.6, 0.6)
Color.GRAY67 = Color(2 / 3, 2 / 3, 2 / 3)
Color.GRAY70 = Color(0.7, 0.7, 0.7)
Color.GRAY75 = Color(0.75, 0.75, 0.75)
Color.GRAY80 = Color(0.8, 0.8, 0.8)
Color.GRAY90 = Color(0.9, 0.9, 0.9)
Color.GRAY100 = Color.WHITE
