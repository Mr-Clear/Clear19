import logging
from typing import Optional

from cairocffi import Context, ImageSurface, pixbuf

from clear19.widgets import load_svg
from clear19.widgets.geometry import Anchor
from clear19.widgets.widget import Widget, ContainerWidget


class ImageWidget(Widget):
    _image: Optional[ImageSurface] = None
    _alignment: Anchor

    def __init__(self, parent: ContainerWidget, alignment: Anchor = Anchor.CENTER_CENTER):
        super().__init__(parent)
        self._alignment = alignment

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
            x = 0
            y = 0
            if self.alignment == Anchor.TOP_LEFT:
                x = 0
                y = 0
            elif self.alignment == Anchor.TOP_CENTER:
                x = (self.width - sw) / 2
                y = 0
            elif self.alignment == Anchor.TOP_RIGHT:
                x = self.width - sw
                y = 0
            elif self.alignment == Anchor.CENTER_LEFT:
                x = 0
                y = (self.height - sh) / 2
            elif self.alignment == Anchor.CENTER_CENTER:
                x = (self.width - sw) / 2
                y = (self.height - sh) / 2
            elif self.alignment == Anchor.CENTER_RIGHT:
                x = (self.width - sw)
                y = (self.height - sh) / 2
            elif self.alignment == Anchor.BOTTOM_LEFT:
                x = 0
                y = self.height - sh
            elif self.alignment == Anchor.BOTTOM_CENTER:
                x = (self.width - sw) / 2
                y = self.height - sh
            elif self.alignment == Anchor.BOTTOM_RIGHT:
                x = self.width - sw
                y = self.height - sh
            x /= s
            y /= s
            ctx.set_source_surface(self._image, x, y)
            ctx.paint()
        else:
            ctx.move_to(0, 0)
            ctx.line_to(self.size.width, self.size.height)
            ctx.stroke()
            ctx.move_to(0, self.size.height)
            ctx.line_to(self.size.width, 0)
            ctx.stroke()

    @property
    def alignment(self) -> Anchor:
        return self._alignment

    @alignment.setter
    def alignment(self, alignment: Anchor):
        self._alignment = alignment
        self.dirty = True
