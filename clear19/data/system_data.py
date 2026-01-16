from datetime import timedelta
from threading import Lock
from typing import List, Callable, Type, Tuple, Dict

import psutil
from psutil import NoSuchProcess, Process

from clear19.scheduler import Scheduler


class SystemData:
    """
    Reads system performance data.
    """
    CpuTimes: Type = psutil._pslinux.scputimes
    MemStats: Type = psutil._ntuples.svmem

    _cpu_times_percent: CpuTimes = None
    _process_cpu_percent: List[Tuple[str, float]]

    _cpu_listeners: List[Callable[[CpuTimes], None]]
    _cpu_listeners_lock: Lock
    _mem_listeners: List[Callable[[MemStats], None]]
    _mem_listeners_lock: Lock
    _process_listeners: List[Callable[[List[Tuple[str, float]]], None]]
    _process_listeners_lock: Lock

    _processes: Dict[int, Process]

    def __init__(self, scheduler: Scheduler):
        self._cpu_listeners = []
        self._cpu_listeners_lock = Lock()
        self._mem_listeners = []
        self._mem_listeners_lock = Lock()
        self._process_listeners = []
        self._process_listeners_lock = Lock()
        self._processes = {}
        scheduler.schedule_synchronous(timedelta(seconds=1), self._update_1)
        scheduler.schedule_synchronous(timedelta(seconds=10), self._update_10)
        self._update_1()
        self._update_10()

    def _update_1(self, _=None):
        self._cpu_times_percent = psutil.cpu_times_percent()
        self._mem_stats = psutil.virtual_memory()
        self._fire_cpu_update(self._cpu_times_percent)
        self._fire_mem_update(self._mem_stats)

    def _update_10(self, _=None):
        process_cpu_percent = []
        old_processes = self._processes
        new_processes = {}
        for pid in psutil.pids():
            if pid in old_processes:
                p = old_processes.pop(pid)
            else:
                try:
                    p = psutil.Process(pid)
                except NoSuchProcess:
                    p = None
            if p:
                process_cpu_percent.append((p.name(), p.cpu_percent()))
                new_processes[pid] = p
        self._processes = new_processes
        self._process_cpu_percent = process_cpu_percent
        self._fire_process_update(process_cpu_percent)

    @property
    def cpu_times_percent(self) -> CpuTimes:
        return self._cpu_times_percent

    @property
    def cpu_count(self) -> int:
        return psutil.cpu_count()

    @property
    def mem_stats(self) -> MemStats:
        return self._mem_stats

    @property
    def process_cpu_percent(self) -> List[Tuple[str, float]]:
        return self._process_cpu_percent

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

    def add_process_listener(self, listener: Callable[[List[Tuple[str, float]]], None]):
        with self._process_listeners_lock:
            self._process_listeners.append(listener)

    def _fire_process_update(self, data: List[Tuple[str, float]]):
        with self._process_listeners_lock:
            for listener in self._process_listeners:
                listener(data)
