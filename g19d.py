#!/usr/bin/python
# coding: utf-8
"""Userspace driver"""

import time
import signal
from appmgr import AppMgr

APPMGR = AppMgr()


def shutdown(*args):
    """SIGTERM/SIGHUP callback"""
    del args
    print("SIG shutdown")
    APPMGR.shutdown()
    exit()

def main():
    """Main"""

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGHUP, shutdown)

    time.sleep(1)
    APPMGR.routine()

if __name__ == '__main__':
    main()
