import subprocess
from datetime import datetime


def uptime() -> datetime:
    uptime = subprocess.run(['uptime', '-s'], stdout=subprocess.PIPE)
    return datetime.strptime(uptime.stdout.decode('latin1').rstrip(), '%Y-%m-%d %H:%M:%S')
