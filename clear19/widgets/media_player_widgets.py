import logging
from abc import ABCMeta, ABC
from dataclasses import replace
from datetime import timedelta
from typing import Optional

from cairo import Context

from clear19.App import Global
from clear19.data.media_player import MediaPlayer, Track, PlayState
from clear19.scheduler import TaskParameters
from clear19.widgets.color import Color
from clear19.widgets.geometry import Size, Rectangle, ZERO_TOP_LEFT, Anchor
from clear19.widgets.image_widget import ImageWidget
from clear19.widgets.text_widget import TextWidget, Font
from clear19.widgets.widget import ContainerWidget, Widget

log = logging.getLogger(__name__)

"""
Widgets that display information of media players.
"""


class MediaPlayerWidget(Widget, ABC):
    """
    Base class for all media player widgets.
    """
    __metaclass__ = ABCMeta

    _media_player: MediaPlayer

    def __init__(self, parent: ContainerWidget, media_player: MediaPlayer):
        super().__init__(parent)
        self._media_player = media_player

    @property
    def media_player(self) -> MediaPlayer:
        return self._media_player


class MediaPlayerNameWidget(MediaPlayerWidget, TextWidget):
    """
    Text widget that shows the name of the current player.
    """
    def __init__(self, parent: ContainerWidget, media_player: MediaPlayer, font: Font = Font()):
        MediaPlayerWidget.__init__(self, parent, media_player)
        TextWidget.__init__(self, parent, font=font)
        self.app.scheduler.schedule_synchronous(timedelta(milliseconds=100), self._update_play_state, priority=90)

    def _update_play_state(self, _: TaskParameters):
        self.text = f'Player: {self.media_player.current_player_name}'


class MediaPlayerTrackTitleWidget(MediaPlayerWidget, ContainerWidget):
    """
    Shows the current track title and the progress.
    """
    _font: Font
    _unselected: TextWidget
    _selected: TextWidget
    _progress: float = 0

    def __init__(self, parent: ContainerWidget, media_player: MediaPlayer, font: Font = Font()):
        super().__init__(parent, media_player)
        self._font = font
        self._unselected = TextWidget(self, "", font)
        self._selected = TextWidget(self, "", font)
        self._selected.background = Color.BLUE * 1.5
        self._update_play_state(self.media_player.current_play_state)
        self.media_player.add_listener(self._update_play_state)
        self.app.scheduler.schedule_synchronous(timedelta(milliseconds=100), self._update_position, priority=90)

    def do_layout(self):
        self._unselected.rectangle = Rectangle(ZERO_TOP_LEFT, self.size)
        self._selected.rectangle = Rectangle(ZERO_TOP_LEFT, self.size)
        self._update_play_state(self.media_player.current_play_state)

    # noinspection PyUnusedLocal
    def shorten_title(self, track: Track, font: Font, space: Size) -> str:
        player = self.media_player.current_player_name
        if player == 'spotify':
            parts = [track.artist, track.album, track.title, ' - ']
            parts_width = list(map(lambda t: font.text_extents(t).width, parts))
            combinations = [[0, 3, 1, 3, 2], # artist - album - title
                            [0, 3, 2],       # artist - title
                            [2]]             # title
            combinations_width = list(map(lambda c: sum(map(lambda i: parts_width[i], c)), combinations))
            combination = next((i for i in range(len(combinations)) if combinations_width[i] <= space.width), len(combinations) - 1)
            title = ''.join(map(lambda i: parts[i], combinations[combination]))
        else:
            title = f"{track.title}"
        return title

    def _update_play_state(self, play_state: PlayState):
        if play_state.track:
            self._progress = self.media_player.current_position / play_state.track.duration if play_state.track.duration and play_state.track.duration > 0 else 0
            title = self.shorten_title(play_state.track, self._font, self.size)
            font = replace(self._unselected.font, italic=False)
        else:
            self._progress = 0
            font = replace(self._unselected.font, italic=True)
            title = "Not connected"
        self._unselected.font = font
        self._unselected.text = title
        self._selected.font = font
        self._selected.text = title
        self.dirty = True

    def _update_position(self, _: TaskParameters):
        if self.media_player.current_track:
            if self.media_player.current_track.duration:
                self._progress = self.media_player.current_position / self.media_player.current_track.duration
            else:
                self._progress = 0
        else:
            self._progress = 0

    @property
    def font(self) -> Font:
        return self._font

    @font.setter
    def font(self, font: Font):
        if self._font != font:
            self._font = font
            self.dirty = True

    def paint_foreground(self, ctx: Context):
        x1 = self.width * self._progress
        x2 = self.width - x1

        ctx.save()
        ctx.translate(*self._unselected.position(Anchor.TOP_LEFT))
        ctx.rectangle(x1, 0, x2, self.height)
        ctx.clip()
        self._unselected.paint(ctx)
        ctx.restore()

        if self._progress:
            ctx.save()
            ctx.translate(*self._selected.position(Anchor.TOP_LEFT))
            ctx.rectangle(0, 0, x1, self.height)
            ctx.clip()
            self._selected.paint(ctx)
            ctx.restore()

        self.dirty = False


