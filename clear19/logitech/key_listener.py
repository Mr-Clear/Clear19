import logging
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from queue import Queue
from threading import Thread
from typing import Set, Union

from clear19.logitech.g19 import DisplayKey, G19, GKey, G19Key
from clear19.scheduler import Scheduler, TaskParameters


class KeyListener:
    @dataclass(frozen=True)
    class KeyEvent:
        class Type(Enum):
            DOWN = 1
            UP = 2

        type: Type
        key: G19Key

    __g19: G19
    __pressed_display_keys: int
    __pressed_g_keys: int
    __pressed_keys: Set[Union[DisplayKey, GKey]]
    __poll_interval: float
    __queue: 'Queue[KeyEvent]'
    __scheduler: Scheduler
    __job_queue: 'Queue[TaskParameters]'
    __job_id: int
    __running: bool

    def __init__(self, g19: G19, queue: "Queue[KeyEvent]", scheduler: Scheduler):
        self.__g19 = g19
        self.__queue = queue
        self.__scheduler = scheduler
        self.__job_queue = Queue(maxsize=1)
        self.__running = True
        self.__pressed_display_keys = 0
        self.__pressed_g_keys = 0
        self.__pressed_keys = set()
        self.__poll_interval: float = 0.01
        self.__job_id = scheduler.schedule_to_queue(timedelta(seconds=self.__poll_interval), self.__job_queue,
                                                    priority=0, command="KEY")
        Thread(target=self.__key_reader).start()

    def stop(self) -> None:
        self.__scheduler.stop_job(self.__job_id)
        self.__running = False

    # noinspection PyCallByClass
    def __key_reader(self) -> None:
        while self.__running:
            self.__job_queue.get()
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

            for key in down_keys:
                self.__queue.put(KeyListener.KeyEvent(KeyListener.KeyEvent.Type.DOWN, key))

            for key in up_keys:
                self.__queue.put(KeyListener.KeyEvent(KeyListener.KeyEvent.Type.UP, key))

    def pressed_keys(self) -> Set[Union[DisplayKey, GKey]]:
        return self.__pressed_keys
