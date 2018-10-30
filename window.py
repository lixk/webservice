import os
import subprocess
import threading
import time
from urllib import request

import psutil
from py4js import Server


class Window:
    def __init__(self, args):
        self.args = ' '.join(args)
        self.server = Server(port=None)

    def server_callback(self):
        while True:
            time.sleep(0.5)
            try:
                r = request.urlopen('http://localhost:%s%s' % (self.server.port, self.server.js_route))
                print(r)
                pid = subprocess.Popen(self.args.format(port=self.server.port)).pid
                while psutil.pid_exists(pid):
                    time.sleep(1)
                os._exit(0)
            except Exception as e:
                print(e)

    def start(self):
        threading.Thread(target=self.server_callback).start()
        for i in range(10):
            try:
                self.server.run()
            except Exception as e:
                print(e)


if __name__ == '__main__':
    import yaml

    config = yaml.load(open('config.yml', 'r', encoding='utf-8'))
    # Window(config['args']).start()

    r = subprocess.Popen('python main.py')
    pid = r.pid
    print(pid, r.stdout)