#!/usr/bin/env python3

import logging
import math
import numpy
import time
from typing import Set

import cairo

from clear19.logitech.g19 import DisplayKey, G19, GKey, KeyLight
from clear19.logitech.key_listener import KeyListener

logging.basicConfig(format="%(asctime)s [%(levelname)-8s] %(message)s", level=logging.DEBUG, force=True)
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
    g19: G19 = G19()
except usb.core.USBError as err:
    logging.critical("Failed to open USB connection: {0}".format(err))
    exit(2)
# noinspection PyUnboundLocalVariable
kl = KeyListener(g19)

image_size = (320, 240)

img = cairo.ImageSurface(cairo.FORMAT_RGB16_565, image_size[1], image_size[0])

speed: int = 2
x: int = 160
y: int = 120

light: Set[KeyLight] = set()

bgr: numpy.uint8 = numpy.uint8(255)
bgg: numpy.uint8 = numpy.uint8(255)
bgb: numpy.uint8 = numpy.uint8(255)

brightness: numpy.uint8 = numpy.uint8(100)

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

        if GKey.M1 in keys:
            if KeyLight.M1 in light:
                light.remove(KeyLight.M1)
            else:
                light.add(KeyLight.M1)
        if GKey.M2 in keys:
            if KeyLight.M2 in light:
                light.remove(KeyLight.M2)
            else:
                light.add(KeyLight.M2)
        if GKey.M3 in keys:
            if KeyLight.M3 in light:
                light.remove(KeyLight.M3)
            else:
                light.add(KeyLight.M3)
        if GKey.MR in keys:
            if KeyLight.MR in light:
                light.remove(KeyLight.MR)
            else:
                light.add(KeyLight.MR)

        if GKey.G01 in keys:
            bgr = numpy.uint8(0)
        if GKey.G07 in keys:
            bgr = numpy.uint8(85)
        if GKey.G02 in keys:
            bgr = numpy.uint8(170)
        if GKey.G08 in keys:
            bgr = numpy.uint8(255)
        if GKey.G03 in keys:
            bgg = numpy.uint8(0)
        if GKey.G09 in keys:
            bgg = numpy.uint8(85)
        if GKey.G04 in keys:
            bgg = numpy.uint8(170)
        if GKey.G10 in keys:
            bgg = numpy.uint8(255)
        if GKey.G05 in keys:
            bgb = numpy.uint8(0)
        if GKey.G11 in keys:
            bgb = numpy.uint8(85)
        if GKey.G06 in keys:
            bgb = numpy.uint8(170)
        if GKey.G12 in keys:
            bgb = numpy.uint8(255)

        if DisplayKey.OK in keys:
            brightness += 1
            if brightness > 100:
                brightness = numpy.uint8(0)

        # http://seriot.ch/pycairo/

        ctx = cairo.Context(img)
        ctx.rotate(-math.pi / 2)
        ctx.scale(-1, 1)

        pat = cairo.LinearGradient(0.0, 0.0, 0.0, image_size[1])
        pat.add_color_stop_rgba(1, 0.7, 0, 0, 0.5)  # First stop, 50% opacity
        pat.add_color_stop_rgba(0, 0.9, 0.7, 0.2, 1)  # Last stop, 100% opacity

        ctx.rectangle(0, 0, image_size[0], image_size[1])  # Rectangle(x0, y0, x1, y1)
        ctx.set_source(pat)
        ctx.fill()

        ctx.set_source_rgb(0, 0, 0)
        ctx.select_font_face("Consolas")
        ctx.set_font_size(28)
        ctx.move_to(image_size[0] - 70, image_size[1] - 20)
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

        g19.set_enabled_m_keys(light)

        g19.set_bg_color(bgr, bgg, bgb)

        g19.set_display_brightness(brightness)

        g19.send_frame(img.get_data())
except KeyboardInterrupt:
    pass
finally:
    kl.stop()
    g19.reset()
    logging.info("END")
