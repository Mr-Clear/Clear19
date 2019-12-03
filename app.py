#!/usr/bin/env python3

import logging
from logitech.g19 import G19
import time
import math
import cairo

from clear19.key_listener import DisplayKey, GKey, KeyListener

logging.basicConfig(format='%(asctime)s [%(levelname)-8s] %(message)s', level=logging.DEBUG, force=True)
logging.info("START")

try:
    import usb
except ModuleNotFoundError:
    logging.critical("Failed to import usb. Use \"sudo pip install pyusb\" to install it.")
    exit(1)

try:
    import PIL.Image as Img
except ModuleNotFoundError:
    logging.critical("Failed to import PIL. Use \"sudo pip install Pillow\" to install it.")
    exit(1)

try:
    g19 = G19()
except usb.core.USBError as err:
    logging.fatal("Failed to open USB connection: {0}".format(err))
    exit(2)
kl = KeyListener(g19)

image_size = (320, 240)

img = cairo.ImageSurface(cairo.FORMAT_ARGB32, image_size[0], image_size[1])

speed = 2
x = 160
y = 120

try:
    start = time.time()
    while time.time() < start + 100:
        keys = kl.pressed_keys()
        if DisplayKey.UP in keys:
            y = y - speed
        if DisplayKey.DOWN in keys:
            y = y + speed
        if DisplayKey.LEFT in keys:
            x = x - speed
        if DisplayKey.RIGHT in keys:
            x = x + speed

        # http://seriot.ch/pycairo/

        ctx = cairo.Context(img)

        pat = cairo.LinearGradient(0.0, 0.0, 0.0, 240)
        pat.add_color_stop_rgba(1, 0.7, 0, 0, 0.5)  # First stop, 50% opacity
        pat.add_color_stop_rgba(0, 0.9, 0.7, 0.2, 1)  # Last stop, 100% opacity

        ctx.rectangle(0, 0, 320, 240)  # Rectangle(x0, y0, x1, y1)
        ctx.set_source(pat)
        ctx.fill()

        ctx.set_source_rgb(0, 0, 0)
        ctx.select_font_face("Consolas")
        ctx.set_font_size(28)
        ctx.move_to(250, 220)
        ctx.show_text("{:3.0f}".format(100 - time.time() + start))

        pat = cairo.RadialGradient(x - 10, y - 10, 5, x, y, 25)
        pat.add_color_stop_rgba(0, 1, 1, 1, 1)
        pat.add_color_stop_rgba(0.3, 0.5, 0.5, 1, 1)
        pat.add_color_stop_rgba(1, 0, 0, 1, 1)
        ctx.set_source(pat)
        ctx.arc(x, y, 25, 0, math.pi * 2)
        ctx.fill()

        ctx.set_source_rgb(0.3, 0.2, 0.5)  # Solid color
        ctx.set_line_width(1)
        ctx.stroke()

        g19.send_frame(g19.convert_surface_to_frame(img))
except KeyboardInterrupt:
    pass
finally:
    kl.stop()
    g19.reset()
    logging.info("END")
