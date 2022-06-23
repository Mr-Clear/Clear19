#!/usr/bin/env python3
import logging
from dataclasses import dataclass
from datetime import timedelta
from queue import Queue
from threading import Lock, Thread
from typing import List, Callable, Optional, Tuple

from fritzconnection import FritzConnection
from fritzconnection.core.exceptions import FritzConnectionException
from fritzconnection.lib.fritzhosts import FritzHosts
from fritzconnection.lib.fritzstatus import FritzStatus
from fritzconnection.lib.fritzwlan import FritzWLAN

from clear19.scheduler import Scheduler, TaskParameters

log = logging.getLogger(__name__)


@dataclass()
class FritzBoxData:
    lan_hosts: Optional[int] = None
    wifi_hosts: Optional[int] = None

    is_linked: Optional[bool] = None
    is_connected: Optional[bool] = None
    external_ip: Optional[str] = None
    external_ipv6: Optional[str] = None
    max_bit_rate: Optional[Tuple[int, int]] = None
    transmission_rate: Optional[Tuple[int, int]] = None
    bytes_sent: Optional[int] = None
    bytes_received: Optional[int] = None


class FritzBox:
    _address: str
    _password: str
    _listeners: List[Callable[[FritzBoxData], None]]
    _listeners_mutex: Lock
    _data_mutex: Lock
    _running: bool = True
    _status_queue: 'Queue[TaskParameters]'
    _hosts_queue: 'Queue[TaskParameters]'
    current_data: Optional[FritzBoxData] = None

    def __init__(self, scheduler: Scheduler, address: str, password: str):
        self._address = address
        self._password = password
        self._listeners = []
        self._listeners_mutex = Lock()
        self._data_mutex = Lock()
        self.current_data = FritzBoxData()
        self._status_queue = Queue(maxsize=1)
        scheduler.schedule_to_queue(timedelta(seconds=3), self._status_queue)
        Thread(target=self._poll_status_loop, daemon=True).start()
        self._hosts_queue = Queue(maxsize=1)
        scheduler.schedule_to_queue(timedelta(seconds=10), self._hosts_queue)
        Thread(target=self._poll_hosts_loop, daemon=True).start()

    def _poll_status_loop(self):
        try:
            fritz_connection = FritzConnection(address=self._address, password=self._password)
        except FritzConnectionException:
            # Error is logged by FritzConnection
            return
        while self._running:
            try:
                status = FritzStatus(fc=fritz_connection)
                with self._data_mutex:
                    self.current_data.is_linked = status.is_linked
                    self.current_data.is_connected = status.is_connected
                    self.current_data.external_ip = status.external_ip
                    self.current_data.external_ipv6 = status.external_ipv6
                    self.current_data.max_bit_rate = status.max_bit_rate
                    self.current_data.transmission_rate = status.transmission_rate
                    self.current_data.bytes_sent = status.bytes_sent
                    self.current_data.bytes_received = status.bytes_received
            except IOError as e:
                log.warning(f"Failed to get FritzBox data: {e}")

            self._notify_listeners()
            self._status_queue.get()

    def _poll_hosts_loop(self):
        try:
            fritz_connection = FritzConnection(address=self._address, password=self._password)
        except FritzConnectionException:
            # Error is logged by FritzConnection
            return
        while self._running:
            try:
                hosts = FritzHosts(fc=fritz_connection)
                wlan = FritzWLAN(fc=fritz_connection)
                active_hosts = len(hosts.get_active_hosts())
                with self._data_mutex:
                    self.current_data.wifi_hosts = wlan.total_host_number
                    self.current_data.lan_hosts = active_hosts - self.current_data.wifi_hosts
            except IOError as e:
                log.warning(f"Failed to get FritzBox data: {e}")

            self._notify_listeners()
            self._hosts_queue.get()

    def add_listener(self, listener: Callable[[FritzBoxData], None]):
        with self._listeners_mutex:
            self._listeners.append(listener)

    def _notify_listeners(self):
        with self._listeners_mutex:
            for listener in self._listeners:
                # noinspection PyBroadException
                try:
                    listener(self.current_data)
                except Exception:
                    log.error("Exception in FritzBox listener.", exc_info=True)
