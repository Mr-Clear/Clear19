from cairocffi import ImageSurface
from cairosvg.parser import Tree
from cairosvg.surface import PNGSurface


def load_svg(svg: bytes, width: float = None, height: float = None) -> ImageSurface:
    return PNGSurface(Tree(bytestring=svg), None, 1, parent_width=width, parent_height=height).cairo