def format_position(position: float):
    """
    :param position: Position in track in seconds.
    :return: Position formatted as %m:%s.
    """
    if position:
        minutes, seconds = divmod(round(position), 60)
        return f"{minutes:02.0f}:{seconds:02.0f}"
    return "--:--"


class MediaPlayerTrackPositionWidget(MediaPlayerWidget, TextWidget):
    """
    Text widget that shows the current position.
    """
    def __init__(self, parent: ContainerWidget, media_player: MediaPlayer, font: Font = Font()):
        MediaPlayerWidget.__init__(self, parent, media_player)
        TextWidget.__init__(self, parent, "--:--", font)
        self.app.scheduler.schedule_synchronous(timedelta(milliseconds=100), self._update_play_state, priority=90)

    def _update_play_state(self, _: TaskParameters):
        if self.media_player.current_track:
            self.text = format_position(self.media_player.current_position)
        else:
            self.text = '--:--'


class MediaPlayerTrackRemainingWidget(MediaPlayerWidget, TextWidget):
    """
    TextWidget that shows the remaining time of the current track.
    """
    def __init__(self, parent: ContainerWidget, media_player: MediaPlayer, font: Font = Font()):
        MediaPlayerWidget.__init__(self, parent, media_player)
        TextWidget.__init__(self, parent, "--:--", font)
        self.app.scheduler.schedule_synchronous(timedelta(milliseconds=100), self._update_play_state, priority=90)

    def _update_play_state(self, _: TaskParameters):
        if self.media_player.current_track:
            self.text = '-' + format_position(self.media_player.current_track.duration
                                              - self.media_player.current_position)
        else:
            self.text = '---:--'


class MediaPlayerTrackDurationWidget(MediaPlayerWidget, TextWidget):
    """
    TextWidget that shows the duration of the current track.
    """
    def __init__(self, parent: ContainerWidget, media_player: MediaPlayer, font: Font = Font()):
        MediaPlayerWidget.__init__(self, parent, media_player)
        TextWidget.__init__(self, parent, "--:--", font)
        self.media_player.add_listener(self._update_play_state)
        self._update_play_state(self.media_player.current_play_state)

    def _update_play_state(self, play_state: PlayState):
        if play_state.track:
            self.text = format_position(play_state.track.duration)
        else:
            self.text = '--:--'


class MediaPlayerTrackDetailsWidget(MediaPlayerWidget, TextWidget):
    """
    TextWidget that shows all known information of the current track.
    """

    def __init__(self, parent: ContainerWidget, media_player: MediaPlayer, font: Font = Font()):
        MediaPlayerWidget.__init__(self, parent, media_player)
        TextWidget.__init__(self, parent, "--:--", font)
        self.media_player.add_listener(self._update_play_state)
        self._update_play_state(self.media_player.current_play_state)

    def _update_play_state(self, play_state: PlayState):
        if play_state.track:
            track = play_state.track
        else:
            track = Track

        self.text = '\n'.join([f'Artist: {track.artist}',
                               f'Album: {track.album}',
                               f'Track: {track.track_number}',
                               f'Title: {track.title}',
                               f'Duration: {track.duration}',
                               f'Rating: {track.rating}'])


class MediaPlayerAlbumArt(MediaPlayerWidget, ImageWidget):
    """
    ImageWidget that shows the album art of the current track.
    """
    _image_url: str = ''

    def __init__(self, parent, media_player, alignment: Anchor = Anchor.CENTER_CENTER, overlay_color: Optional[Color] = None):
        MediaPlayerWidget.__init__(self, parent, media_player)
        ImageWidget.__init__(self, parent, alignment, overlay_color)
        self.media_player.add_listener(self._update_play_state)
        self._update_play_state(self.media_player.current_play_state)

    def _update_play_state(self, play_state: PlayState):
        if play_state.track:
            url = play_state.track.album_art_url
        else:
            url = ''

        if url != self._image_url:
            self.load_image(None)
            self._image_url = url
            if url:
                Global.download_manager.get(url, self.load_image)
