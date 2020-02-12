#!/usr/bin/env python3
import locale
import logging
import os
import shutil
import sys
import traceback
from typing import Optional

from clear19.App.app import App
from clear19.data import Config

logging.basicConfig(format='%(asctime)s [%(levelname)-8s] %(message)s', level=logging.DEBUG, force=True)

if __name__ == "__main__":
    logging.info("START")

    if not os.path.exists('clear19.ini'):
        logging.warning("No settings file found. Restore from default settings file.")
        shutil.copyfile('clear19.default.ini', 'clear19.ini')

    locale.setlocale(locale.LC_ALL, (Config.locale(), 'UTF-8'))

    app: Optional[App] = None
    try:
        app = App()
    except Exception as e:
        logging.critical(f"Exception in App\n{''.join(traceback.format_exception(None, e, e.__traceback__))}")
        os._exit(os.EX_SOFTWARE)
    logging.info("END")
    sys.exit(app.exit_code)
