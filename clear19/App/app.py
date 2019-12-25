#!/usr/bin/env python3
import os
import signal
import traceback
from datetime import timedelta
from queue import Queue
from typing import Union, Type, Dict

import usb

from clear19.App.screens import Screens
from clear19.logitech.g19 import G19

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

            super().__init__(self)
            self.__screens = {Screens.MAIN: MainScreen(self), Screens.TIME: TimeScreen(self)}
            self.set_screen(Screens.MAIN)

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
                        self.current_screen.on_key_down(p.key)
                    elif p.type == KeyListener.KeyEvent.Type.UP:
                        self.current_screen.on_key_up(p.key)
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

    def set_screen(self, screen: Screens):
        self.current_screen = self.__screens[screen]


if __name__ == "__main__":
    logging.info("START")
    # noinspection PyBroadException
    try:
        App()
    except Exception as e:
        logging.critical("Exception in App\n{}".format(''.join(traceback.format_exception(None, e, e.__traceback__))))
        os._exit(os.EX_SOFTWARE)
    logging.info("END")
