from py4js import Server
from gevent import monkey
monkey.patch_all()

print('server start')
Server(server='gevent', port=80).run()
