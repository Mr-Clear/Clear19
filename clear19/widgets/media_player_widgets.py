from abc import ABCMeta, ABC
from datetime import timedelta

from clear19.data.media_player import MediaPlayer, Track, PlayState
from clear19.scheduler import TaskParameters
from clear19.widgets.geometry import Size, Rectangle, ZERO_TOP_LEFT
from clear19.widgets.text_widget import TextWidget, Font
from clear19.widgets.widget import ContainerWidget, Widget


class MediaPlayerWidget(Widget, ABC):
    __metaclass__ = ABCMeta

    _media_player: MediaPlayer

    def __init__(self, parent: ContainerWidget, media_player: MediaPlayer):
        super().__init__(parent)
        self._media_player = media_player

    @property
    def media_player(self) -> MediaPlayer:
        return self._media_player


class MediaPlayerTrackTitleWidget(MediaPlayerWidget, ContainerWidget):
    _font: Font
    _unselected: TextWidget

    def __init__(self, parent: ContainerWidget, media_player: MediaPlayer, font: Font = Font()):
        super().__init__(parent, media_player)
        self._font = font
        self._unselected = TextWidget(self, self.shorten_title(media_player.current_track, font, self.size), font)
        self._unselected.rectangle = Rectangle(ZERO_TOP_LEFT, self.size)
        self.children.append(self._unselected)
        self._update_play_state(self.media_player.current_play_state)
        self.media_player.add_listener(self._update_play_state)

    @staticmethod
    def shorten_title(track: Track, font: Font, space: Size) -> str:
        title = "{} - {} - {}".format(track.artist, track.album, track.title)
        return title

    def _update_play_state(self, play_state: PlayState):
        self._unselected.text = self.shorten_title(play_state.track, self._font, self.size)

    @property
    def font(self) -> Font:
        return self._font

    @font.setter
    def font(self, font: Font):
        if self._font != font:
            self._font = font
            self.dirty = True


def format_position(position: float):
    minutes, seconds = divmod(position, 60)
    return "{:02.0f}:{:02.0f}".format(minutes, seconds)


class MediaPlayerTrackPositionWidget(MediaPlayerWidget, TextWidget):
    def __init__(self, parent: ContainerWidget, media_player: MediaPlayer, font: Font = Font()):
        MediaPlayerWidget.__init__(self, parent, media_player)
        TextWidget.__init__(self, parent, "--:--", font)
        self.app.scheduler.schedule_synchronous(timedelta(milliseconds=100), self._update_play_state, priority=90)

    def _update_play_state(self, _: TaskParameters):
        self.text = format_position(self.media_player.current_position)


class MediaPlayerTrackRemainingWidget(MediaPlayerWidget, TextWidget):
    def __init__(self, parent: ContainerWidget, media_player: MediaPlayer, font: Font = Font()):
        MediaPlayerWidget.__init__(self, parent, media_player)
        TextWidget.__init__(self, parent, "--:--", font)
        self.app.scheduler.schedule_synchronous(timedelta(milliseconds=100), self._update_play_state, priority=90)

    def _update_play_state(self, _: TaskParameters):
        self.text = "-" + format_position(self.media_player.current_track.duration - self.media_player.current_position)


class MediaPlayerTrackDurationWidget(MediaPlayerWidget, TextWidget):
    def __init__(self, parent: ContainerWidget, media_player: MediaPlayer, font: Font = Font()):
        MediaPlayerWidget.__init__(self, parent, media_player)
        TextWidget.__init__(self, parent, "--:--", font)
        self.media_player.add_listener(self._update_play_state)
        self._update_play_state(self.media_player.current_play_state)

    def _update_play_state(self, play_state: PlayState):
        self.text = format_position(play_state.track.duration)
