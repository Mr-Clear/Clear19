#!/usr/bin/env python3
import logging
import math
import signal
from datetime import timedelta
from queue import Queue
from typing import Union, Type, Dict, Optional

import cairocffi as cairo
from usb.core import USBError

from clear19.App import Global
from clear19.App.main_screen import MainScreen
from clear19.App.menu_screen import MenuScreen
from clear19.App.screens import Screens
from clear19.App.time_screen import TimeScreen
from clear19.App.weather_screen import WeatherScreen
from clear19.logitech.g19 import G19, DisplayKey
from clear19.logitech.g19_simulator import G19Simulator
from clear19.logitech.key_listener import KeyListener
from clear19.scheduler import TaskParameters
from clear19.widgets.color import Color
from clear19.widgets.geometry import Size
from clear19.widgets.widget import AppWidget, Screen

log = logging.getLogger(__name__)


class App(AppWidget):
    _image: cairo.ImageSurface
    _g19: Optional[Union[G19, G19Simulator]]
    _screen_size: Size
    _running: bool
    _screens: Dict[Screens, Screen]
    _exit_code: int = 0

    def __init__(self):
        try:
            schedule_queue: Queue[Union[TaskParameters, KeyListener.KeyEvent]] = Queue()
            log.debug("Connect LCD")
            try:
                self._g19 = G19()
            except USBError as e:
                log.error("Cannot create G19 object: " + str(e))
                self._g19 = G19Simulator(self)
            self._screen_size = self._g19.image_size
            self._image = cairo.ImageSurface(cairo.FORMAT_RGB16_565,
                                             round(self.screen_size.height),
                                             round(self.screen_size.width))

            super().__init__()
            Global.init(self.scheduler)
            self.foreground = Color.GRAY90
            self._screens = {Screens.MAIN: MainScreen(self),
                             Screens.TIME: TimeScreen(self),
                             Screens.MENU: MenuScreen(self),
                             Screens.WEATHER: WeatherScreen(self)}
            self.current_screen = Screens.MAIN

            if self._g19:
                key_listener = KeyListener(self._g19, schedule_queue, self.scheduler)
            else:
                key_listener = None

            signal.signal(signal.SIGINT, self._on_signal)
            signal.signal(signal.SIGTERM, self._on_signal)
            self._running = True
            self.scheduler.schedule_to_queue(timedelta(milliseconds=10), schedule_queue, 'UPDATE')
            while self._running:
                p = schedule_queue.get()
                if isinstance(p, TaskParameters):
                    if p.command == 'UPDATE':
                        if self.dirty:
                            self.update_lcd()
                    else:
                        log.warning(f"Unknown command: {p.command}")
                elif isinstance(p, KeyListener.KeyEvent):
                    if p.type == KeyListener.KeyEvent.Type.DOWN:
                        self.on_key_down(p)
                    elif p.type == KeyListener.KeyEvent.Type.UP:
                        self.on_key_up(p)
                    else:
                        log.critical(f"Unknown key event: {p}")
                else:
                    log.warning(f"Unknown queue content: {p}")
            if key_listener:
                key_listener.stop()
            self.scheduler.stop_scheduler()

        finally:
            if self._g19 is not None:
                log.debug("Reset LCD")
                self._g19.reset()

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
        # noinspection PyBroadException
        try:
            self.paint(ctx)
        except Exception:
            log.error("Error when updating display.", exc_info=True)
        if self._g19:
            self._g19.send_frame(self._image.get_data())

    def get_lcd_context(self) -> cairo.Context:
        ctx = cairo.Context(self._image)
        ctx.rotate(-math.pi / 2)
        ctx.scale(-1, 1)
        return ctx

    @property
    def screen_size(self) -> Size:
        return self._screen_size

    @property
    def exit_code(self) -> int:
        return self._exit_code

    # noinspection PyUnusedLocal
    def _on_signal(self, signum, frame):
        # noinspection PyArgumentList
        log.info(f"Received signal {signum}({signal.Signals(signum).name})")
        self._running = False

    def screens(self) -> Type[Screens]:
        return Screens

    def _screen_object(self, screen: Screens) -> Screen:
        return self._screens[screen]

    def exit(self, exit_code: int = 0):
        self._exit_code = exit_code
        self._running = False
