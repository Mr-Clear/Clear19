from cairocffi import ImageSurface, Context
from cairosvg.parser import Tree
from cairosvg.surface import PNGSurface

from clear19.widgets.geometry import Rectangle, Anchor

""" Widget framework """


def load_svg(svg: bytes, width: float = None, height: float = None) -> ImageSurface:
    """
    Load a SVG image to an Cairo ImageSurface.
    :param svg: Plain SVG data
    :param width: Designated with of the image. If None, it will be determined from the svg data.
    :param height:  Designated height of the image. If None, it will be determined from the svg data.
    :return: ImageSurface that contains the image from the SVG data.
    """
    return PNGSurface(Tree(bytestring=svg), None, 1, parent_width=width, parent_height=height).cairo


def draw_rounded_rectangle(ctx: Context, rectangle: Rectangle, radius: float):
    """
    Draw rectangles with rounded (circular arc) corners.
    :param ctx: Cairo render context.
    :param rectangle: Extent of the rectangle.
    :param radius: Radius of the corners.
    """
    from math import pi
    a, c = rectangle.position(Anchor.TOP_LEFT)
    b, d = rectangle.position(Anchor.BOTTOM_RIGHT)
    ctx.arc(a + radius, c + radius, radius, 2 * (pi / 2), 3 * (pi / 2))
    ctx.arc(b - radius, c + radius, radius, 3 * (pi / 2), 4 * (pi / 2))
    ctx.arc(b - radius, d - radius, radius, 0 * (pi / 2), 1 * (pi / 2))  # ;o)
    ctx.arc(a + radius, d - radius, radius, 1 * (pi / 2), 2 * (pi / 2))
    ctx.close_path()
