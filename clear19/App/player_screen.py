import logging

from clear19.App.screens import Screens
from clear19.logitech.g19 import G19Key, DisplayKey
from clear19.widgets.geometry import VAnchor
from clear19.widgets.text_widget import TextWidget
from clear19.widgets.widget import Screen, AppWidget

log = logging.getLogger(__name__)


class PlayerScreen(Screen):
    def __init__(self, parent: AppWidget):
        super().__init__(parent, "Time")

        self.title = TextWidget(self, "Player", h_alignment=TextWidget.HAlignment.CENTER)
        self.title.rectangle = self.rectangle
        self.title.set_height(30, VAnchor.TOP)
        self.title.fit_font_size()

    def on_key_down(self, key: G19Key):
        if super().on_key_down(key):
            return True
        if key == DisplayKey.LEFT:
            self.app.current_screen = Screens.MAIN
            return True

