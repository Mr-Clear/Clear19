from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

import cairo
from cairo import Context, ImageSurface

from clear19.scheduler import TaskParameters
from clear19.widgets.geometry.size import Size
from clear19.widgets.widget import Widget, ContainerWidget


@dataclass()
class Font:
    name: str = "Noto Sans Display"
    size: float = 16
    bold: bool = False
    italic: bool = False

    def fit_size(self, space: Size, text: str, ctx: Context = None) -> Font:
        s = Size(space.width - 1, space.height)
        return dataclasses.replace(self, size=Font._narrow(self, s, text, 0, 10000, ctx))

    @staticmethod
    def _narrow(font: Font, space: Size, text: str, low: float, high: float, ctx) -> float:
        mid: float = (low + high) / 2.0

        copy: Font = dataclasses.replace(font, size=mid)

        fit = copy.extents(text, ctx).fits_into(space)

        if high - low < 0.0001:
            if fit:
                return mid
            else:
                return 0

        if fit:
            x = copy._narrow(font, space, text, mid, high, ctx)
            if x:
                return x
            else:
                return mid
        else:
            return copy._narrow(font, space, text, low, mid, ctx)

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
        x_bearing: float = 0
        y: float = font_ascent
        for line in text.split('\n'):
            x_bearing, y_bearing, text_width, height, x_advance, y_advance = ctx.text_extents(line)
            if text_width > max_width:
                max_width = text_width
            max_height = y
            y += font_ascent
        max_height += font_descent
        return Size(max_width + x_bearing, max_height)


class TextWidget(Widget):
    class HAlignment(Enum):
        LEFT = 0
        CENTER = 1
        RIGHT = 2

    class VAlignment(Enum):
        TOP = 0
        CENTER = 1
        BOTTOM = 2

    _text: str
    _font: Font
    _h_alignment: HAlignment
    _v_alignment: VAlignment

    def __init__(self, parent: ContainerWidget, text: str = "", font: Font = Font(),
                 h_alignment: HAlignment = HAlignment.LEFT, v_alignment: VAlignment = VAlignment.TOP):
        super().__init__(parent)
        self._text = text
        self._font = font
        self._h_alignment = h_alignment
        self._v_alignment = v_alignment

    def paint_foreground(self, ctx: Context):
        self.font.set(ctx)
        font_ascent, font_descent, font_height, font_max_x_advance, font_max_y_advance = ctx.font_extents()
        lines = self.text.split('\n')
        text_height = len(lines) * font_ascent + font_descent
        if self.v_alignment == TextWidget.VAlignment.TOP:
            y = 0
        elif self.v_alignment == TextWidget.VAlignment.CENTER:
            y = self.size.height / 2 - text_height / 2
        elif self.v_alignment == TextWidget.VAlignment.BOTTOM:
            y = self.size.height - text_height
        else:
            raise Exception("Unknown v alignment: {}".format(self.v_alignment))
        for line in lines:
            y += font_ascent
            line_size = self.font.extents(line, ctx)
            if self.h_alignment == TextWidget.HAlignment.LEFT:
                x = 0
            elif self.h_alignment == TextWidget.HAlignment.CENTER:
                x = self.size.width / 2 - line_size.width / 2
            elif self.h_alignment == TextWidget.HAlignment.RIGHT:
                x = self.size.width - line_size.width
            else:
                raise Exception("Unknown v alignment: {}".format(self.v_alignment))
            ctx.move_to(x, y)
            ctx.show_text(line)

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str):
        if self._text != text:
            self._text = text
            self.dirty = True

    @property
    def font(self) -> Font:
        return self._font

    @font.setter
    def font(self, font: Font):
        self._font = font
        self.dirty = True

    def fit_font_size(self, text: str = None):
        if text is None:
            text = self.text
        self.font = self.font.fit_size(self.size, text)

    @property
    def h_alignment(self) -> HAlignment:
        return self._h_alignment

    @h_alignment.setter
    def h_alignment(self, h_alignment: HAlignment):
        self._h_alignment = h_alignment
        self.dirty = True

    @property
    def v_alignment(self) -> VAlignment:
        return self._v_alignment

    @v_alignment.setter
    def v_alignment(self, v_alignment: VAlignment):
        self._v_alignment = v_alignment
        self.dirty = True

    @property
    def preferred_size(self) -> Size:
        return self.font.extents(self.text)

    def __str__(self) -> str:
        return "{}(rectangle={}, background={}, foreground={}, text={}, font={}" \
            .format(self.__class__.__name__, self.rectangle, self.background, self.foreground, self.text, self.font)


class TimeWidget(TextWidget):
    _time_format: str
    _extents_datetime: datetime = datetime(2000, 12, 25, 22, 22, 22)  # Monday may be the longest day string

    def __init__(self, parent: ContainerWidget, time_format: str = "%H:%M:%S", font: Font = Font(),
                 h_alignment: TextWidget.HAlignment = TextWidget.HAlignment.LEFT,
                 v_alignment: TextWidget.VAlignment = TextWidget.VAlignment.TOP):
        super().__init__(parent, datetime.now().strftime(time_format), font,
                         h_alignment, v_alignment)
        self._time_format = time_format
        self.app.scheduler.schedule_synchronous(timedelta(seconds=1), self.update)

    @property
    def time_format(self) -> str:
        return self._time_format

    @time_format.setter
    def time_format(self, time_format: str):
        self._time_format = time_format
        self.update()

    def update(self, _: TaskParameters = None):
        self.text = datetime.now().strftime(self.time_format)

    @property
    def preferred_size(self) -> Size:
        return self.font.extents(self._extents_datetime.strftime(self.time_format))

    def fit_font_size(self, text: str = None):
        if text is None:
            text = self._extents_datetime.strftime(self.time_format)
        return super().fit_font_size(text)
