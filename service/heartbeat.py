import os
import time
import threading

counter = 10


def beat():
    global counter
    counter = 10


def timing():
    global counter
    while True:
        time.sleep(1)
        print('beating', counter)
        counter -= 1
        if counter == 0:
            os.abort()


threading.Thread(target=timing).start()