# coding: utf-8
"""Userspace driver"""

import time
import random
from logitech.g19 import G19
from appmgr import AppMgr
import libdraw

def main():
    """Main"""

    app_mgr = AppMgr()
    time.sleep(1)
    app_mgr.routine()

    lcd = G19(True)
    drawer = libdraw.Drawer(libdraw.Frame())
    drawer.draw_rectangle([0, 0], [320, 240], [255, 255, 255])
    drawer.draw_rectangle([random.randint(20, 25), random.randint(20, 25)], [100, 100], [0, 0, 255])
    drawer.draw_rectangle([170, 120], [50, 50], [0, 0, 255])
    drawer.draw_image_from_file("/home/grayhook/Изображения/golovka.png", [170, 120], [150, 120])
    drawer.draw_text([40, 120], 32, u"ТЫ ПИДОР")
    lcd.send_frame(drawer.get_frame_data())

if __name__ == '__main__':
    main()

# if __name__ == '__main__':
#     try:
#         lg19 = G19()
#         lg19.start_event_handling()
#         while True:
#             time.sleep(10)
#     except KeyboardInterrupt:
#         lg19.stop_event_handling()
