import collections
import logging

from clear19.widgets.menu_widget import MenuWidget, MenuWidgetEntry
from clear19.widgets.text_widget import Font
from clear19.widgets.widget import Screen, AppWidget

log = logging.getLogger(__name__)


def set_log_level(level: int):
    log.print(f"Setting log level to {logging.getLevelName(level)} ({level})")
    logging.getLogger().setLevel(level)


class MenuScreen(Screen):
    def __init__(self, parent: AppWidget):
        super().__init__(parent, "Menu")

        self.menu_widget = MenuWidget(self, [MenuWidgetEntry("Exit", lambda _: self.app.exit()),
                                             MenuWidgetEntry("Set Log Level", self._set_log_level)],
                                      Font())
        self.menu_widget.rectangle = self.rectangle

    def _set_log_level(self, _):
        menu = []
        index = 0
        # noinspection PyUnresolvedReferences
        levels = collections.OrderedDict(sorted(logging._levelToName.items()))
        for i, (level, name) in enumerate(levels.items()):
            menu.append(MenuWidgetEntry(name, lambda _, l=level: set_log_level(l)))
            if level == logging.getLogger().getEffectiveLevel():
                index = i
        self.menu_widget.enter_submenu(menu, index)
