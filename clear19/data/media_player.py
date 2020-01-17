import datetime
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import Thread, Lock
from typing import Dict, Optional, Callable, List

import dbus
from _dbus_glib_bindings import DBusGMainLoop
from dbus import Bus
from dbus.mainloop import NativeMainLoop
from dbus.proxies import ProxyObject
from gi.repository import GLib

from clear19.widgets.widget import AppWidget


@dataclass
class Track:
    duration: float  # In seconds
    title: str
    track_number: int
    album: str
    album_art_url: str
    disc_number: int
    artist: str
    rating: float


@dataclass()
class KnownPosition:
    position: float  # In seconds
    time: datetime

    def current_position(self):
        past = datetime.now() - self.time
        return self.position + past.seconds + past.microseconds / 1000000


@dataclass()
class PlayState:
    track: Track
    playing: bool


class MediaPlayer:
    _listeners: List[Callable[[PlayState], None]]
    _listeners_mutex: Lock

    _session_bus_loop: NativeMainLoop
    _session_bus: Bus

    _current_conn: Optional[ProxyObject] = None
    _connected_conns: List[ProxyObject]
    _conn_names: Dict[str, str]
    _current_player_name: Optional[str] = None

    _current_track: Optional[Track] = None
    _playing: bool = None
    _position: Optional[KnownPosition] = None

    def __init__(self, app: AppWidget):
        self._listeners = []
        self._listeners_mutex = Lock()

        self._conn_names = {}

        self._session_bus_loop = DBusGMainLoop(set_as_default=True)
        self._session_bus = dbus.SessionBus()

        self._connected_conns = []
        self._read_current_status()

        loop = GLib.MainLoop()
        # noinspection PyUnresolvedReferences
        Thread(target=loop.run, daemon=True).start()

        app.scheduler.schedule_synchronous(timedelta(seconds=1), self._update_connections)

    def _update_connections(self, _):
        self._get_connection()

    def _get_connection(self) -> Optional[ProxyObject]:
        conns = []
        for conn_name in self._session_bus.list_names():
            if re.match('org.mpris.MediaPlayer2.', conn_name):
                conn = self._session_bus.get_object(conn_name, "/org/mpris/MediaPlayer2")
                conns.append(conn)
                self._conn_names[conn.bus_name] = conn_name[23:]

        if not conns:
            connection = None

        elif len(conns) == 1:
            connection = conns[0]

        else:
            playing_conns = []
            for conn in conns:
                playing = str(conn.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus',
                                       dbus_interface='org.freedesktop.DBus.Properties')) == 'Playing'
                if playing:
                    playing_conns.append(conn)

            if playing_conns:
                conns = playing_conns

            if self._current_conn and self._current_conn.bus_name in map(lambda b: b.bus_name, conns):
                connection = self._current_conn
            else:
                connection = conns[0]

        if not self.comp_conns(self._current_conn, connection):
            self._current_conn = connection
            if connection and connection.bus_name not in map(lambda b: b.bus_name, self._connected_conns):
                connection.connect_to_signal("PropertiesChanged", self._handle_properties_changed)
                self._connected_conns.append(connection)
            self._read_current_status(connection)

        return connection

    @staticmethod
    def comp_conns(a: ProxyObject, b: ProxyObject):
        if not a and not b:
            return True
        if a and not b or b and not a:
            return False
        return a.bus_name == b.bus_name

    def _read_current_status(self, conn: ProxyObject = None, data: Optional[dbus.Dictionary] = None) -> Optional[Track]:
        metadata = None
        play_state = None
        position = None
        if data and 'Metadata' in data:
            metadata = data['Metadata']
        if data and 'PlaybackStatus' in data:
            play_state = str(data['PlaybackStatus']) == 'Playing'
        if data and 'Position' in data:
            position = float(data['Position']) / 1000000

        if not metadata or not play_state:
            if not conn:
                conn = self._get_connection()
            if conn:
                props_iface = dbus.Interface(conn, dbus_interface='org.freedesktop.DBus.Properties')
                if not metadata:
                    metadata = props_iface.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
                if not play_state:
                    play_state = str(props_iface.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')) == 'Playing'
                if not position:
                    position = float(props_iface.Get('org.mpris.MediaPlayer2.Player', 'Position')) / 1000000

        self.current_track = self._read_metadata(metadata)
        self._set_playing(play_state)
        if position:
            self._position = KnownPosition(position, datetime.now())
        return self.current_track

    @staticmethod
    def _read_metadata(metadata: Optional[Dict]) -> Optional[Track]:
        if not metadata:
            return None

        return Track(float(metadata['mpris:length']) / 1000000 if 'mpris:length' in metadata else None,
                     str(metadata['xesam:title']) if 'xesam:title' in metadata else None,
                     int(metadata['xesam:trackNumber']) if 'xesam:trackNumber' in metadata else None,
                     str(metadata['xesam:album']) if 'xesam:album' in metadata else None,
                     str(metadata['mpris:artUrl']) if 'mpris:artUrl' in metadata else None,
                     int(metadata['xesam:discNumber']) if 'xesam:discNumber' in metadata else None,
                     str(metadata['xesam:artist'][0]) if 'xesam:artist' in metadata else None,
                     float(metadata['xesam:autoRating']) if 'xesam:autoRating' in metadata else None)

    def _handle_properties_changed(self, _, data, _3):
        self._read_current_status(data=data)

    def add_listener(self, listener: Callable[[PlayState], None]):
        with self._listeners_mutex:
            self._listeners.append(listener)

    def _notify_listeners(self):
        with self._listeners_mutex:
            current_state = self.current_play_state
            for listener in self._listeners:
                try:
                    listener(current_state)
                except Exception as e:
                    logging.error("Exception in play state listener: {}".format(e))

    @property
    def current_track(self) -> Track:
        return self._current_track

    @current_track.setter
    def current_track(self, current_track: Track):
        if self._current_track != current_track:
            self._current_track = current_track
            logging.info("Current track: {}".format(current_track))
            self._position = KnownPosition(0, datetime.now())
            self._notify_listeners()

    @property
    def playing(self) -> bool:
        return self._playing

    def _set_playing(self, playing: bool):
        if self._playing != playing:
            self._position = KnownPosition(self.current_position, datetime.now())
            self._playing = playing
            logging.info("Playing" if playing else "Stopped")
            self._notify_listeners()

    @property
    def current_play_state(self) -> PlayState:
        return PlayState(self.current_track, self.playing)

    @property
    def current_position(self) -> float:
        if not self._position:
            return 0
        if self.playing:
            return self._position.current_position()
        else:
            return self._position.position

    @property
    def current_player_name(self) -> Optional[str]:
        if self._current_conn:
            return self._conn_names[self._current_conn.bus_name]
        return None
