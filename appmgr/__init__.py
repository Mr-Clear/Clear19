# coding: utf-8
"""Applet manager"""
from time import sleep
import random
import datetime
import timeit
import threading
import logging
from gi.repository import GLib
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import PIL.Image as Img
import libdraw
from logitech.g19 import G19
from coloradapter import ColorAdapter
from appmgr.keybindings import KeyBindings


# def print_notification(bus, message):
#     keys = ["app_name", "replaces_id", "app_icon", "summary",
#             "body", "actions", "hints", "expire_timeout"]
#     args = message.get_args_list()
#     print "print_notification"
#     if len(args) == 8:
#         notification = dict([(keys[i], args[i]) for i in range(8)])
#         print notification["summary"], notification["body"]

class AppMgr(object):
    """docstring for AppMgr."""
    def __init__(self):
        fmat = u'%(levelname)-8s [%(asctime)s] <%(funcName)s:%(lineno)s> %(message)s'
        fname = u'/tmp/g19driver.log'
        logging.basicConfig(format=fmat, filename=fname, level=logging.INFO)
        # logging.debug(u'AppMgr initializes...')
        super(AppMgr, self).__init__()
        # logging.debug(u'AppMgr has inited class')
        # self.__applet = AppMgrApplet()
        random.seed()
        self.__exit = False
        self.__lcd = G19(True)
        # logging.debug(u'AppMgr has inited G19')
        self.__key_listener = KeyBindings(self.__lcd)
        # logging.debug(u'AppMgr has inited KeyBindings')
        self.__lcd.add_key_listener(self.__key_listener)
        # logging.debug(u'AppMgr has inited key listener')
        self.__lcd.start_event_handling()
        # logging.debug(u'AppMgr has started event handling')
        self.__drawer = libdraw.Drawer(libdraw.Frame())
        # logging.debug(u'AppMgr has inited Drawer')
        self.__color_adapter = ColorAdapter(self.ambient_callback)
        # logging.debug(u'AppMgr has inited ColorAdapter')
        self.__cur_app = UrPidor(self.__drawer)
        # logging.debug(u'AppMgr has inited start app')
        self.__color_adapter.start()
        # logging.debug(u'AppMgr\'s ColorAdapter started')
        self.__loop = GLib.MainLoop()
        self.__notification_thread = threading.Thread(target=self.__notification_thread_target,
                                                      name='Notification thread')
        self.__notification_thread.start()
        # logging.debug(u'AppMgr\'s notification thread started')
        logging.info(u'AppMgr has been inited')

    def __notification_thread_target(self):
        try:
            # logging.debug(u'Notification thread started. Waiting 10 secs...')
            sleep(10)
            # logging.debug(u'Notification thread init dbus')
            DBusGMainLoop(set_as_default=True)
            session_bus = dbus.SessionBus()
            session_bus.add_match_string_non_blocking("eavesdrop=true, interface='org.freedesktop.Notifications', member='Notify'")
            session_bus.add_message_filter(self.__print_notification)
            # logging.debug(u'Notification thread running loop...')
            self.__loop.run()
        except KeyboardInterrupt:
            logging.info(u'Notification thread has catch KeyboardInterrupt')
            self.shutdown()

    def __print_notification(self, bus, message):
        # logging.debug(u'Printing notification...')
        keys = ["app_name", "replaces_id", "app_icon", "summary",
                "body", "actions", "hints", "expire_timeout"]
        args = message.get_args_list()
        # logging.debug(u'Get notification\'s args')
        if len(args) == 8:
            notification = dict([(keys[i], args[i]) for i in range(8)])
            logging.info(u'Notification: %s: %s', notification["summary"], notification["body"])
            # logging.debug(u'Remebering current app')
            drawer = libdraw.Drawer(libdraw.Frame())
            notification_app = Notification(drawer, notification)
            # logging.debug(u'Starting up notification app')
            notification_app.startup()
            # logging.debug(u'Sending new frame')
            self.__lcd.send_frame(drawer.get_frame_data())
            # logging.debug(u'Setting interrupt')
            self.__lcd.set_interrupt()
            timeout = notification["expire_timeout"] / 1000 \
                      if notification["expire_timeout"] > 2000 \
                      else 4
            # logging.debug(u'Waiting %d secs...', timeout)
            sleep(timeout)
            # # logging.debug(u'Starting up app')
            # self.__cur_app.startup()
            # logging.debug(u'Unsetting interrupt')
            self.__lcd.unset_interrupt()
            # logging.debug(u'Sending frame')
            self.__lcd.send_frame(self.__drawer.get_frame_data())

    def routine(self):
        """Routine for applet manager"""
        # logging.debug(u'Starting up current app')
        self.__cur_app.startup()
        try:
            while True:
                # # logging.debug(u'Doing routine')
                self.__cur_app.routine()
                if self.__exit:
                    # logging.debug(u'Exit flag is up — exiting')
                    break
                # # logging.debug(u'Sending frame')
                self.__lcd.send_frame(self.__drawer.get_frame_data())
                sleep(self.__cur_app.get_period())
        except (KeyboardInterrupt, SystemExit):
            logging.info(u'Catching KeyboardInterrupt')
            self.shutdown()

    def ambient_callback(self, color_rgb):
        """Callback for ColorAdapter"""
        # # logging.debug(u'Ambient callback')
        self.__lcd.set_bg_color(color_rgb[0], color_rgb[1], color_rgb[2])
        self.__cur_app.ambient_callback(color_rgb)

    def shutdown(self):
        """Shutdown appmgr"""
        logging.info(u'Shutting down')
        if self.__exit:
            # logging.debug(u'Already exited... (\'-\' )')
            return
        self.__exit = True
        if self.__loop.is_running():
            # logging.debug(u'Stopping loop')
            self.__loop.quit()
        if self.__notification_thread.isAlive() and threading.current_thread() != self.__notification_thread:
            # logging.debug(u'Waiting notification app')
            self.__notification_thread.join()
        # logging.debug(u'Reseting lcd...')
        self.__lcd.reset()
        # logging.debug(u'Stopping event handler')
        self.__lcd.stop_event_handling()
        # logging.debug(u'Shutting down ColorAdapter')
        self.__color_adapter.shutdown()

