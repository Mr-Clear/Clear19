#!/usr/bin/env python3
import signal
from datetime import timedelta
from queue import Queue
from typing import Union

import usb

from clear19.logitech.g19 import G19

import cairo

import logging
import math

from clear19.scheduler import TaskParameters
from clear19.widgets.geometry.size import Size
from clear19.widgets.main_screen import MainScreen
from clear19.widgets.widget import AppWidget

logging.basicConfig(format="%(asctime)s [%(levelname)-8s] %(message)s", level=logging.DEBUG, force=True)


class App(AppWidget):
    __image: cairo.ImageSurface
    __g19: Union[G19, None]
    __screen_size: Size
    __running: bool

    def __init__(self):
        try:
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

            self.current_screen = MainScreen(self)

            super().__init__(self)

            signal.signal(signal.SIGINT, self.__on_signal)
            signal.signal(signal.SIGTERM, self.__on_signal)
            self.__running = True
            schedule_queue: Queue[TaskParameters] = Queue()
            self.scheduler.schedule_to_queue(timedelta(milliseconds=10), schedule_queue, "UPDATE")
            while self.__running:
                p = schedule_queue.get()
                if p.command == "UPDATE":
                    if self.dirty:
                        self.update_lcd()
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


if __name__ == "__main__":
    logging.info("START")
    App()
    logging.info("END")
