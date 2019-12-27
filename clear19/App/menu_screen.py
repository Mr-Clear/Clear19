from clear19.widgets.menu_widget import MenuWidget, MenuWidgetEntry
from clear19.widgets.text_widget import Font
from clear19.widgets.widget import Screen, AppWidget


class MenuScreen(Screen):
    def __init__(self, parent: AppWidget):
        super().__init__(parent, "Menu")

        m = MenuWidget(self, [MenuWidgetEntry("Exit", lambda _: self.app.exit())], Font())
        m.rectangle = self.rectangle
        self.children.append(m)
