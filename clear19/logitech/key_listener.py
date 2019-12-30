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

    _g19: G19
    _pressed_display_keys: int = 0
    _pressed_g_keys: int = 0
    _pressed_keys: Set[Union[DisplayKey, GKey]]
    _poll_interval: float = 0.01
    _queue: 'Queue[KeyEvent]'
    _scheduler: Scheduler
    _job_queue: 'Queue[TaskParameters]'
    _job_id: int
    _running: bool = True

    def __init__(self, g19: G19, queue: "Queue[KeyEvent]", scheduler: Scheduler):
        self._g19 = g19
        self._queue = queue
        self._scheduler = scheduler
        self._job_queue = Queue(maxsize=1)
        self._pressed_keys = set()
        self._job_id = scheduler.schedule_to_queue(timedelta(seconds=self._poll_interval), self._job_queue,
                                                   priority=0, command="KEY")
        Thread(target=self._key_reader).start()

    def stop(self) -> None:
        self._scheduler.stop_job(self._job_id)
        self._running = False

    # noinspection PyCallByClass
    def _key_reader(self) -> None:
        while self._running:
            self._job_queue.get()
            down_keys = set()
            up_keys = set()

            data = self._g19.read_display_menu_keys()
            if data:
                if data[1] != 128:
                    logging.warning("Unknown data: %s", data)
                down_key_codes: int = ~self._pressed_display_keys & data[0]
                up_key_codes: int = self._pressed_display_keys & ~data[0]
                if down_key_codes:
                    down_display_keys = DisplayKey.get_display_keys(down_key_codes)
                    self._pressed_keys.update(down_display_keys)
                    down_keys.update(down_display_keys)
                if up_key_codes:
                    up_display_keys = DisplayKey.get_display_keys(up_key_codes)
                    self._pressed_keys = self._pressed_keys.difference(up_display_keys)
                    up_keys.update(up_display_keys)
                self._pressed_display_keys = data[0]

            data = self._g19.read_g_and_m_keys()
            if data and data[0] == 2:
                key_code = data[1] | data[2] << 8 | data[3] << 16
                down_key_codes: int = ~self._pressed_g_keys & key_code
                up_key_codes: int = self._pressed_g_keys & ~key_code
                if down_key_codes:
                    down_g_keys = GKey.get_g_keys(down_key_codes)
                    self._pressed_keys.update(down_g_keys)
                    down_keys.update(down_g_keys)
                if up_key_codes:
                    up_g_keys = GKey.get_g_keys(up_key_codes)
                    self._pressed_keys = self._pressed_keys.difference(up_g_keys)
                    up_keys.update(up_g_keys)
                self._pressed_g_keys = key_code

            for key in down_keys:
                self._queue.put(KeyListener.KeyEvent(KeyListener.KeyEvent.Type.DOWN, key))

            for key in up_keys:
                self._queue.put(KeyListener.KeyEvent(KeyListener.KeyEvent.Type.UP, key))

    def pressed_keys(self) -> Set[Union[DisplayKey, GKey]]:
        return self._pressed_keys
