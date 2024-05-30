import pygame
import numpy as np
import json

MAX_BULLET_NUM = 1000

TANK_IMG_PATH = "resources/tank1.png"
BARREL_IMG_PATH = "resources/barrel1.png"

class Tank(pygame.sprite.Sprite):
    def __init__(self, pos, direct, color, size, speed, health, shoot_cd):
        super().__init__()
        self.image = pygame.Surface((size,size)).convert_alpha()
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)
        self.barrel_image = pygame.Surface((size,size*0.3)).convert_alpha()
        self.barrel_image.fill(color)
        self.barrel_rect = self.barrel_image.get_rect(center=pos + np.array([0, size/2]))
        self.pos = pos
        self.direct = direct / np.linalg.norm(direct)
        self.color = color
        self.size = size
        self.speed = speed
        self.health = health
        self.shoot_cd = shoot_cd
        self.shoot_timer = 0
        
    def move(self, direct, delta_time, map = None):
        self.pos += direct * self.speed * delta_time
        if(map == None):
            return
        wall = map.collide(self)
        if(wall != None):
            normal = wall.collide_normal(self.pos)
            self.pos += normal * self.speed * delta_time
                
    def rotate(self, direct):
        direct /= np.linalg.norm(direct)       
        self.direct = direct
        
    def shoot(self, time):
        if(time - self.shoot_timer > self.shoot_cd):
            self.shoot_timer = time
            return Bullet(self.pos + self.direct * self.size, self.direct, (10,10,10), 10, 500, 10)
        return None
    
    def is_hit(self, bullet):
        if(pygame.sprite.collide_rect(self, bullet)):
            self.health -= bullet.damage
            return True
        return False
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        
        # rotate barrel image
        angle = -np.degrees(np.arctan2(self.direct[1], self.direct[0]))
        rotated_barrel_image = pygame.transform.rotate(self.barrel_image, angle)
        rotated_barrel_rect = rotated_barrel_image.get_rect(center=self.pos + self.size / 2 * self.direct)
        screen.blit(rotated_barrel_image, rotated_barrel_rect)        
        
        # pygame.draw.rect(screen, self.color, (self.pos[0] - self.size / 2, self.pos[1] - self.size / 2, self.size, self.size))
        # pygame.draw.line(screen, self.color, self.pos, self.pos + self.direct * self.size, int(self.size / 2))
    
    def update_color(self, color):
        self.color = color
        self.image.fill(self.color)
        self.barrel_image.fill(self.color)
            
    def update(self, delta_time, map = None):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.move(np.array([0, -1]), delta_time, map)
        if keys[pygame.K_a]:
            self.move(np.array([-1, 0]), delta_time, map)
        if keys[pygame.K_s]:
            self.move(np.array([0, 1]), delta_time, map)
        if keys[pygame.K_d]:
            self.move(np.array([1, 0]), delta_time, map)
             
        mouse_pos = pygame.mouse.get_pos()
        self.rotate(np.array(mouse_pos) - self.pos)
        
        # update sprite pos
        self.rect.center = self.pos
        self.barrel_rect.center = self.pos

    
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
    
class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direct, color, size, speed, damage, max_duration = 1, timer = 0):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)
        self.pos = np.array(pos)
        self.direct = np.array(direct)
        self.color = color
        self.size = size
        self.speed = speed
        self.damage = damage
        self.max_duration = max_duration
        self.timer = timer
        
    def move(self, delta_time):
        self.pos += self.speed * delta_time * self.direct / np.linalg.norm(self.direct)
        
    def draw(self, screen):
        # pass
        pygame.draw.circle(screen, self.color, self.pos, self.size)
        
    def update(self, delta_time):
        if(self.timer > self.max_duration * 1000):
            return False
        self.timer += delta_time * 1000
        self.move(delta_time)
        self.rect.center = self.pos
    
    def to_bytes(self):
        return json.dumps(
            {'pos': self.pos.tolist(), 
             'direct': self.direct.tolist(), 
             'color': self.color, 
             'size': self.size, 
             'speed': self.speed, 
             'damage': self.damage,
             'max_duration': self.max_duration,
             'timer': self.timer}
            )

    @staticmethod
    def from_bytes(data):
        info = json.loads(data)
        return Bullet(np.array(info['pos']), np.array(info['direct']), info['color'], info['size'], info['speed'], info['damage'], info['max_duration'], info['timer'])
    
