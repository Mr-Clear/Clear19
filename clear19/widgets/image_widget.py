import logging
from typing import Optional

from cairocffi import Context, ImageSurface, pixbuf

from clear19.widgets import load_svg
from clear19.widgets.widget import Widget, ContainerWidget


class ImageWidget(Widget):
    _image: Optional[ImageSurface] = None

    def __init__(self, parent: ContainerWidget):
        super().__init__(parent)

    def load_image(self, image_data: Optional[bytes]):
        if image_data:
            try:
                self._image = pixbuf.decode_to_image_surface(image_data)[0]
            except pixbuf.ImageLoadingError as e:
                logging.error("Error while loading image: {}".format(e))
                self._image = None
        else:
            self._image = None
        self.dirty = True

    def load_svg(self, svg_data: Optional[bytes]):
        if svg_data:
            self._image = load_svg(svg_data, *self.size)
        else:
            self._image = None
        self.dirty = True

    def paint_foreground(self, ctx: Context):
        if self._image:
            sx = self.width / self._image.get_width()
            sy = self.height / self._image.get_height()
            s = min(sx, sy)
            sw = self._image.get_width() * s
            sh = self._image.get_height() * s
            ctx.scale(s, s)
            s2 = s * 2
            ctx.set_source_surface(self._image, (self.width - sw) / s2, (self.height - sh) / s2)
            ctx.paint()
        else:
            ctx.move_to(0, 0)
            ctx.line_to(self.size.width, self.size.height)
            ctx.stroke()
            ctx.move_to(0, self.size.height)
            ctx.line_to(self.size.width, 0)
            ctx.stroke()
