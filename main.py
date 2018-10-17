import socket
import threading
import time
import webbrowser

from bottle import Bottle

app = Bottle()


@app.route('/')
def index():
    return 'Hello Bottle!'


def open_browser():
    while True:
        try:
            sk = socket.socket()
            sk.connect(('127.0.0.1', 80))
            sk.close()
            break
        except ConnectionError:
            time.sleep(0.5)
    webbrowser.open('127.0.0.1')


# threading.Thread(target=open_browser).start()
# app.run(host='0.0.0.0', port=8000)
import inspect
print(inspect.getfullargspec(index).args + ['success', 'error'])
print(inspect.getdoc(index))