class Applet(object):
    """docstring for Applet."""
    def __init__(self, drawer, period=1):
        super(Applet, self).__init__()
        # logging.debug(u'Initing applet')
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
        self.__background = Img.open(u"/home/grayhook/Изображения/usny.jpg")
        self.__background = self.__background.resize((320, 240), Img.CUBIC)

        self.__watch_alpha = 0.6
        self.__bg_color = [177, 31, 80, self.__watch_alpha]

    def startup(self):
        """Draw init image on screen"""
        drawer = self._drawer
        time = datetime.datetime.now().strftime("%H:%M:%S")

        drawer.draw_image([0, 0], [320, 240], self.__background)
        drawer.draw_rectangle([0, 90], [320, 85], self.__bg_color)
        drawer.draw_textline([32, 90], 72, time)


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

        # drawer.draw_image([0, 0], [320, 240, 0, 90, 320, 175], self.__background)
        drawer.draw_image([0, 0], [320, 240], self.__background)
        drawer.draw_rectangle([0, 90], [320, 85], self.__bg_color)
        drawer.draw_textline([32, 90], 72, time)

        # drawer.draw_text([0, 94], 64, time)
        # print "draw_screen: " + str(timeit.default_timer() - start_time)
        self._period = (1 - (timeit.default_timer() - start_time))
        if self._period < 0:
            self._period = 0

    def ambient_callback(self, color_rgb):
        """Callback for ambient_light"""
        color_rgba = color_rgb
        color_rgba.append(self.__watch_alpha)
        self.__bg_color = color_rgba


class Notification(Applet):
    """docstring for UrPidor."""
    def __init__(self, drawer, message):
        super(Notification, self).__init__(drawer, 0.7)
        # logging.debug(u'Initing notification applet')
        self.name = "Notification"
        self.__background = Img.open(u"/home/grayhook/Изображения/usny.jpg")
        self.__background = self.__background.resize((320, 240), Img.CUBIC)
        self.__watch_alpha = 0.6
        self.__bg_color = [66, 240, 120, self.__watch_alpha]
        self.__message = message
        self._period = 1

    def startup(self):
        """Draw init image on screen"""
        # logging.debug(u'Startup notification applet')
        drawer = self._drawer
        time = datetime.datetime.now().strftime("%H:%M:%S")

        drawer.draw_image([0, 0], [320, 240], self.__background)
        # logging.debug(u'Draw rectangle 1')
        drawer.draw_rectangle([0, 0], [320, 240], self.__bg_color)
        # logging.debug(u'Draw textline 1')
        drawer.draw_textline([15, 200], 32, time)
        # logging.debug(u'Draw textline 2')
        drawer.draw_textline([15, 10], 32, self.__message["summary"])
        # logging.debug(u'Draw text fitted')
        try:
            drawer.draw_text_fitted([15, 50], 24, self.__message["body"])
        except Exception as e:
            logging.error(e)
        # logging.debug(u'Drawing finishd')


    def routine(self):
        """Applet's routine"""
        pass



def digit_fit_width(digit, width):
    """Fit digit in width and return string"""
    result = str(digit)
    while len(result) < width:
        result = "0" + result
    return result
