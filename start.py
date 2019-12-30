#!/usr/bin/env python3
import logging
import os

import sys
import traceback

from clear19.App.app import App, app_exit_code

if __name__ == "__main__":
    logging.info("START")
    # noinspection PyBroadException
    try:
        App()
    except Exception as e:
        logging.critical("Exception in App\n{}".format(''.join(traceback.format_exception(None, e, e.__traceback__))))
        logging.critical("Exception in App\n{}".format(''.join(traceback.format_exception(None, e, e.__traceback__))))
        os._exit(os.EX_SOFTWARE)
    logging.info("END")
    sys.exit(app_exit_code)
