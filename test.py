import threading
import time

from client import Client
from server import Server

def Server_begin():
    server = Server('127.0.0.1', 12347)
    server.listen()
    server.start()

def Client_begin():
    client = Client('127.0.0.1', 12347)
    client.start()

#利用多线程同时启动客户端和服务端
thread_server = threading.Thread(target=Server_begin, args=(''))
thread_server.start()

time.sleep(1)


thread_client = threading.Thread(target=Client_begin, args=(''))
thread_client.start()

