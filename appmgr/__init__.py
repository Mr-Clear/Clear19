# coding: utf-8
"""Applet manager"""
from time import sleep
import random
import libdraw
from logitech.g19 import G19

class AppMgr(object):
    """docstring for AppMgr."""
    def __init__(self):
        super(AppMgr, self).__init__()
        # self.__applet = AppMgrApplet()
        self.__lcd = G19(True)
        self.__drawer = libdraw.Drawer(libdraw.Frame())
        self.__cur_app = UrPidor()

    def routine(self):
        """Routine for applet manager"""
        try:
            while True:
                self.__cur_app.routine(self.__drawer)
                self.__lcd.send_frame(self.__drawer.get_frame_data())
                sleep(1)
        except KeyboardInterrupt:
            self.__lcd.reset()


# class AppMgrApplet(object):
#     """docstring for AppMgrApplet."""
#     def __init__(self):
#         super(AppMgrApplet, self).__init__()
#         self.apps_list = [UrPidor()]

class UrPidor(object):
    """docstring for UrPidor."""
    def __init__(self):
        super(UrPidor, self).__init__()
        self.name = "U r pidor"

    def routine(self, drawer):
        """Applet's routine"""
        random.seed()
        drawer.draw_rectangle([0, 0], [320, 240], [255, 255, 255])
        drawer.draw_rectangle([random.randint(20, 25), random.randint(20, 25)], [100, 100], [0, 0, 255])
        drawer.draw_rectangle([170, 120], [50, 50], [0, 0, 255])
        drawer.draw_image_from_file("/home/grayhook/Изображения/golovka.png", [170, 120], [150, 120])
        drawer.draw_text([40, 120], 32, u"ТЫ ПИДОР")