class BulletPool(pygame.sprite.Group):
    def __init__(self, max_bullet_num = MAX_BULLET_NUM):
        super().__init__()
        self.pool = []
        self.max_bullet_num = max_bullet_num    
    
    def add_bullet(self, bullet):
        if(len(self.pool) < self.max_bullet_num):
            self.pool.append(bullet)
            self.add(bullet)
    
    def remove_bullet(self, bullet):
        if(bullet in self.pool):
            self.pool.remove(bullet)
            self.remove(bullet)
         
    def draw(self, screen):
        for bullet in self.pool:
            bullet.draw(screen)
                   
    def update(self, delta_time, map = None, tanks = None):
        for bullet in self.pool:
            # update bullet collision with walls
            if(map != None):
                wall = map.collide(bullet)
                if(wall != None):
                    normal = wall.collide_normal(bullet.pos)
                    if(np.dot(bullet.direct, normal) < 0):
                        bullet.direct = bullet.direct - 2 * np.dot(bullet.direct, normal) * normal
            
            # update bullet collision with tanks
            if(tanks != None):
                for tank in tanks:
                    if(tank.is_hit(bullet)):
                        self.remove_bullet(bullet)
                        break
            
            if(bullet.update(delta_time) == False):
                self.remove_bullet(bullet)
                
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
                pool.add_bullet(Bullet.from_bytes(i))
        return pool

class Wall(pygame.sprite.Sprite):
    def __init__(self, pos, size, color):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pos
        self.size = size
        self.color = color
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.pos[0] - self.size[0] / 2, self.pos[1] - self.size[1] / 2, self.size[0], self.size[1]))
    
    def inside(self, pos):
        if(pos[0] > self.pos[0] - self.size[0] / 2 and pos[0] < self.pos[0] + self.size[0] / 2 and pos[1] > self.pos[1] - self.size[1] / 2 and pos[1] < self.pos[1] + self.size[1] / 2):
            return True
        return False
    
    def collide_normal(self, pos):
        angle = np.arctan2(pos[1] - self.pos[1], pos[0] - self.pos[0])
        wall_angle = np.arctan2(self.size[1], self.size[0])
        if(angle > -wall_angle and angle < wall_angle):
            return np.array([1, 0])
        if(angle > wall_angle and angle < np.pi - wall_angle):
            return np.array([0, 1])
        if(angle < -wall_angle and angle > -np.pi + wall_angle):
            return np.array([0, -1])
        return np.array([-1, 0])
           
    
    def collide(self, sprite):
        return pygame.sprite.collide_rect(sprite, self)
        
    def to_bytes(self):
        return json.dumps(
            {'pos': self.pos.tolist(), 
             'size': self.size, 
             'color': self.color}
            )
        
    @staticmethod
    def from_bytes(data):
        info = json.loads(data)
        return Wall(np.array(info['pos']), info['size'], info['color'])
    
class Map(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.walls = []
        self.create_test_wall()
        
    def create_test_wall(self):
        wall1 = Wall(np.array([400, 300]), (200, 20), (0, 0, 0))
        wall2 = Wall(np.array([400, 500]), (200, 20), (0, 0, 0))
        wall3 = Wall(np.array([300, 400]), (20, 200), (0, 0, 0))
        wall4 = Wall(np.array([500, 400]), (20, 200), (0, 0, 0))
        self.add_wall(wall1)
        self.add_wall(wall2)
        self.add_wall(wall3)
        self.add_wall(wall4)
    
    def add_wall(self, wall):
        self.walls.append(wall)
        self.add(wall)
    
    def draw(self, screen):
        for wall in self.walls:
            wall.draw(screen)
            
    def collide(self, sprite):
        for wall in self.walls:
            if(wall.collide(sprite)):
                return wall
        return None
    
    def collide_normal(self, pos):
        for wall in self.walls:
            if(wall.inside(pos)):
                return wall.collide_normal(pos)
        return None
    
    def to_bytes(self):
        info = ""   
        for wall in self.walls:
            info += wall.to_bytes() + "#"
        return info
    
    @staticmethod
    def from_bytes(data):
        map = Map()
        info = data.split('#')
        for i in info:
            if(i != ""):
                map.add_wall(Wall.from_bytes(i))
        return map

        