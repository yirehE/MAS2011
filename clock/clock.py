import pygame
import numpy as np
import math
import os
from datetime import datetime

# 게임 윈도우 크기
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# 색 정의
BLACK = (0, 0, 0)
GRAY = (100,100,100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Pygame 초기화
pygame.init()

# 윈도우 제목
pygame.display.set_caption("Robot Arm")

# 윈도우 생성
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# 게임 화면 업데이트 속도
clock = pygame.time.Clock()

# 게임 종료 전까지 반복
done = False

assets_path = os.path.join(os.path.dirname(__file__), 'assets')

def R(theta):
    rad = math.radians(theta)
    c,s = np.cos(rad), np.sin(rad)
    R_matrix = np.array(((c, -s,0), (s, c,0), (0,0,1)))
    return R_matrix

def M(arr):
    a,b = arr
    M_matrix = np.array(((1,0,a),(0,1,b),(0,0,1)))
    return M_matrix

def MRM(theta, arr):
    return M(arr)@R(theta)@M(arr*(-1))

def rev_affine(arr):
    try:
        arr.shape[1]
        return np.array([np.append(i,1) for i in arr])
    except:
        arr = np.array([arr])
        return rev_affine(arr)

def to_affine(arr):
    if arr.shape[0] == 1:
        arr = arr[0]
        return arr[:2]
    return np.array([i[:2] for i in arr])

class CLOCK:
    def __init__(self, city = 'Seoul', point=np.array([0,0])):
        city_dict = {"Seoul":0,"Beijing":-1,"London":-9, "Vancouver":-17, "New York":-14, "Sydney":2}
        self.city = city
        self.hour = datetime.now().hour + city_dict[city]
        self.point = point
        self.plate = pygame.image.load(os.path.join(assets_path, 'clock.png'))
        self.arrowh = np.array([[-5,-100], [5,-100], [5,0], [-5,0]]) + self.point
        self.arrowm = np.array([[-3,-120], [3,-120], [3,0], [-3,0]]) + self.point
        self.arrows = np.array([[-1,-130], [1,-130], [1,0], [-1,0]]) + self.point
        self.clock = [0,0,0]
    
    def move(self,time):
        hour, minute, second = time.hour, time.minute, time.second
        s = 3600*(hour + self.hour) + 60*minute + second
        sec = MRM((s%60)*6, self.point)@(rev_affine(self.arrows).T)
        minu = MRM((s%3600)/10, self.point)@(rev_affine(self.arrowm).T)
        hou = MRM((s%43200)/120, self.point)@(rev_affine(self.arrowh).T)
        self.clock[0] = to_affine(sec.T)
        self.clock[1] = to_affine(minu.T)
        self.clock[2] = to_affine(hou.T)
    
    def draw(self, screen):
        font = pygame.font.SysFont('FixedSys', 40, False)
        text = font.render(f"{self.city}", True, BLACK)
        text_rect = text.get_rect()
        text_rect.midbottom = self.point - [0,170]
        screen.blit(self.plate, self.point - [150,150])
        pygame.draw.polygon(screen, RED, self.clock[0])
        pygame.draw.polygon(screen, GRAY, self.clock[1])
        pygame.draw.polygon(screen, BLACK, self.clock[2])
        pygame.draw.circle(screen, BLACK, self.point, 145,2)
        screen.blit(text, text_rect)

clock_list = []
clock_list.append(CLOCK(point=np.array([200,200])))
clock_list.append(CLOCK(city="Beijing", point=np.array([600,200])))
clock_list.append(CLOCK(city="London", point=np.array([1000,200])))
clock_list.append(CLOCK(city="Vancouver", point=np.array([200,600])))
clock_list.append(CLOCK(city="New York", point=np.array([600,600])))
clock_list.append(CLOCK(city="Sydney", point=np.array([1000,600])))

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
            
    screen.fill(WHITE)

    for c in clock_list:
        c.move(datetime.now())
        c.draw(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()