#!/usr/bin/python
# coding: utf-8
"""Userspace driver"""

import logging
import time
import signal
from appmgr import AppMgr

APP_MGR = AppMgr()


def shutdown():
    """SIGTERM/SIGHUP callback"""
    logging.info("SIG shutdown")
    APP_MGR.shutdown()
    exit()


def main():
    """Main"""

    logging.basicConfig(level=logging.DEBUG)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGHUP, shutdown)

    time.sleep(1)
    APP_MGR.routine()


if __name__ == '__main__':
    main()
