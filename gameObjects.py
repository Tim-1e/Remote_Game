import pygame
import numpy as np
import json

MAX_BULLET_NUM = 1000

class Tank():
    def __init__(self, pos, direct, color, size, speed, health, shoot_cd):
        self.pos = pos
        self.direct = direct / np.linalg.norm(direct)
        self.color = color
        self.size = size
        self.speed = speed
        self.health = health
        self.shoot_cd = shoot_cd
        self.shoot_timer = 0
    def move(self, direct, delta_time):
        self.pos +=  direct * self.speed * delta_time
        
    def rotate(self, direct):
        self.direct = direct / np.linalg.norm(direct)

    def shoot(self, time):
        if(time - self.shoot_timer > self.shoot_cd):
            self.shoot_timer = time
            return Bullet(self.pos, self.direct, (10,10,10), 5, 500)
        return None
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.pos[0] - self.size / 2, self.pos[1] - self.size / 2, self.size, self.size))
        pygame.draw.line(screen, self.color, self.pos, self.pos + self.direct * self.size, int(self.size / 2))
        
    def update(self, delta_time):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.move(np.array([0, -1]), delta_time)
        if keys[pygame.K_a]:
            self.move(np.array([-1, 0]), delta_time)
        if keys[pygame.K_s]:
            self.move(np.array([0, 1]), delta_time)
        if keys[pygame.K_d]:
            self.move(np.array([1, 0]), delta_time)

        mouse_pos = pygame.mouse.get_pos()
        self.rotate(np.array(mouse_pos) - self.pos)
    
    def to_bytes(self):
        return json.dumps(
            {'pos': self.pos.tolist(), 
             'direct': self.direct.tolist(), 
             'color': self.color, 
             'size': self.size, 
             'speed': self.speed, 
             'health': self.health, 
             'shoot_cd': self.shoot_cd}
            )
        
    def from_bytes(data):
        info = json.loads(data)
        return Tank(np.array(info['pos']), np.array(info['direct']), info['color'], info['size'], info['speed'], info['health'], info['shoot_cd'])
    
class Bullet():
    def __init__(self, pos, direct, color, size, speed, max_duration = 1, timer = 0):
        self.pos = np.array(pos)
        self.direct = np.array(direct)
        self.color = color
        self.size = size
        self.speed = speed
        self.max_duration = max_duration
        self.timer = timer
        
    def move(self, delta_time):
        self.pos += self.speed * delta_time * self.direct / np.linalg.norm(self.direct)
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.pos, self.size)
        
    def update(self, delta_time):
        if(self.timer > self.max_duration * 1000):
            return False
        self.timer += delta_time * 1000
        self.move(delta_time)
    
    def to_bytes(self):
        return json.dumps(
            {'pos': self.pos.tolist(), 
             'direct': self.direct.tolist(), 
             'color': self.color, 
             'size': self.size, 
             'speed': self.speed, 
             'max_duration': self.max_duration,
             'timer': self.timer}
            )

    @staticmethod
    def from_bytes(data):
        info = json.loads(data)
        return Bullet(np.array(info['pos']), np.array(info['direct']), info['color'], info['size'], info['speed'], info['max_duration'], info['timer'])
    
class BulletPool():
    def __init__(self, max_bullet_num = MAX_BULLET_NUM):
        self.pool = []
        self.max_bullet_num = max_bullet_num    
    
    def add(self, bullet):
        if(len(self.pool) < self.max_bullet_num):
            self.pool.append(bullet)
     
    def draw(self, screen):
        for bullet in self.pool:
            bullet.draw(screen)
                   
    def update(self, delta_time):
        for bullet in self.pool:
            if(bullet.update(delta_time) == False):
                self.pool.remove(bullet)
                
    def to_bytes(self):
        info = ""   
        for bullet in self.pool:
            info += bullet.to_bytes() + "#"
        return info
    
    def from_bytes(data):
        pool = BulletPool(MAX_BULLET_NUM)
        info = data.split('#')
        for i in info:
            if(i != ""):
                pool.add(Bullet.from_bytes(i))
        return pool



        