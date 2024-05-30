import socket
import threading
import time
from threading import Lock
from gameObjects import *
from test_all import message

MAX_CLIENT_NUM = 4
fps = 60
physics_fps = 120

lock = Lock()

player_colors = [(83,134,139), (69,139,116), (72,61,139), (139,129,76)]


class Server():
    def __init__(self, host_ip, host_port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host_ip = host_ip
        self.host_port = host_port
        self.is_active = True
        self.temp_id = 5000 # 5000-5003
        self.client_id = dict() # client_socket -> id
        self.tanks = dict() # id -> tank
        self.bullet_pool = BulletPool(MAX_BULLET_NUM)
        self.map = Map()

    def listen(self):
        self.server_socket.bind((self.host_ip, self.host_port))
        self.server_socket.listen(MAX_CLIENT_NUM)
        print("Server at ", self.host_ip, ":", self.host_port, " is listening...")
        
    def accept(self):
        while self.is_active:
            client_socket, client_address = self.server_socket.accept()
            print("Client ", client_address, " connected")
            client_msg = self.recv(client_socket)
            if not client_msg:
                break

            # register data
            data = message.Msg.from_bytes(client_msg)

            type = data.type
            if(type == 'register'):
                # register
                # print("register, client: ", client_socket, " id: ", self.temp_id)
                self.client_id[client_socket] = self.temp_id # 5000 - 5003
                msg = message.Msg('register', {'id': self.temp_id, 'color': player_colors[self.temp_id - 5000], 'map': self.map.to_bytes()})
                self.send(client_socket, msg.to_bytes())
                self.temp_id += 1
            else:
                continue

            thread_handle_client = threading.Thread(target=self.handle_client, args=(client_socket, ))
            thread_handle_client.start()
            thread_update_state = threading.Thread(target=self.client_update_state, args=(client_socket, ))
            thread_update_state.start()

    def recv(self, client_socket):
        try:
            msg = client_socket.recv(1024)
            client_socket.setblocking(0)
            while True:
                try:
                    data=client_socket.recv(1024)
                    msg += data
                except BlockingIOError as e:
                    break
            client_socket.setblocking(1)
            return msg.decode('utf-8')
        except Exception as e:
            print("RecvError in Server: ", e)
            return None

    def send(self, client_socket, msg):
        client_socket.sendall(msg.encode('utf-8'))

    def client_update_state(self, client_socket):
        ip_name= client_socket.getpeername()
        while self.is_active:
            # make sure thread end
            if(client_socket not in self.client_id.keys()):
                break

            # send data to clients
            update_start_time = time.time()
            data = dict()

            # tanks data
            tanks_data = []
            for id in self.client_id.values():
                if(id not in self.tanks.keys()):
                    continue
                tanks_data.append({'id' : id, 'info' : self.tanks[id].to_bytes()})
            data['tanks'] = tanks_data

            # bullet pool data
            bullet_pool_data = self.bullet_pool.to_bytes()
            data['bullet_pool'] = bullet_pool_data

            # send message
            msg = message.Msg('game_data', data)
            self.send(client_socket, msg.to_bytes() + '||')

            update_end_time = time.time()

            sleep_time = 1 / fps - (update_end_time - update_start_time)
            time.sleep(max(0, sleep_time))
        print("Client ", ip_name, " recv close")

    def handle_client(self, client_socket):
        while self.is_active:
            client_msg = self.recv(client_socket)
            if not client_msg:
                break

            info = client_msg.split('||')
            # handle data
            data = message.Msg.from_bytes(info[0])

            type = data.type
            if(type == 'add_bullet'):
                # add bullet
                bullet = Bullet.from_bytes(data.data)
                self.bullet_pool.add_bullet(bullet)
            elif(type == 'update_tank'):
                # update tank
                # print("update tank, client: ", client_socket, " id: ", self.temp_id)
                id = self.client_id[client_socket]
                self.tanks[id] = Tank.from_bytes(data.data)
            elif(type == 'quit'):
                break

        if(client_socket in self.client_id.keys()):
            id = self.client_id[client_socket]
            self.client_id.pop(client_socket)
            self.tanks.pop(id)

        print("Client ", client_socket.getpeername(), " disconnected")
        client_socket.close()
    
    def game_loop(self):
        start_time = time.time()
        with lock:
            self.bullet_pool.update(1 / physics_fps, self.map, self.tanks.values())             
                    
        end_time = time.time()
        sleep_time = 1 / physics_fps - (end_time - start_time)
        time.sleep(max(0, sleep_time))
    
    def start(self):
        thread = threading.Thread(target=self.accept)
        thread.start()

        # game loop
        while True:
            self.game_loop()


    def quit(self):
        self.is_active = False
        exit()

if __name__ == '__main__':
    server = Server('127.0.0.1', 12347)
    server.listen()
    server.start()

