import logging
import threading
from enum import Enum
from typing import Set, Union, List

from logitech.g19 import G19


class DisplayKey(Enum):
    SETTINGS = 0x01
    BACK = 0x02
    MENU = 0x04
    OK = 0x08
    RIGHT = 0x10
    LEFT = 0x20
    DOWN = 0x40
    UP = 0x80

    @staticmethod
    def get_display_keys(key_code: int) -> List:
        keys = []
        for key in DisplayKey:
            if key_code & key.value > 0:
                keys.append(key)
        return keys


class GKey(Enum):
    G01 = 0x000001
    G02 = 0x000002
    G03 = 0x000004
    G04 = 0x000008
    G05 = 0x000010
    G06 = 0x000020
    G07 = 0x000040
    G08 = 0x000080
    G09 = 0x000100
    G10 = 0x000200
    G11 = 0x000400
    G12 = 0x000800
    M1 = 0x001000
    M2 = 0x002000
    M3 = 0x004000
    MR = 0x008000
    LIGHT = 0x080000

    @staticmethod
    def get_g_keys(key_code: int) -> List:
        keys = []
        for key in GKey:
            if key_code & key.value > 0:
                keys.append(key)
        return keys


class Light(Enum):
    M1 = 0x80
    M2 = 0x40
    M3 = 0x20
    MR = 0x10

    @staticmethod
    def set_to_code(s: Set):
        code = 0
        for v in s:
            code |= v.value
        return code


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
