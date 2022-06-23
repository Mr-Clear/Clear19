import logging

from _cffi_backend import buffer

from clear19.widgets.geometry import Size

log = logging.getLogger(__name__)


# noinspection PyMethodMayBeStatic
class G19Simulator:
    def __init__(self):
        self.image_size = Size(320, 240)

    def reset(self):
        log.info("Reset")

    def send_frame(self, data: buffer):
        pass

    def read_g_and_m_keys(self, _=None):
        return []

    def read_display_menu_keys(self):
        return []
