from __future__ import annotations

import dataclasses
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from xml.sax.saxutils import escape

import cairocffi as cairo
import pangocairocffi as pangocairo
from cairocffi import Context, ImageSurface
from pangocffi import Layout, Alignment

from clear19.data import Config
from clear19.scheduler import TaskParameters
from clear19.widgets.color import Color
from clear19.widgets.geometry import Size
from clear19.widgets.widget import Widget, ContainerWidget


log = logging.getLogger(__name__)


@dataclass()
class Font:
    @dataclass()
    class Extents:
        ascent: float
        descent: float
        height: float
        top: float

    class Style(Enum):
        NORMAL = 0
        OBLIQUE = 1
        ITALIC = 2

    class Weight(Enum):
        ULTRALIGHT = 0
        LIGHT = 1
        NORMAL = 2
        BOLD = 3
        ULTRABOLD = 4
        HEAVY = 5

    class Variant(Enum):
        NORMAL = 0
        SMALL_CAPS = 1
        ALL_SMALL_CAPS = 2
        PETITE_CAPS = 3
        ALL_PETITE_CAPS = 4
        UNICASE = 5
        TITLE_CAPS = 6

    name: str = 'Noto Sans Display'
    size: float = 16
    bold: bool = False
    style: Style = Style.NORMAL
    weight: Weight = Weight.NORMAL
    variant: Variant = Variant.TITLE_CAPS
    line_spacing: Optional[float] = None
    word_wrap: bool = False

    def fit_size(self, space: Size, text: str, ctx: Context = None) -> Font:
        s = Size(space.width, space.height)
        return dataclasses.replace(self, size=Font._narrow(self, s, text, 0, 10000, ctx))

    @staticmethod
    def _narrow(font: Font, space: Size, text: str, low: float, high: float, ctx) -> float:
        mid: float = (low + high) / 2.0

        copy: Font = dataclasses.replace(font, size=mid)
        extents = copy.text_extents(text, ctx)
        fit = extents.fits_into(space)

        if high - low < 1:
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

    def text_extents(self, text: str, inked: bool = True, ctx: Optional[Context] = None, width: Optional[int] = None) -> Size:
        """
        :param text: Arbitrary text
        :param inked: If true, only the extent of the inked area is returned.
        :param ctx: If None, a dummy context will be created.
        :param width: If set, word wrap will be used
        :return: Extents of the given text.
        """
        layout = self.get_layout(text, ctx)
        if width:
            layout.width = int(width * 1000)
        extents = layout.get_extents()[0 if inked else 1]
        return Size(extents.width / 1000, extents.height / 1000)

    def font_extents(self, inked: bool = True, ctx: Optional[Context] = None) -> Font.Extents:
        """
        :param inked: If true, only the extent of the inked area is returned.
        :param ctx: If None, a dummy context will be created.
        :return: Basic extents of this font which will are independent of the text.
        """
        layout = self.get_layout('Mg', ctx)
        extents = layout.get_extents()
        baseline = layout.get_baseline()
        if inked:
            return self.Extents(baseline / 1000 - extents[0].y, (extents[0].height - baseline) / 1000,
                                extents[0].height / 1000, extents[0].y / 1000)
        else:
            return self.Extents(baseline / 1000, (extents[1].height - baseline) / 1000, extents[1].height / 1000, 0)

    def get_layout(self, text: str, ctx: Optional[Context] = None, color: Color = Color.WHITE, escape_text=True)\
            -> Layout:
        """
        :param text: Text to layout.
        :param ctx: If None, a dummy context will be created.
        :param color: Color of the text.
        :param escape_text: If True, control characters will be macerated.
        :return: A pango layout object that can be rendered on the screen.
        """
        if ctx is None:
            ctx = Context(ImageSurface(cairo.FORMAT_RGB16_565, 1, 1))
        layout = pangocairo.create_layout(ctx)
        attributes = {'font_family': self.name,
                      'size': str(round(self.size * 1000)),
                      'foreground': color.to_hex()}
        if self.style != Font.Style.NORMAL:
            attributes['style'] = self.style.name.lower()
        if self.weight != Font.Weight.NORMAL:
            attributes['weight'] = self.weight.name.lower()
        if self.variant != Font.Variant.NORMAL:
            attributes['variant'] = self.variant.name.lower().replace('_', '-')
        if self.line_spacing:
            attributes['line_height'] = str(self.size * 1000)
        if not self.word_wrap:
            attributes['allow_breaks'] = 'false'
        attributes_string = ' '.join(map(lambda a: f'{a[0]}="{escape(a[1])}"', attributes.items()))
        layout.apply_markup(f'<span {attributes_string}>{escape(text) if escape_text else text}</span>')
        return layout


"""
Widget to show text.
"""
class TextWidget(Widget):
    """
    A widget that renders a text.
    """
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
                 h_alignment: TextWidget.HAlignment = HAlignment.LEFT,
                 v_alignment: TextWidget.VAlignment = VAlignment.TOP,
                 escape: bool = True):
        super().__init__(parent)
        self._text = text
        self._font = font
        self._h_alignment = h_alignment
        self._v_alignment = v_alignment
        self._escape = escape

    def paint_foreground(self, ctx: Context):
        layout = self.font.get_layout(self.text, ctx, self.foreground, self.escape)
        layout.line_spacing = 100
        layout.width = round(self.width * 1000)
        if self.h_alignment == TextWidget.HAlignment.LEFT:
            layout.alignment = Alignment.LEFT
        elif self.h_alignment == TextWidget.HAlignment.CENTER:
            layout.alignment = Alignment.CENTER
        elif self.h_alignment == TextWidget.HAlignment.RIGHT:
            layout.alignment = Alignment.RIGHT

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
        assert isinstance(text, str)
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
        """
        Changes the font size so that the given text fits into this widget.
        :param text: If none, the current text is used.
        """
        if text is None:
            text = self.text
        self.font = self.font.fit_size(self.size, text)

    @property
    def h_alignment(self) -> TextWidget.HAlignment:
        return self._h_alignment

    @h_alignment.setter
    def h_alignment(self, h_alignment: TextWidget.HAlignment):
        self._h_alignment = h_alignment
        self.dirty = True

    @property
    def v_alignment(self) -> TextWidget.VAlignment:
        return self._v_alignment

    @v_alignment.setter
    def v_alignment(self, v_alignment: TextWidget.VAlignment):
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
        """
        :return: The size of the current text with the current font.
        """
        return self.font.text_extents(self.text, width=int(self.width))

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(rectangle={self.rectangle}, background={self.background}, " \
               f"foreground={self.foreground}, text={self.text}, font={self.font}"


class TimeWidget(TextWidget):
    """
    Shows the current date/time and updates automatically.
    """
    _time_format: str
    _extents_datetime: datetime = datetime(2000, 12, 25, 22, 22, 22)  # Monday may be the longest day string

    def __init__(self, parent: ContainerWidget, time_format: str = Config.DateTime.date_time_format(),
                 font: Font = Font(),
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
