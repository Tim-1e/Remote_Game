import pygame
import numpy as np

class Tank(pygame.sprite.Sprite):
    def __init__(self, pos, color, size, speed):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.speed = speed

    def update(self, delta_time):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect.y -= self.speed * delta_time
        if keys[pygame.K_s]:
            self.rect.y += self.speed * delta_time
        if keys[pygame.K_a]:
            self.rect.x -= self.speed * delta_time
        if keys[pygame.K_d]:
            self.rect.x += self.speed * delta_time

# 初始化 Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# 创建一个坦克精灵
tank = Tank((400, 300), (0, 255, 0), 50, 200)
all_sprites = pygame.sprite.Group()
all_sprites.add(tank)

# 主循环
running = True
while running:
    delta_time = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update(delta_time)

    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
