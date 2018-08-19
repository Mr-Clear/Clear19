# coding: utf-8
"""Applet manager"""
from time import sleep
import random
import datetime
import timeit
import PIL.Image as Img
import libdraw
from logitech.g19 import G19
from coloradapter import ColorAdapter
from appmgr.keybindings import KeyBindings

class AppMgr(object):
    """docstring for AppMgr."""
    def __init__(self):
        super(AppMgr, self).__init__()
        # self.__applet = AppMgrApplet()
        random.seed()
        self.__lcd = G19(True)
        self.__key_listener = KeyBindings(self.__lcd)
        self.__lcd.add_key_listener(self.__key_listener)
        self.__lcd.start_event_handling()
        self.__drawer = libdraw.Drawer(libdraw.Frame())
        self.__color_adapter = ColorAdapter(self.ambient_callback)
        self.__cur_app = UrPidor(self.__drawer)
        self.__color_adapter.start()


    def routine(self):
        """Routine for applet manager"""
        self.__cur_app.startup()
        try:
            while True:
                tik = timeit.default_timer()
                self.__cur_app.routine()
                print "__cur_app.routine: " + str(timeit.default_timer() - tik)
                self.__lcd.send_frame(self.__drawer.get_frame_data())
                sleep(self.__cur_app.get_period())
        except KeyboardInterrupt:
            self.shutdown()

    def ambient_callback(self, color_rgb):
        """Callback for ColorAdapter"""
        self.__lcd.set_bg_color(color_rgb[0], color_rgb[1], color_rgb[2])
        self.__cur_app.ambient_callback(color_rgb)

    def shutdown(self):
        """Shutdown appmgr"""
        self.__lcd.reset()
        self.__lcd.stop_event_handling()
        self.__color_adapter.shutdown()

# class AppMgrApplet(object):
#     """docstring for AppMgrApplet."""
#     def __init__(self):
#         super(AppMgrApplet, self).__init__()
#         self.apps_list = [UrPidor()]

class Applet(object):
    """docstring for Applet."""
    def __init__(self, drawer, period=1):
        super(Applet, self).__init__()
        self._drawer = drawer
        self._period = period

    def startup(self):
        """Draw init image on screen"""
        pass

    def get_period(self):
        """Getter for _period"""
        return self._period

    def ambient_callback(self, color_rgb):
        """Callback for ambient_light"""
        pass

class UrPidor(Applet):
    """docstring for UrPidor."""
    def __init__(self, drawer):
        super(UrPidor, self).__init__(drawer, 0.7)
        self.name = "Watch"
        self.__background = Img.open(u"/home/grayhook/Изображения/us.jpg")
        self.__watch_alpha = 0.6
        self.__bg_color = [177, 31, 80, self.__watch_alpha]

    def startup(self):
        """Draw init image on screen"""
        drawer = self._drawer
        time = datetime.datetime.now().strftime("%H:%M:%S")

        drawer.draw_image([0, 0], [320, 240], self.__background)
        drawer.draw_rectangle([0, 90], [320, 85], self.__bg_color)
        drawer.draw_text([32, 90], 72, time)


    def routine(self):
        """Applet's routine"""
        start_time = timeit.default_timer()
        drawer = self._drawer
        time = datetime.datetime.now().strftime("%H:%M:%S")
        # tdelta = datetime.datetime(2018, 7, 13, 19, 50) - datetime.datetime.now()
        # time = digit_fit_width(tdelta.days, 2) + ":" + \
        #        digit_fit_width(tdelta.seconds // 3600, 2) + ":" +\
        #        digit_fit_width(tdelta.seconds // 60 % 60, 2) + ":" +\
        #        digit_fit_width(tdelta.seconds % 60, 2)

        drawer.draw_image([0, 0], [320, 240, 0, 90, 320, 175], self.__background)
        drawer.draw_rectangle([0, 90], [320, 85], self.__bg_color)
        drawer.draw_text([32, 90], 72, time)
        # drawer.draw_text([0, 94], 64, time)
        print "draw_screen: " + str(timeit.default_timer() - start_time)
        self._period = 1 - (timeit.default_timer() - start_time)

    def ambient_callback(self, color_rgb):
        """Callback for ambient_light"""
        color_rgba = color_rgb
        color_rgba.append(self.__watch_alpha)
        self.__bg_color = color_rgba

def digit_fit_width(digit, width):
    """Fit digit in width and return string"""
    result = str(digit)
    while len(result) < width:
        result = "0" + result
    return result
