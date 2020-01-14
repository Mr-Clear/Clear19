from clear19.data.media_player import MediaPlayer, Track, PlayState
from clear19.widgets.geometry import Size, Rectangle, ZERO_TOP_LEFT
from clear19.widgets.text_widget import TextWidget, Font
from clear19.widgets.widget import ContainerWidget


class MediaPlayerTrackTitle(ContainerWidget):
    _data: MediaPlayer
    _font: Font
    _unselected: TextWidget

    def __init__(self, parent: ContainerWidget, media_player: MediaPlayer, font: Font = Font()):
        super().__init__(parent)
        self._data = media_player
        self._font = font
        self._unselected = TextWidget(self, self.shorten_title(media_player.current_track, font, self.size), font)
        self._unselected.rectangle = Rectangle(ZERO_TOP_LEFT, self.size)
        self.children.append(self._unselected)
        self._update_play_state(self._data.current_play_state)
        self._data.add_listener(self._update_play_state)

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
