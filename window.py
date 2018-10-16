import os
import threading
import time
from urllib import request

import psutil


class Window:
    def __init__(self):
        self.url = None
        self.thread = None

    def _on_server_startup(self):
        while True:
            try:
                request.urlopen(self.url)
                break
            except OSError as e:
                print(e)
                time.sleep(0.1)
        self._callback()

    def listen(self, url):
        self.url = url
        if not self.thread:
            self.thread = threading.Thread(target=self._on_server_startup)
            self.thread.start()

    @staticmethod
    def _callback():
        """
        server startup callback function

        :return:
        """
        import subprocess
        args = ['bin/easy-window.exe',
                '-url view/index.html',
                '-title 哈哈哈',
                '-icon bin/favicon.ico',
                '-timeout 6000']
        pid = subprocess.Popen(' '.join(args)).pid
        while psutil.pid_exists(pid):
            time.sleep(1)
        # exit
        os._exit(0)
