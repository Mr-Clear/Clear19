#!/usr/bin/env python3
import locale
import logging
import os
import sys
import traceback
from typing import Optional

from clear19.App.app import App

logging.basicConfig(format="%(asctime)s [%(levelname)-8s] %(message)s", level=logging.DEBUG, force=True)
locale.setlocale(locale.LC_ALL, ('de_DE', 'UTF-8'))

if __name__ == "__main__":
    logging.info("START")
    # noinspection PyBroadException
    app: Optional[App] = None
    try:
        app = App()
    except Exception as e:
        logging.critical("Exception in App\n{}".format(''.join(traceback.format_exception(None, e, e.__traceback__))))
        os._exit(os.EX_SOFTWARE)
    logging.info("END")
    sys.exit(app.exit_code)
