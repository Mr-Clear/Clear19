import logging
import math

import cairo
import gi
from cairo import ImageSurface

from clear19.widgets.geometry import Size

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository.Gtk import ApplicationWindow, Button, DrawingArea

log = logging.getLogger(__name__)


# noinspection PyMethodMayBeStatic
class G19Simulator:
    # noinspection PyTypeChecker
    def __init__(self, app):
        self.app = app
        self.image_size = Size(320, 240)
        self.image = ImageSurface(cairo.FORMAT_RGB16_565, self.image_size.height, self.image_size.width)
        builder = Gtk.Builder()
        builder.add_from_file("clear19/logitech/g19_simulator.glade")
        self.window: ApplicationWindow = builder.get_object("window")
        self.display: DrawingArea = builder.get_object("display")
        self.btn_up: Button = builder.get_object("btn_up")
        self.btn_down: Button = builder.get_object("btn_down")
        self.btn_left: Button = builder.get_object("btn_left")
        self.btn_right: Button = builder.get_object("btn_right")
        self.btn_ok: Button = builder.get_object("btn_ok")
        self.btn_menu: Button = builder.get_object("btn_menu")
        self.btn_back: Button = builder.get_object("btn_back")
        self.btn_settings: Button = builder.get_object("btn_settings")

        self.window.connect("destroy", self.app.exit)
        self.display.set_size_request(*self.image_size)
        self.display.connect("draw", self.on_draw)
        self.window.show_all()

    def on_draw(self, _area, context):
        if self.image:
            context.rotate(-math.pi / 2)
            context.scale(-1, 1)
            context.set_source_surface(self.image, 0, 00)
            context.paint()

    def reset(self):
        log.info("Reset")

    def send_frame(self, data):
        self.image = ImageSurface.create_for_data(data, cairo.FORMAT_RGB16_565,
                                                  round(self.image_size.height), round(self.image_size.width))
        self.display.queue_draw()
        pass

    def read_g_and_m_keys(self, _=None):
        return []

    def read_display_menu_keys(self):
        return []