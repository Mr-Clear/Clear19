import logging

from clear19.App import Global
from clear19.App.screens import Screens
from clear19.logitech.g19 import G19Key, DisplayKey
from clear19.widgets import Rectangle, Anchor
from clear19.widgets.color import Color
from clear19.widgets.geometry import Size, Point
from clear19.widgets.media_player_widgets import MediaPlayerTrackTitleWidget, MediaPlayerTrackPositionWidget, \
    MediaPlayerTrackDurationWidget, MediaPlayerTrackRemainingWidget, MediaPlayerNameWidget, MediaPlayerAlbumArt, \
    MediaPlayerTrackDetailsWidget
from clear19.widgets.text_widget import TextWidget, Font
from clear19.widgets.widget import Screen, AppWidget

log = logging.getLogger(__name__)


class PlayerScreen(Screen):
    def __init__(self, parent: AppWidget):
        super().__init__(parent, "Time")

        self.background = None

        self.album_art = MediaPlayerAlbumArt(self, Global.media_player, overlay_color=Color(0, 0, 0, 0.5))
        self.album_art.background = Color.BLACK
        self.album_art.foreground = Color.BLACK
        self.album_art.rectangle = self.rectangle

        self.title = MediaPlayerNameWidget(self, Global.media_player)
        self.title.rectangle = Rectangle(self.rectangle.position(Anchor.TOP_LEFT),
                                         Size(self.size.width, self.title.font.font_extents().height))

        self.track_title = MediaPlayerTrackTitleWidget(self, Global.media_player, Font(size=14))
        self.track_title.rectangle = Rectangle(self.rectangle.position(Anchor.BOTTOM_LEFT).anchored(Anchor.BOTTOM_LEFT),
                                               Size(self.width, self.track_title.font.font_extents().height))

        track_position_font = Font(size=11, bold=True)
        self.track_position = MediaPlayerTrackPositionWidget(self, Global.media_player, track_position_font)
        self.track_position.rectangle = Rectangle(
            self.track_title.position(Anchor.TOP_LEFT).anchored(Anchor.BOTTOM_LEFT)
            + Point(0, 2),
            Size(self.width / 3, self.track_position.font.font_extents().height))

        self.track_duration = MediaPlayerTrackDurationWidget(self, Global.media_player, track_position_font)
        self.track_duration.rectangle = Rectangle(
            self.track_title.position(Anchor.TOP_CENTER).anchored(Anchor.BOTTOM_CENTER)
            + Point(0, 2),
            Size(self.width / 3, self.track_duration.font.font_extents().height))
        self.track_duration.h_alignment = TextWidget.HAlignment.CENTER

        self.track_remaining = MediaPlayerTrackRemainingWidget(self, Global.media_player, track_position_font)
        self.track_remaining.rectangle = Rectangle(
            self.track_title.position(Anchor.TOP_RIGHT).anchored(Anchor.BOTTOM_RIGHT)
            + Point(0, 2),
            Size(self.width / 3, self.track_remaining.font.font_extents().height))
        self.track_remaining.h_alignment = TextWidget.HAlignment.RIGHT

        self.track_details = MediaPlayerTrackDetailsWidget(self, Global.media_player, Font(size=10, line_spacing=1, word_wrap=True))
        self.track_details.rectangle = Rectangle(self.title.position(Anchor.BOTTOM_LEFT).anchored(Anchor.TOP_LEFT)
                                                 + Point(0, 10),
                                                 self.track_remaining.position(Anchor.TOP_RIGHT))


    def on_key_down(self, key: G19Key):
        if super().on_key_down(key):
            return True
        if key == DisplayKey.LEFT:
            self.app.current_screen = Screens.MAIN
            return True

