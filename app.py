#!/usr/bin/env python3

import logging
from logitech.g19 import G19
import time
from PIL import Image, ImageDraw

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

aa = 2
image_size = (320 * aa, 240 * aa)

img = Image.new("RGBA", image_size, (0, 0, 0, 255))

speed = 2
x = 0
y = 0

try:
    end = time.time() + 100
    while time.time() < end:
        keys = kl.pressed_keys()
        if DisplayKey.UP in keys:
            y = y - speed
        if DisplayKey.DOWN in keys:
            y = y + speed
        if DisplayKey.LEFT in keys:
            x = x - speed
        if DisplayKey.RIGHT in keys:
            x = x + speed
        img = Image.new("RGBA", image_size, (0, 0, 0, 255))
        draw = ImageDraw.Draw(img)
        draw.ellipse([x * aa, y * aa, (x + 50) * aa, (y + 50) * aa], (255, 255, 255, 255))
        g19.send_frame(g19.convert_image_to_frame(img))
except KeyboardInterrupt:
    pass

kl.stop()
g19.reset()
logging.info("END")
