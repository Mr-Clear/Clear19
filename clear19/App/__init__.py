import subprocess
from datetime import datetime
from pathlib import Path

from clear19.data.download_manager import DownloadManager


class Global:
    download_manager: DownloadManager


def uptime() -> datetime:
    uptime = subprocess.run(['uptime', '-s'], stdout=subprocess.PIPE)
    return datetime.strptime(uptime.stdout.decode('latin1').rstrip(), '%Y-%m-%d %H:%M:%S')


Global.download_manager = DownloadManager(Path.home().joinpath('.cache/clear/clear19'))
