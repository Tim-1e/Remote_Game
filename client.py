from gameObjects import *
import message
import json
import socket
import pygame
import threading
from threading import Lock
import time

fps = 60
lock = Lock()

class Client():
    def __init__(self, host_ip, host_port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host_ip = host_ip
        self.host_port = host_port
        self.id = 0
        self.connect_state = "init"
        self.is_active = True
        
        # game info
        self.bullet_pool = BulletPool(MAX_BULLET_NUM)
        self.tank = Tank(np.array([100.0, 100.0]), np.array([1.0, 0]), (255, 0, 0), 50, 200, 100, 500)
        self.tanks = [self.tank]
        
    def connect(self):
        self.client_socket.connect((self.host_ip, self.host_port))
        self.connect_state = "connected"
        
    def register(self):
        self.send(message.Msg("register", None).to_bytes())
        data = message.Msg.from_bytes(self.recv())
        print(data)
        # example {'type': 'register', 'id': 0, 'color': (255, 0, 0)...}
        self.id = data.data['id']
        self.tank.color = data.data['color']
        # and other info
        self.connect_state == "registered"  
        
    def send(self, msg):
        self.client_socket.sendall(msg.encode('utf-8'))
        
    def recv(self):
        try:
            msg = self.client_socket.recv(1024)
            self.client_socket.setblocking(0)
            while True:
                try:
                    data=self.client_socket.recv(1024)
                    msg += data
                except BlockingIOError as e:
                    break
            self.client_socket.setblocking(1)
            return msg.decode('utf-8')
        except Exception as e:
            print(e)
            return None
    
    def recv_and_update(self):
        while(self.is_active):
            server_msg = self.recv()
            if(server_msg != None):
                msg = server_msg.split('||')
                for m in msg:
                    if(m != ''):
                        self.update(m)
            
    def update(self, server_msg):    
        data = message.Msg.from_bytes(server_msg)
        type = data.type
        if(type != "game_data"):
            print("unknown message type: " + type)
            return
        # example {'tanks': ..., 'bullet_pool': ...'}
        # print(data)
        # tanks data
        tanks_data = data.data['tanks']
        if(tanks_data != None):
            with lock:
                self.tanks = [self.tank]
                for tank_info in tanks_data:
                    if(tank_info['id'] == self.id):
                        continue
                    tank = Tank.from_bytes(tank_info['info'])
                    self.tanks.append(tank)
        # bullet pool data
        bullet_pool_data = data.data['bullet_pool']
        if(bullet_pool_data != None):
            with lock:
                self.bullet_pool = BulletPool.from_bytes(bullet_pool_data)
    
    def draw(self, screen, tanks, bullet_pool):
        for tank in tanks:
            tank.draw(screen)    
        bullet_pool.draw(screen)   
         
    def game_loop(self, screen):
        loop_start_time = pygame.time.get_ticks()
        
        screen.fill((255, 255, 255))
        self.tank.update(1 / fps)  
        # with lock:
        #     self.bullet_pool.update(1 / fps)
        
        # update shoot
        if(pygame.mouse.get_pressed()[0]):
            bullet = self.tank.shoot(pygame.time.get_ticks())
            if(bullet != None):
                # send shoot message to server 
                self.send(message.Msg("add_bullet", bullet.to_bytes()).to_bytes() + '||')       
        
        # send tank message to server
        self.send(message.Msg("update_tank", self.tank.to_bytes()).to_bytes() + '||')
        
        # draw
        self.draw(screen, self.tanks, self.bullet_pool)
        
        loop_end_time = pygame.time.get_ticks() 
               
        pygame.display.update()
        pygame.time.delay(int(1000 / fps - (loop_end_time - loop_start_time)))
        
    def start(self):
        screen = pygame.display.set_mode((640, 480))
        thread_connect = threading.Thread(target=self.connect)
        thread_connect.start()
        while(self.connect_state != "connected"):
            time.sleep(0.1)
        self.register()
        
        thread_recv = threading.Thread(target=self.recv_and_update)
        thread_recv.start() 
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
            self.game_loop(screen)                
               
    def quit(self):
        self.client_socket.send(message.Msg("quit", None).to_bytes())
        self.is_active = False
        pygame.quit()
        exit()

if __name__ == "__main__":
    client = Client('127.0.0.1', 12347)
    client.start()
    
    