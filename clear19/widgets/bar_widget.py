from enum import Enum
from typing import List, Tuple, Optional

from cairocffi import Context

from clear19.widgets import draw_rounded_rectangle, Rectangle
from clear19.widgets.color import Color
from clear19.widgets.geometry import ZERO_TOP_LEFT
from clear19.widgets.widget import Widget, ContainerWidget


class BarWidget(Widget):
    """
    Shows a bar, like a progress bar.
    """
    ValueType = Tuple[float, Optional[Color]]
    ValuesType = List[ValueType]

    class Orientation(Enum):
        HORIZONTAL_LEFT_TO_RIGHT = 1
        HORIZONTAL_RIGHT_TO_LEFT = 2
        VERTICAL_UP = 3
        VERTICAL_DOWN = 4

    _values: ValuesType
    _orientation: Orientation
    _border: Optional[Color]
    _border_width: float
    _border_corner: float
    _total: float = 0

    def __init__(self, parent: ContainerWidget, orientation: Orientation, values: ValuesType = None,
                 border: Optional[Color] = None, border_width: float = 1, border_corner: float = 5):
        super().__init__(parent)
        self._orientation = orientation
        self._values = values
        self._border = border
        self._border_width = border_width
        self._border_corner = border_corner

    def paint_foreground(self, ctx: Context):
        if self.border_corner:
            draw_rounded_rectangle(ctx, Rectangle(ZERO_TOP_LEFT, self.size), self.border_corner)
            ctx.clip()

        self.paint_scale_background(ctx)

        if self.values:
            pos = 0.0
            for value in self.values:
                l_pos = pos
                pos += value[0] / self._total
                if value[1]:
                    ctx.set_source_rgba(*value[1])
                    if self.orientation == BarWidget.Orientation.HORIZONTAL_LEFT_TO_RIGHT:
                        ctx.rectangle(l_pos * self.width, 0, (pos - l_pos) * self.width, self.height)
                    elif self.orientation == BarWidget.Orientation.HORIZONTAL_RIGHT_TO_LEFT:
                        ctx.rectangle(self.width - l_pos * self.width, 0, self.width - (l_pos - pos) * self.width,
                                      self.height)
                    elif self.orientation == BarWidget.Orientation.VERTICAL_DOWN:
                        ctx.rectangle(0, l_pos * self.height, self.width, (pos - l_pos) * self.height)
                    elif self.orientation == BarWidget.Orientation.VERTICAL_UP:
                        ctx.rectangle(0, self.height - l_pos * self.height, self.width, (l_pos - pos) * self.height)
                    ctx.fill()

        self.paint_scale_foreground(ctx)

        if self.border:
            ctx.set_source_rgba(*self.border)
            ctx.set_line_width(self.border_width)
            draw_rounded_rectangle(ctx, Rectangle(ZERO_TOP_LEFT, self.size), self.border_corner)
            ctx.stroke()

    def paint_scale_background(self, ctx: Context):
        pass

    def paint_scale_foreground(self, ctx: Context):
        pass

    @property
    def orientation(self) -> Orientation:
        return self._orientation

    @orientation.setter
    def orientation(self, orientation: Orientation):
        self._orientation = orientation
        self.dirty = True

    @property
    def values(self) -> ValuesType:
        return self._values

    @values.setter
    def values(self, values: ValuesType):
        total = 0
        for value in values:
            total += value[0]
        self._values = values
        self._total = total
        self.dirty = True

    @property
    def border(self) -> Optional[Color]:
        return self._border

    @border.setter
    def border(self, border: Optional[Color]):
        self._border = border
        self.dirty = True

    @property
    def border_width(self) -> float:
        return self._border_width

    @border_width.setter
    def border_width(self, border_width: float):
        self._border_width = border_width
        self.dirty = True

    @property
    def border_corner(self) -> float:
        return self._border_corner

    @border_corner.setter
    def border_corner(self, border_corner: float):
        self._border_corner = border_corner
        self.dirty = True
