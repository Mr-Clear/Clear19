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

# if __name__ == '__main__':
#     try:
#         lg19 = G19()
#         lg19.start_event_handling()
#         while True:
#             time.sleep(10)
#     except KeyboardInterrupt:
#         lg19.stop_event_handling()
