#!/usr/bin/env python3
import os
import signal
import traceback
from datetime import timedelta
from queue import Queue
from typing import Union, Type, Dict

import sys
import usb

from clear19.App.menu_screen import MenuScreen
from clear19.App.screens import Screens
from clear19.logitech.g19 import G19, DisplayKey

import cairo

import logging
import math

from clear19.logitech.key_listener import KeyListener
from clear19.scheduler import TaskParameters
from clear19.widgets.geometry.size import Size
from clear19.App.main_screen import MainScreen
from clear19.App.time_screen import TimeScreen
from clear19.widgets.widget import AppWidget, Screen

logging.basicConfig(format="%(asctime)s [%(levelname)-8s] %(message)s", level=logging.DEBUG, force=True)

app_exit_code: int = 0


class App(AppWidget):
    __image: cairo.ImageSurface
    __g19: Union[G19, None]
    __screen_size: Size
    __running: bool
    __screens: Dict[Screens, Screen]

    def __init__(self):
        try:
            schedule_queue: Queue[Union[TaskParameters, KeyListener.KeyEvent]] = Queue()
            try:
                logging.debug("Connect LCD")
                self.__g19 = G19()
                self.__screen_size = self.__g19.image_size
            except usb.core.USBError as err:
                logging.error("Cannot connect to keyboard: " + str(err))
                self.__g19 = None
                self.__screen_size = Size(320, 240)
            self.__image = cairo.ImageSurface(cairo.FORMAT_RGB16_565,
                                              int(self.screen_size.height),
                                              int(self.screen_size.width))

            super().__init__()
            self.__screens = {Screens.MAIN: MainScreen(self),
                              Screens.TIME: TimeScreen(self),
                              Screens.MENU: MenuScreen(self)}
            self.current_screen = Screens.MAIN

            if self.__g19:
                key_listener = KeyListener(self.__g19, schedule_queue, self.scheduler)
            else:
                key_listener = None

            signal.signal(signal.SIGINT, self.__on_signal)
            signal.signal(signal.SIGTERM, self.__on_signal)
            self.__running = True
            self.scheduler.schedule_to_queue(timedelta(milliseconds=10), schedule_queue, "UPDATE")
            while self.__running:
                p = schedule_queue.get()
                if isinstance(p, TaskParameters):
                    if p.command == "UPDATE":
                        if self.dirty:
                            self.update_lcd()
                    else:
                        logging.warning("Unknown command: {}".format(p.command))
                elif isinstance(p, KeyListener.KeyEvent):
                    if p.type == KeyListener.KeyEvent.Type.DOWN:
                        self.on_key_down(p)
                    elif p.type == KeyListener.KeyEvent.Type.UP:
                        self.on_key_up(p)
                    else:
                        logging.critical("Unknown key event: {}".format(p))
                else:
                    logging.warning("Unknown queue content: {}".format(p))
            if key_listener:
                key_listener.stop()
            self.scheduler.stop_scheduler()

        finally:
            if self.__g19 is not None:
                logging.debug("Reset LCD")
                self.__g19.reset()

    def on_key_down(self, evt: KeyListener.KeyEvent):
        if not self._current_screen_object.on_key_down(evt.key):
            if evt.key == DisplayKey.SETTINGS:
                self.app.current_screen = Screens.MENU
            elif evt.key == DisplayKey.BACK:
                self.navigate_back()

    def on_key_up(self, evt: KeyListener.KeyEvent):
        self._current_screen_object.on_key_up(evt.key)

    def update_lcd(self):
        ctx = self.get_lcd_context()
        self.paint(ctx)
        if self.__g19:
            self.__g19.send_frame(self.__image.get_data())

    def get_lcd_context(self) -> cairo.Context:
        ctx = cairo.Context(self.__image)
        ctx.rotate(-math.pi / 2)
        ctx.scale(-1, 1)
        return ctx

    @property
    def screen_size(self) -> Size:
        return self.__screen_size

    # noinspection PyUnusedLocal
    def __on_signal(self, signum, frame):
        logging.info("Received signal {}({})".format(signum, signal.Signals(signum).name))
        self.__running = False

    def screens(self) -> Type[Screens]:
        return Screens

    def _screen_object(self, screen: Screens) -> Screen:
        return self.__screens[screen]

    def exit(self, exit_code: int = 0):
        global app_exit_code
        app_exit_code = exit_code
        self.__running = False


if __name__ == "__main__":
    logging.info("START")
    # noinspection PyBroadException
    try:
        App()
    except Exception as e:
        logging.critical("Exception in App\n{}".format(''.join(traceback.format_exception(None, e, e.__traceback__))))
        os._exit(os.EX_SOFTWARE)
    logging.info("END")
    sys.exit(app_exit_code)
