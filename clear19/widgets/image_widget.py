import logging
from typing import Optional

from cairocffi import Context, ImageSurface, pixbuf

from clear19.widgets import load_svg
from clear19.widgets.color import Color
from clear19.widgets.geometry import Anchor
from clear19.widgets.widget import Widget, ContainerWidget

log = logging.getLogger(__name__)


class ImageWidget(Widget):
    """
    Displays an image.
    Supports all formats supported by pixbuf and SVG.
    """
    _image: Optional[ImageSurface] = None
    _alignment: Anchor

    def __init__(self, parent: ContainerWidget, alignment: Anchor = Anchor.CENTER_CENTER, overlay_color : Optional[Color] = None):
        super().__init__(parent)
        self._alignment = alignment
        self._overlay_color = overlay_color

    def load_image(self, image_data: Optional[bytes]):
        if image_data:
            try:
                self._image = pixbuf.decode_to_image_surface(image_data)[0]
            except pixbuf.ImageLoadingError as e:
                log.error(f"Error while loading image: {e}", exc_info=True)
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
            ctx.save()
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
            ctx.restore()
        else:
            ctx.set_source_rgba(*self.background)
            ctx.rectangle(0, 0, self.size.width, self.size.height)
            ctx.fill()

            ctx.set_source_rgba(*self.foreground)
            ctx.move_to(0, 0)
            ctx.line_to(self.size.width, self.size.height)
            ctx.stroke()
            ctx.move_to(0, self.size.height)
            ctx.line_to(self.size.width, 0)
            ctx.stroke()

        if self._overlay_color:
            ctx.set_source_rgba(*self._overlay_color)
            ctx.rectangle(0, 0, self.size.width, self.size.height)
            ctx.fill()

    @property
    def alignment(self) -> Anchor:
        """
        :return: Where to align the image within this widget when its doesn't fit exactly.
        """
        return self._alignment

    @alignment.setter
    def alignment(self, alignment: Anchor):
        self._alignment = alignment
        self.dirty = True
        
    @property
    def overlay_color(self) -> Color:
        return self._overlay_color
    
    @overlay_color.setter
    def overlay_color(self, overlay_color: Color):
        self._overlay_color = overlay_color
