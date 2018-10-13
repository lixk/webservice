import os
import time

import psutil


def monitor(pid):
    while psutil.pid_exists(pid):
        time.sleep(1)
    os._exit(0)
