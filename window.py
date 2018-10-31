import os
import subprocess
import threading
import time
from urllib import request

import psutil
from py4js import Server


class Window:
    def __init__(self, url='index.html', title='form', icon='', width=800, height=600, border=True, layered=False):
        self.__form = 'easy-window.exe'
        self.args = []
        self.args.append(self.__form)

        self.args.append('-url %s' % url)
        self.args.append('-title %s' % title)
        self.args.append('-icon %s' % icon)
        self.args.append('-width %s' % width)
        self.args.append('-height %s' % height)
        self.args.append('-border %s' % ('true' if border else 'false'))
        self.args.append('-layered %s' % ('true' if layered else 'false'))

        self.__view_path = os.path.splitdrive(url)[0]
        self.__view_path = self.__view_path if os.path.isdir(self.__view_path) else './'
        self.__js_path = os.path.join(self.__view_path, 'service.js')

        self.server = Server(port=None)

    def server_callback(self):
        while True:
            time.sleep(0.5)
            try:
                js = request.urlopen('http://127.0.0.1:%s%s' % (self.server.port, self.server.js_route)).read().decode('utf-8')
                with open(self.__js_path, 'w', encoding='utf-8') as f:
                    f.write(js)
                pid = subprocess.Popen(' '.join(self.args)).pid
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
                self.server = Server(port=None)
                print(e)


if __name__ == '__main__':
    import yaml

    config = yaml.load(open('config.yml', 'r', encoding='utf-8'))
    # Window(config['args']).start()
    print(os.path.isdir('http://view/a/'), os.path.split('http://view/a/index.html'))
    Window(url='view/index.html', title='窗口',width=200).start()