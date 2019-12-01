#!/usr/bin/env python3

import logging
from logitech.g19 import G19
import time

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

try:
    time.sleep(100)
except KeyboardInterrupt:
    pass

kl.stop()
g19.reset()
logging.info("END")
