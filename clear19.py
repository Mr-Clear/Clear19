#!/usr/bin/env python3
import locale
import logging
import os
import shutil
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional

import haggis.logs

from clear19.App.app import App
from clear19.data import Config

log = logging.getLogger(__name__)

rootLogger = logging.getLogger()
for h in rootLogger.handlers[:]:
    rootLogger.removeHandler(h)
    h.close()

logFormatter = logging.Formatter('%(asctime)s [%(name)-24.24s] [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s')
rootLogger.setLevel(logging.DEBUG)

logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

Path("logs").mkdir(exist_ok=True)
fileHandler = logging.FileHandler(f"logs/{datetime.now().isoformat()}.log")
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

if __name__ == "__main__":
    log.info("START")

    haggis.logs.add_logging_level('TRACE', 2)
    haggis.logs.add_logging_level('VERBOSE', 5)
    haggis.logs.add_logging_level('FATAL', 60, if_exists=haggis.logs.OVERWRITE)
    haggis.logs.add_logging_level('WTF', 70)
    haggis.logs.add_logging_level('PRINT', 80)

    if not os.path.exists('clear19.ini'):
        log.warning("No settings file found. Restore from default settings file.")
        shutil.copyfile('clear19.default.ini', 'clear19.ini')

    locale.setlocale(locale.LC_ALL, (Config.locale(), 'UTF-8'))

    app: Optional[App] = None
    try:
        app = App()
    except Exception as e:
        log.fatal(f"Exception in App\n{''.join(traceback.format_exception(None, e, e.__traceback__))}")
        os._exit(os.EX_SOFTWARE)
    log.info("END")
    sys.exit(app.exit_code)
