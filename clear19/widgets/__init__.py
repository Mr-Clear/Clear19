from cairocffi import ImageSurface, Context
from cairosvg.parser import Tree
from cairosvg.surface import PNGSurface

from clear19.widgets.geometry import Rectangle, Anchor


def load_svg(svg: bytes, width: float = None, height: float = None) -> ImageSurface:
    return PNGSurface(Tree(bytestring=svg), None, 1, parent_width=width, parent_height=height).cairo


def _clip(v: float, v_min: float = 0, v_max: float = 1) -> float:
    if v < v_min:
        return v_min
    elif v > v_max:
        return v_max
    else:
        return v


def draw_rounded_rectangle(ctx: Context, rectangle: Rectangle, radius: float):
    """ draws rectangles with rounded (circular arc) corners """
    from math import pi
    a, c = rectangle.position(Anchor.TOP_LEFT)
    b, d = rectangle.position(Anchor.BOTTOM_RIGHT)
    ctx.arc(a + radius, c + radius, radius, 2 * (pi / 2), 3 * (pi / 2))
    ctx.arc(b - radius, c + radius, radius, 3 * (pi / 2), 4 * (pi / 2))
    ctx.arc(b - radius, d - radius, radius, 0 * (pi / 2), 1 * (pi / 2))  # ;o)
    ctx.arc(a + radius, d - radius, radius, 1 * (pi / 2), 2 * (pi / 2))
    ctx.close_path()
