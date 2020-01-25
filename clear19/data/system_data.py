from datetime import timedelta
from threading import Lock
from typing import List, Callable, Any

import psutil

from clear19.scheduler import Scheduler


class SystemData:
    _cpu_times_percent: Any = None

    _cpu_listeners: List[Callable[[Any], None]]
    _cpu_listeners_lock: Lock

    def __init__(self, scheduler: Scheduler):
        self._cpu_listeners = []
        self._cpu_listeners_lock = Lock()
        scheduler.schedule_synchronous(timedelta(seconds=1), self._update_1)
        scheduler.schedule_synchronous(timedelta(seconds=10), self._update_10)

    def _update_1(self, _):
        self._cpu_times_percent = psutil.cpu_times_percent()
        self._fire_cpu_update(self._cpu_times_percent)

    def _update_10(self, _):
        pass

    @property
    def cpu_times_percent(self) -> Any:
        return self._cpu_times_percent

    @property
    def cpu_count(self) -> int:
        return psutil.cpu_count()

    def add_cpu_listener(self, listener: Callable[[Any], None]):
        with self._cpu_listeners_lock:
            self._cpu_listeners.append(listener)

    def _fire_cpu_update(self, data: Any):
        with self._cpu_listeners_lock:
            for listener in self._cpu_listeners:
                listener(data)
