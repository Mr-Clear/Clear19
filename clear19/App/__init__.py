import subprocess
from datetime import datetime
from pathlib import Path

from clear19.data.download_manager import DownloadManager
from clear19.data.media_player import MediaPlayer
from clear19.data.system_data import SystemData
from clear19.scheduler import Scheduler


class Global:
    download_manager: DownloadManager
    media_player: MediaPlayer
    system_data: SystemData

    @staticmethod
    def init(scheduler: Scheduler):
        Global.download_manager = DownloadManager(Path.home().joinpath('.cache/clear/clear19'))
        Global.media_player = MediaPlayer(scheduler)
        Global.system_data = SystemData(scheduler)


def uptime() -> datetime:
    uptime = subprocess.run(['uptime', '-s'], stdout=subprocess.PIPE)
    return datetime.strptime(uptime.stdout.decode('latin1').rstrip(), '%Y-%m-%d %H:%M:%S')
