from typing import Optional

from cairocffi import Context, ImageSurface

from clear19.widgets import load_svg
from clear19.widgets.widget import Widget, ContainerWidget


class ImageWidget(Widget):
    _image: Optional[ImageSurface] = None

    def __init__(self, parent: ContainerWidget):
        super().__init__(parent)

    def load_svg(self, svg_data: Optional[bytes]):
        if svg_data:
            self._image = load_svg(svg_data, *self.size)
        else:
            self._image = None
        self.dirty = True

    def paint_foreground(self, ctx: Context):
        if self._image:
            ctx.set_source_surface(self._image)
            ctx.paint()
        else:
            ctx.move_to(0, 0)
            ctx.line_to(self.size.width, self.size.height)
            ctx.stroke()
            ctx.move_to(0, self.size.height)
            ctx.line_to(self.size.width, 0)
            ctx.stroke()
