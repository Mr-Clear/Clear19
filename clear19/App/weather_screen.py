import logging
from datetime import timedelta
from typing import Optional

from clear19.App import Global
from clear19.App.screens import Screens
from clear19.data import Config
from clear19.data.wetter_com import WetterCom, WeatherData
from clear19.logitech.g19 import G19Key, DisplayKey
from clear19.widgets.geometry import VAnchor
from clear19.widgets.text_widget import TextWidget
from clear19.widgets.widget import Screen, AppWidget

log = logging.getLogger(__name__)


class WeatherScreen(Screen):
    def __init__(self, parent: AppWidget):
        super().__init__(parent, "Time")

        self.wetter_com = WetterCom(Config.Weather.city_code(), Global.download_manager)

        self.title = TextWidget(self, "Wetter", h_alignment=TextWidget.HAlignment.CENTER)
        self.title.rectangle = self.rectangle
        self.title.set_height(30, VAnchor.TOP)
        self.title.fit_font_size()

        self.load_weather()
        self.app.scheduler.schedule_synchronous(timedelta(minutes=10), self.load_weather)

    def on_key_down(self, key: G19Key):
        if super().on_key_down(key):
            return True
        if key == DisplayKey.UP:
            self.app.current_screen = Screens.MAIN
            return True

    def load_weather(self, _=None):
        data = self.wetter_com.load_weather(self.read_weather)
        if data:
            self.read_weather(data)

    def read_weather(self, data: Optional[WeatherData] = None):
        if data:
            self.title.text = data.location
            self.title.fit_font_size()
