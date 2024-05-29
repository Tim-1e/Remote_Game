import threading
from threading import Lock
lock = Lock()

class A():
    def __init__(self):
        self.a = 0
    def update(self):
        with lock:
            self.a += 1
    def print(self):
        with lock:
            print(self.a)
            
    def thread1(self):
        for i in range(10000):
            self.update()
            self.print()

    def start(self):
        t1 = threading.Thread(target = self.thread1)
        t1.start()
        self.thread1()
        
a = A()
a.start()