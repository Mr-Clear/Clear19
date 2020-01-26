from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from xml.sax.saxutils import escape, quoteattr

import cairocffi as cairo
import pangocairocffi as pangocairo
from cairocffi import Context, ImageSurface
from pangocffi import Layout, Alignment

from clear19.scheduler import TaskParameters
from clear19.widgets.color import Color
from clear19.widgets.geometry import Size
from clear19.widgets.widget import Widget, ContainerWidget


@dataclass()
class Font:
    @dataclass()
    class Extents:
        ascent: float
        descent: float
        height: float
        top: float

    name: str = 'Noto Sans Display'
    size: float = 16
    bold: bool = False
    italic: bool = False

    def fit_size(self, space: Size, text: str, ctx: Context = None) -> Font:
        s = Size(space.width, space.height)
        return dataclasses.replace(self, size=Font._narrow(self, s, text, 0, 10000, ctx))

    @staticmethod
    def _narrow(font: Font, space: Size, text: str, low: float, high: float, ctx) -> float:
        mid: float = (low + high) / 2.0

        copy: Font = dataclasses.replace(font, size=mid)

        fit = copy.text_extents(text, ctx).fits_into(space)

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

    def text_extents(self, text: str, inked: bool = True, ctx: Context = None) -> Size:
        layout = self.get_layout(text, ctx)
        extents = layout.get_extents()[0 if inked else 1]
        return Size(extents.width / 1000, extents.height / 1000)

    def font_extents(self, inked: bool = True, ctx: Context = None) -> Font.Extents:
        layout = self.get_layout('Mg', ctx)
        extents = layout.get_extents()
        baseline = layout.get_baseline()
        if inked:
            return self.Extents(baseline / 1000 - extents[0].y, (extents[0].height - baseline) / 1000,
                                extents[0].height / 1000, extents[0].y / 1000)
        else:
            return self.Extents(baseline / 1000, (extents[1].height - baseline) / 1000, extents[1].height / 1000, 0)

    def get_layout(self, text: str, ctx: Context = None, color: Color = Color.WHITE, escape_text=True) -> Layout:
        if ctx is None:
            ctx = Context(ImageSurface(cairo.FORMAT_RGB16_565, int(1), int(1)))
        layout = pangocairo.create_layout(ctx)
        layout.set_markup('<span font_family={} size={} foreground={} style={} weight={}>{}</span>'
                          .format(quoteattr(self.name),
                                  quoteattr(str(int(self.size * 1000))),
                                  quoteattr(color.to_hex()),
                                  '"italic"' if self.italic else '"normal"',
                                  '"bold"' if self.bold else '"normal"',
                                  escape(text) if escape_text else text))
        return layout


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
    _escape: bool

    def __init__(self, parent: ContainerWidget, text: str = "", font: Font = Font(),
                 h_alignment: HAlignment = HAlignment.LEFT, v_alignment: VAlignment = VAlignment.TOP,
                 escape: bool = True):
        super().__init__(parent)
        self._text = text
        self._font = font
        self._h_alignment = h_alignment
        self._v_alignment = v_alignment
        self._escape = escape

    def paint_foreground(self, ctx: Context):
        layout = self.font.get_layout(self.text, ctx, self.foreground, self.escape)
        if self.h_alignment == TextWidget.HAlignment.LEFT:
            layout.set_alignment(Alignment.LEFT)
        else:
            layout.set_width(int(self.width * 1000))
            if self.h_alignment == TextWidget.HAlignment.CENTER:
                layout.set_alignment(Alignment.CENTER)
            elif self.h_alignment == TextWidget.HAlignment.RIGHT:
                layout.set_alignment(Alignment.RIGHT)

        y = -layout.get_extents()[0].y / 1000
        if self.v_alignment == TextWidget.VAlignment.BOTTOM:
            y += self.height - layout.get_extents()[0].height / 1000
        elif self.v_alignment == TextWidget.VAlignment.CENTER:
            y += (self.height - layout.get_extents()[0].height / 1000) / 2

        ctx.move_to(0, y)
        pangocairo.show_layout(ctx, layout)

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
        if self._font != font:
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
    def escape(self) -> bool:
        return self._escape

    @escape.setter
    def escape(self, escape: bool):
        self._escape = escape

    @property
    def preferred_size(self) -> Size:
        return self.font.text_extents(self.text)

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
        return self.font.text_extents(self._extents_datetime.strftime(self.time_format))

    def fit_font_size(self, text: str = None):
        if text is None:
            text = self._extents_datetime.strftime(self.time_format)
        return super().fit_font_size(text)
