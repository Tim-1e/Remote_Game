from gameObjects import *
import socket
import pygame

fps = 60

pygame.init()
screen = pygame.display.set_mode((640, 480))

tank = Tank(np.array([100.0, 100.0]), np.array([1.0, 0]), (255, 0, 0), 50, 200, 100, 500)
    
bullet_pool = BulletPool(MAX_BULLET_NUM)

def client_connect(host_ip, host_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host_ip, host_port))
    return client_socket



while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
            
    screen.fill((255, 255, 255))
    
    tank.update(1 / fps)
    bullet_pool.update(1 / fps)
        
    pygame.display.update()
    pygame.time.delay(int(1000 / fps))
    
