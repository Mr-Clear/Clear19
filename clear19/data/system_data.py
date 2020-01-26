from datetime import timedelta
from threading import Lock
from typing import List, Callable

import psutil

from clear19.scheduler import Scheduler


class SystemData:
    CpuTimes = psutil._pslinux.scputimes
    MemStats = psutil._pslinux.svmem

    _cpu_times_percent: CpuTimes = None

    _cpu_listeners: List[Callable[[CpuTimes], None]]
    _cpu_listeners_lock: Lock
    _mem_listeners: List[Callable[[MemStats], None]]
    _mem_listeners_lock: Lock

    def __init__(self, scheduler: Scheduler):
        self._cpu_listeners = []
        self._cpu_listeners_lock = Lock()
        self._mem_listeners = []
        self._mem_listeners_lock = Lock()
        scheduler.schedule_synchronous(timedelta(seconds=1), self._update_1)
        scheduler.schedule_synchronous(timedelta(seconds=10), self._update_10)

    def _update_1(self, _):
        self._cpu_times_percent = psutil.cpu_times_percent()
        self._mem_stats = psutil.virtual_memory()
        self._fire_cpu_update(self._cpu_times_percent)
        self._fire_mem_update(self._mem_stats)

    def _update_10(self, _):
        pass

    @property
    def cpu_times_percent(self) -> CpuTimes:
        return self._cpu_times_percent

    @property
    def cpu_count(self) -> int:
        return psutil.cpu_count()

    @property
    def mem_stats(self) -> MemStats:
        return self._mem_stats

    def add_cpu_listener(self, listener: Callable[[CpuTimes], None]):
        with self._cpu_listeners_lock:
            self._cpu_listeners.append(listener)

    def _fire_cpu_update(self, data: CpuTimes):
        with self._cpu_listeners_lock:
            for listener in self._cpu_listeners:
                listener(data)

    def add_mem_listener(self, listener: Callable[[MemStats], None]):
        with self._mem_listeners_lock:
            self._mem_listeners.append(listener)

    def _fire_mem_update(self, data: MemStats):
        with self._mem_listeners_lock:
            for listener in self._mem_listeners:
                listener(data)
