import logging
import threading
from typing import Set, Union

from clear19.g19 import DisplayKey, G19, GKey


class KeyListener:
    __g19: G19
    __stopped: bool = False
    __pressed_display_keys: int = 0
    __pressed_g_keys: int = 0
    __pressed_keys: Set[Union[DisplayKey, GKey]] = set()
    __poll_interval: float = 0.01

    def __init__(self, g19: G19):
        self.__g19 = g19
        self.__key_reader()

    def stop(self) -> None:
        self.__stopped = True

    def __key_reader(self) -> None:
        down_keys = set()
        up_keys = set()

        data = self.__g19.read_display_menu_keys()
        if data:
            if data[1] != 128:
                logging.warning("Unknown data: %s", data)
            down_key_codes: int = ~self.__pressed_display_keys & data[0]
            up_key_codes: int = self.__pressed_display_keys & ~data[0]
            if down_key_codes:
                down_display_keys = DisplayKey.get_display_keys(down_key_codes)
                self.__pressed_keys.update(down_display_keys)
                down_keys.update(down_display_keys)
            if up_key_codes:
                up_display_keys = DisplayKey.get_display_keys(up_key_codes)
                self.__pressed_keys = self.__pressed_keys.difference(up_display_keys)
                up_keys.update(up_display_keys)
            self.__pressed_display_keys = data[0]

        data = self.__g19.read_g_and_m_keys()
        if data and data[0] == 2:
            key_code = data[1] | data[2] << 8 | data[3] << 16
            down_key_codes: int = ~self.__pressed_g_keys & key_code
            up_key_codes: int = self.__pressed_g_keys & ~key_code
            if down_key_codes:
                down_g_keys = GKey.get_g_keys(down_key_codes)
                self.__pressed_keys.update(down_g_keys)
                down_keys.update(down_g_keys)
            if up_key_codes:
                up_g_keys = GKey.get_g_keys(up_key_codes)
                self.__pressed_keys = self.__pressed_keys.difference(up_g_keys)
                up_keys.update(up_g_keys)
            self.__pressed_g_keys = key_code

        if down_keys:
            logging.debug("Down: {}".format(down_keys))

        if up_keys:
            logging.debug("Up: {}".format(up_keys))

        if not self.__stopped:
            threading.Timer(self.__poll_interval, self.__key_reader).start()

    def pressed_keys(self) -> Set[Union[DisplayKey, GKey]]:
        return self.__pressed_keys
