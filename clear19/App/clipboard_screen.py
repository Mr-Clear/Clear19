import logging

from PyQt5.QtWidgets import QApplication

from clear19.App.screens import Screens
from clear19.logitech.g19 import G19Key, DisplayKey
from clear19.widgets.geometry import VAnchor
from clear19.widgets.text_widget import TextWidget, Font
from clear19.widgets.widget import Screen, AppWidget

log = logging.getLogger(__name__)


class ClipboardScreen(Screen):
    def __init__(self, parent: AppWidget):
        super().__init__(parent, "Time")

        #self.application = QApplication(list())
        self.title = TextWidget(self, "ClipboardText", h_alignment=TextWidget.HAlignment.LEFT, font=Font(size=8))
        self.title.rectangle = self.rectangle
        #clipboard = QApplication.clipboard()
        #if clipboard:
        #    QApplication.clipboard().dataChanged.connect(self.clipboard_changed)
        #else:
        #    log.print(type(clipboard))

    def on_key_down(self, key: G19Key):
        if super().on_key_down(key):
            return True
        if key == DisplayKey.RIGHT:
            self.app.current_screen = Screens.MAIN
            return True
        #clipboard = QApplication.clipboard()
        #if clipboard:
        #    self.title.text = clipboard.text()

    def clipboard_changed(self):
        clipboard = QApplication.clipboard()
        if clipboard:
            self.title.text = clipboard.text()

