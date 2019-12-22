from __future__ import annotations

import dataclasses

import cairo
from dataclasses import dataclass
from cairo import Context, ImageSurface

from clear19.widgets.geometry.size import Size
from clear19.widgets.widget import Widget, ContainerWidget


@dataclass()
class Font:
    name: str = "Noto Sans Display"
    size: float = 16
    bold: bool = False
    italic: bool = False

    def fit_size(self, space: Size, text: str, ctx: Context = None) -> Font:
        return dataclasses.replace(self, size=Font.__narrow(self, space, text, 0, 10000, ctx))

    @staticmethod
    def __narrow(font: Font, space: Size, text: str, low: float, high: float, ctx) -> float:
        mid: float = (low + high) / 2.0

        copy: Font = dataclasses.replace(font, size=mid)

        fit = copy.extents(text, ctx).fits_into(space)

        if high - low < 0.0001:
            if fit:
                return mid
            else:
                return 0

        if fit:
            x = copy.__narrow(font, space, text, mid, high, ctx)
            if x:
                return x
            else:
                return mid
        else:
            return copy.__narrow(font, space, text, low, mid, ctx)

    def set(self, ctx: Context):
        ctx.select_font_face(self.name,
                             cairo.FONT_SLANT_ITALIC if self.italic else cairo.FONT_SLANT_NORMAL,
                             cairo.FONT_WEIGHT_BOLD if self.bold else cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(self.size)

    def extents(self, text: str, ctx: Context = None) -> Size:
        if ctx is None:
            ctx = Context(ImageSurface(cairo.FORMAT_RGB16_565, int(1), int(1)))
        self.set(ctx)
        font_ascent, font_descent, font_height, font_max_x_advance, font_max_y_advance = ctx.font_extents()
        max_width: float = 0
        max_height: float = 0
        y: float = font_ascent
        for line in text.split('\n'):
            _, _, text_width, _, _, _ = ctx.text_extents(line)
            if text_width > max_width:
                max_width = text_width
            max_height = y
            y += font_ascent
        max_height += font_descent
        return Size(max_width, max_height)


class TextWidget(Widget):
    __text: str
    __font: Font

    def __init__(self, parent: ContainerWidget, text: str = "", font: Font = Font()):
        super().__init__(parent)
        self.__text = text
        self.__font = font

    def paint_foreground(self, ctx: Context):
        self.font.set(ctx)
        font_ascent, font_descent, font_height, font_max_x_advance, font_max_y_advance = ctx.font_extents()
        y: float = font_ascent
        for line in self.text.split('\n'):
            ctx.move_to(0, y)
            ctx.show_text(line)
            y += font_ascent

    @property
    def text(self) -> str:
        return self.__text

    @text.setter
    def text(self, text: str):
        if self.__text != text:
            self.__text = text
            self.dirty = True

    @property
    def font(self) -> Font:
        return self.__font

    @font.setter
    def font(self, font: Font):
        self.__font = font
        self.dirty = True

    def fit_font_size(self, text: str = None):
        if text is None:
            text = self.text
        self.font = self.font.fit_size(self.size, text)
