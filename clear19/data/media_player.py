import datetime
import logging
from dataclasses import dataclass
from datetime import datetime
from pprint import pp
from threading import Thread, Lock
from typing import Dict, Optional, Callable, List

import dbus
from _dbus_glib_bindings import DBusGMainLoop
from dbus import Bus
from dbus.mainloop import NativeMainLoop
from gi.repository import GLib


@dataclass
class Track:
    length: int  # In nanoseconds
    title: str
    track_number: int
    album: str
    album_art_url: str
    disc_number: int
    artist: str
    rating: float


@dataclass()
class KnownPosition:
    position: int  # In nanoseconds
    time: datetime

    def current_position(self):
        return self.position + (datetime.now() - self.time).microseconds * 1000


@dataclass()
class PlayState:
    track: Track
    playing: bool


class MediaPlayer:
    _listeners: List[Callable[[PlayState], None]]
    _listeners_mutex: Lock

    _session_bus_loop: NativeMainLoop
    _session_bus: Bus
    _conn_spotify: dbus.proxies.ProxyObject

    _current_track: Optional[Track] = None
    _playing: bool = None
    _position: Optional[KnownPosition]

    def __init__(self):
        self._listeners = []
        self._listeners_mutex = Lock()

        self._session_bus_loop = DBusGMainLoop(set_as_default=True)
        self._session_bus = dbus.SessionBus()

        self._conn_spotify = self._session_bus.get_object("org.mpris.MediaPlayer2.spotify",
                                                          "/org/mpris/MediaPlayer2")
        self._conn_spotify.connect_to_signal("PropertiesChanged", self.handle_properties_changed)
        self._read_current_status()

        loop = GLib.MainLoop()
        # noinspection PyUnresolvedReferences
        Thread(target=loop.run, daemon=True).start()
        logging.debug("Loop started.")

    def _read_current_status(self) -> Track:
        props_iface = dbus.Interface(self._conn_spotify, dbus_interface='org.freedesktop.DBus.Properties')
        self.current_track = self._read_metadata(props_iface.Get('org.mpris.MediaPlayer2.Player', 'Metadata'))
        self.playing = str(props_iface.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')) == 'Playing'
        return self.current_track

    @staticmethod
    def _read_metadata(metadata: Dict) -> Track:
        return Track(int(metadata['mpris:length']) if 'mpris:length' in metadata else None,
                     str(metadata['xesam:title']) if 'xesam:title' in metadata else None,
                     int(metadata['xesam:trackNumber']) if 'xesam:trackNumber' in metadata else None,
                     str(metadata['xesam:album']) if 'xesam:album' in metadata else None,
                     str(metadata['mpris:artUrl']) if 'mpris:artUrl' in metadata else None,
                     int(metadata['xesam:discNumber']) if 'xesam:discNumber' in metadata else None,
                     str(metadata['xesam:artist'][0]) if 'xesam:artist' in metadata else None,
                     float(metadata['xesam:autoRating']) if 'xesam:autoRating' in metadata else None)

    # noinspection PyMethodMayBeStatic
    def handle_properties_changed(self, _, changed_props: Dict, _2):
        if 'Metadata' in changed_props:
            metadata = changed_props['Metadata']
            self.current_track = self._read_metadata(metadata)
            position = int(changed_props['Position']) if 'Position' in changed_props else 0
            self._position = KnownPosition(position, datetime.now())
            changed_props.pop('Metadata', None)
        if 'PlaybackStatus' in changed_props:
            self._position = KnownPosition(self.current_position, datetime.now())
            self.playing = str(changed_props['PlaybackStatus']) == 'Playing'
            changed_props.pop('PlaybackStatus', None)
        if 'Position' in changed_props:
            self._position = KnownPosition(int(changed_props['Position']), datetime.now())
            changed_props.pop('Position', None)

        changed_props.pop('CanPlay', None)
        changed_props.pop('CanPause', None)

        if changed_props:
            pp(changed_props)

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
            self._notify_listeners()

    @property
    def playing(self) -> bool:
        return self._playing

    @playing.setter
    def playing(self, playing: bool):
        if self._playing != playing:
            self._playing = playing
            logging.info("Playing" if playing else "Stopped")
            self._notify_listeners()

    @property
    def current_play_state(self) -> PlayState:
        return PlayState(self.current_track, self.playing)

    @property
    def current_position(self) -> int:
        if not self._position:
            return 0
        if self.playing:
            return self._position.current_position()
        else:
            return self._position.position
