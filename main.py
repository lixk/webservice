import socket
import time
import webbrowser

from bottle import Bottle, request, route

app = Bottle()


@app.route('/index.html')
def index():
    print(request.path,'-------', request.url,'------------', request.urlparts)
    print(request.urlparts.scheme,
        request.urlparts.netloc)
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
# app.run(host='0.0.0.0', port=8080)
# import inspect
# print(inspect.getfullargspec(index).args + ['success', 'error'])
# print(inspect.getdoc(index))
class Server(Bottle):
    pass

@app.route('/index')
def index(self):
    return 'index'
app.run(port=5000)
# import requests
# print(requests.post('http://localhost:8080/?id=1name=小明').content)