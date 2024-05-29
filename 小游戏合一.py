import socket

import pygame

# 设置初始状态为等待选择
state = "WAIT_FOR_SELECT"

# 初始化Pygame
pygame.init()
screen = pygame.display.set_mode((640, 480))

# 绘制开始界面
def draw_start_screen():
    screen.fill((255, 255, 255))
    font = pygame.font.Font(None, 36)
    create_game_text = font.render("Create Game", True, (0, 0, 0))
    join_game_text = font.render("Join Game", True, (0, 0, 0))
    create_game_rect = create_game_text.get_rect()
    join_game_rect = join_game_text.get_rect()
    create_game_rect.center = (320, 240)
    join_game_rect.center = (320, 300)
    screen.blit(create_game_text, create_game_rect)
    screen.blit(join_game_text, join_game_rect)
    pygame.display.update()


def get_input(tips):
    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()
    input_text = ""
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key==1073741912:
                    done = True
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode
        screen.fill((255, 255, 255))

        txt_surface = font.render(tips, True, (0, 0, 0))
        txt_surface_rect = txt_surface.get_rect()
        txt_surface_rect.center=(300,150)
        screen.blit(txt_surface, txt_surface_rect)

        txt_surface = font.render(input_text, True, (0, 0, 0))
        txt_surface_rect = txt_surface.get_rect()
        txt_surface_rect.center = (300, 200)
        screen.blit(txt_surface, txt_surface_rect)

        pygame.display.update()
        clock.tick(30)
    return input_text

def CheckIp(host_ip):
    flag = False
    while (not flag):
        x = host_ip.split('.')
        flag = True
        if (len(x) != 4):
            flag = False
        for i in x:
            if (not i.isdigit()):
                flag = False
        if (not flag):
            tips="Please input correct ip"
            host_ip = get_input(tips)
    return host_ip
# 绘制输入IP的界面
def draw_input_ip_screen():
    tips = "Input the IP:"
    host_ip = get_input(tips)
    host_ip=CheckIp(host_ip)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host_ip, 54321))
    return client_socket

# 绘制等待加入界面
def draw_waiting_screen():
    screen.fill((255, 255, 255))
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    host_ip="10.129.219.200"
    font = pygame.font.Font(None, 36)
    text = font.render("Host Name: " + host_name, True, (0, 0, 0))
    text_rect = text.get_rect()
    text_rect.centerx = screen.get_rect().centerx
    text_rect.centery = screen.get_rect().centery - 50
    screen.blit(text, text_rect)

    text = font.render("Host IP: " + host_ip, True, (0, 0, 0))
    text_rect = text.get_rect()
    text_rect.centerx = screen.get_rect().centerx
    text_rect.centery = screen.get_rect().centery
    screen.blit(text, text_rect)

    text = font.render("Waiting for connection...", True, (0, 0, 0))
    text_rect = text.get_rect()
    text_rect.centerx = screen.get_rect().centerx
    text_rect.centery = screen.get_rect().centery+50
    screen.blit(text, text_rect)

    # 在这里创建服务器套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host_ip, 54321))
    server_socket.listen(1)

    pygame.display.update()
    client_socket, client_address = server_socket.accept()
    return client_socket

# 定义方块类
class Block:
    def __init__(self, x, y, block_size):
        self.x = x
        self.y = y
        self.block_size = block_size
        self.move_size=block_size/100

    def update(self, keys):
        if keys[pygame.K_w]:
            self.y -= self.move_size
        if keys[pygame.K_s]:
            self.y += self.move_size
        if keys[pygame.K_a]:
            self.x -= self.move_size
        if keys[pygame.K_d]:
            self.x += self.move_size

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.block_size, self.block_size))




# 循环游戏进程
def Gaming(server_socket):
    # 创建方块对象
    block1 = Block(320, 240, 20)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        block1.update(keys)

        # 发送方块信息到客户端
        server_socket.sendall(f"{block1.x} {block1.y} #".encode('utf-8'))

        # 接收客户端方块信息
        data = server_socket.recv(1024)
        if (not data):
            break
        data_par=data.decode('utf-8').split('#')[0]
        print(data_par)
        block1.x,block1.y= map(float, data_par.split())

        # 绘制方块
        screen.fill((255, 255, 255))
        block1.draw(screen)

        # 更新窗口
        pygame.display.update()

    # 退出pygame
    pygame.quit()

#程序开始处
# 等待用户选择（创建游戏或加入游戏）
while state == "WAIT_FOR_SELECT":
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            #print(mouse_x,mouse_y)
            if 240 < mouse_x < 400:
                if 220 < mouse_y < 250:
                    state = "CREATE_GAME"
                elif 290 < mouse_y < 350:
                    state = "JOIN_GAME"
    draw_start_screen()
    pygame.display.update()

server_socket=None
# 计算机A创建游戏
if state == "CREATE_GAME":
    server_socket=draw_waiting_screen()
    state = "PLAY_GAME"

# 计算机B加入游戏
elif state == "JOIN_GAME":
    server_socket=draw_input_ip_screen()
    state = "PLAY_GAME"

# 游戏状态
if state == "PLAY_GAME":
    # 游戏代码
    Gaming(server_socket)