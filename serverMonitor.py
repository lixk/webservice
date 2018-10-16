import os
import socket
import threading
import time

import psutil
from urllib import request

HOST = '127.0.0.1'
PORT = 80


# server startup callback function
def _on_server_startup():
    while True:
        url = 'http://%s:%s/view/index.html' % (HOST, PORT)
        try:
            r = request.urlopen(url)
            print(r)
            break
        except OSError:
            time.sleep(0.1)

    import subprocess
    args = '''bin/easy-window.exe 
    -url %s 
    -title 哈哈哈 
    -icon bin/favicon.ico''' % url
    pid = subprocess.Popen(args).pid
    while psutil.pid_exists(pid):
        time.sleep(1)
    # exit
    os._exit(0)


def monitor():
    """
    server startup monitor

    :return:
    """
    threading.Thread(target=_on_server_startup).start()
