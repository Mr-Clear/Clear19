#!/usr/bin/env python3
import logging
from dataclasses import dataclass
from datetime import timedelta, datetime
from queue import Queue
from threading import Lock, Thread
from typing import List, Callable, Optional

from fritzconnection.lib.fritzhosts import FritzHosts
from fritzconnection.lib.fritzstatus import FritzStatus
from fritzconnection.lib.fritzwlan import FritzWLAN

from clear19.scheduler import Scheduler, TaskParameters

log = logging.getLogger(__name__)


@dataclass()
class FritzBoxData:
    status: FritzStatus = None
    hosts: FritzHosts = None
    wlan: FritzWLAN = None


class FritzBox:
    _address: str
    _password: str
    _listeners: List[Callable[[FritzBoxData], None]]
    _listeners_mutex: Lock
    _running: bool = True
    _queue: 'Queue[TaskParameters]'
    _current_data: FritzBoxData = None

    def __init__(self, scheduler: Scheduler, address: str, password: str):
        self._address = address
        self._password = password
        self._queue = Queue(maxsize=1)
        self._listeners = []
        self._listeners_mutex = Lock()
        scheduler.schedule_to_queue(timedelta(seconds=5), self._queue)
        Thread(target=self._poll_loop, daemon=True).start()

    def _poll_loop(self):
        self._current_data = FritzBoxData()
        last_hosts: Optional[datetime] = None
        while self._running:
            try:
                self._current_data.status = FritzStatus(address=self._address, password=self._password)
                if not last_hosts or (datetime.now() - last_hosts) / timedelta(seconds=10) >= 1:
                    self.current_data.hosts = FritzHosts(address=self._address, password=self._password)
                    self.current_data.wlan = FritzWLAN(address=self._address, password=self._password)
                    last_hosts = datetime.now()
            except IOError as e:
                log.warning(f"Failed to get FritzBox data: {e}")
            self._notify_listeners()
            self._queue.get()

    def add_listener(self, listener: Callable[[FritzBoxData], None]):
        with self._listeners_mutex:
            self._listeners.append(listener)

    def _notify_listeners(self):
        with self._listeners_mutex:
            current_data = self._current_data
            for listener in self._listeners:
                # noinspection PyBroadException
                try:
                    listener(current_data)
                except Exception:
                    log.error("Exception in FritzBox listener.", exc_info=True)

    @property
    def current_data(self) -> FritzBoxData:
        return self._current_data
