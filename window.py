import os
import subprocess
import threading
import time

import psutil

import netutil
import server


class Window:
    def __init__(self, args, port):
        self.args = ' '.join(args)
        self.port = netutil.get_available_port(default_port=port)

    def server_callback(self):
        while True:
            time.sleep(0.5)
            if netutil.is_port_used('localhost', self.port):
                pid = subprocess.Popen(self.args).pid
                while psutil.pid_exists(pid):
                    time.sleep(1)
                os._exit(0)

    def start(self):
        threading.Thread(target=self.server_callback).start()
        server.start(self.port)


if __name__ == '__main__':
    window = Window(server.CONFIG['window-config']['args'], server.PORT)
    window.start()
