import os
import time
import threading

counter = 20


def beat():
    global counter
    counter = 10


def count_down():
    global counter
    while True:
        time.sleep(1)
        print('beating', counter)
        counter -= 1
        if counter == 0:
            os._exit(0)


threading.Thread(target=count_down).start()