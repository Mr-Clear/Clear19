from __future__ import annotations

import cairo
from cairo import Context

from clear19.widgets.widget import Widget, ContainerWidget


class Font:
    name: str
    size: float
    bold: bool
    italic: bool

    def __init__(self, name: str = "DejaVu Sans Mono", size: float = 16, bold: bool = False, italic: bool = False):
        self.name = name
        self.size = size
        self.bold = bold
        self.italic = italic


class TextWidget(Widget):
    __text: str
    __font: Font

    def __init__(self, parent: ContainerWidget, text: str = "", font: Font = Font()):
        super().__init__(parent)
        self.__text = text
        self.__font = font

    def paint_foreground(self, ctx: Context):
        ctx.select_font_face(self.font.name,
                             cairo.FONT_SLANT_ITALIC if self.font.italic else cairo.FONT_SLANT_NORMAL,
                             cairo.FONT_WEIGHT_BOLD if self.font.bold else cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(self.font.size)
        ctx.move_to(0, self.__font.size)
        ctx.show_text(self.text)

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
