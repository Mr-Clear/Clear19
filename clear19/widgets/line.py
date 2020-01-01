from __future__ import annotations
from enum import Enum

from cairo import Context

from clear19.widgets.geometry import Anchor
from clear19.widgets.geometry import Size
from clear19.widgets.widget import Widget, ContainerWidget


class Line(Widget):
    class Orientation(Enum):
        HORIZONTAL = 1
        VERTICAL = 2

    _orientation: Orientation
    _line_width: float
    _margin: float

    def __init__(self, parent: ContainerWidget, orientation: Orientation, line_width: float = 1.5,
                 margin: float = 0.75):
        super().__init__(parent)
        self._orientation = orientation
        self._line_width = line_width
        self._margin = margin

    def paint_foreground(self, ctx: Context):
        ctx.set_line_width(self.line_width)
        if self.orientation == Line.Orientation.HORIZONTAL:
            ctx.move_to(*self.size.position(Anchor.CENTER_LEFT))
            ctx.line_to(*self.size.position(Anchor.CENTER_RIGHT))
        else:
            ctx.move_to(*self.size.position(Anchor.TOP_CENTER))
            ctx.line_to(*self.size.position(Anchor.BOTTOM_CENTER))
        ctx.stroke()

    def preferred_size(self) -> Size:
        if self.orientation == Line.Orientation.HORIZONTAL:
            return Size(self.width, self.margin * 2 + self.width)
        return Size(self.margin * 2 + self.width, self.height)

    @property
    def orientation(self) -> Orientation:
        return self._orientation

    @orientation.setter
    def orientation(self, orientation: Orientation):
        self._orientation = orientation
        self.repaint()

    @property
    def line_width(self) -> float:
        return self._line_width

    @line_width.setter
    def line_width(self, line_width: float):
        self._line_width = line_width
        self.repaint()

    @property
    def margin(self) -> float:
        return self._margin

    @margin.setter
    def margin(self, margin: float):
        self._margin = margin
        self.repaint()
