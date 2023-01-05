import pygame
import numpy as np
import math

# 게임 윈도우 크기
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 1000

# 색 정의
BLACK = (0, 0, 0)
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

def R(theta):
    rad = math.radians(theta)
    c,s = np.cos(rad), np.sin(rad)
    R_matrix = np.array(((c, -s,0), (s, c,0), (0,0,1)))
    return R_matrix

def M(arr):
    a,b = arr
    M_matrix = np.array(((1,0,a),(0,1,b),(0,0,1)))
    return M_matrix

def MR(theta, arr):
    return M(arr)@R(theta)@M(arr*(-1))

def to_affine(arr):
    try:
        arr.shape[1]
        return np.array([np.append(i,1) for i in arr])
    except:
        arr = np.array([arr])
        return to_affine(arr)

def rev_affine(arr):
    if arr.shape[0] == 1:
        arr = arr[0]
        return arr[:2]
    return np.array([i[:2] for i in arr])

class BLADE:
    def __init__(self,arr):
        self.rec = arr

    def draw(self, screen):
        pygame.draw.polygon(screen, RED, self.rec, 2)

class JOINT:
    def __init__(self,blades=[], joints=[], point=[]):
        self.bladelist = blades
        self.jointlist = joints
        self.point = point
        self.color = BLUE
        self.theta = 0
    
    def move(self,speed=1):
        self.theta = speed * -2
        if self.theta:
            matrix = MR(self.theta, self.point)
            for blade in self.bladelist:
                a = matrix @(to_affine(blade.rec).T)
                blade.rec = rev_affine(a.T)
            for joint in self.jointlist:
                j = matrix@(to_affine(joint.point).T)
                joint.point = rev_affine(j.T)
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.point, 8)

ar = np.array([[350, 500], [350, 350], [600, 350]])
bd = np.array([[650, 300], [550, 300], [400, 900], [800,900]])
jp = np.array([600,350])
matrix = MR(-90,jp)
blade_list = [ar]
for i in range(1,4):
    blade_list.append(rev_affine((matrix@to_affine(blade_list[i-1]).T).T))
blade_list = [BLADE(a) for a in blade_list]
joint = JOINT(blades=blade_list, point=jp)

speed = 1

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                speed -= 1
            elif event.key == pygame.K_u:
                speed += 1
    joint.move(speed)
            
    screen.fill(BLACK)

    pygame.draw.polygon(screen, GREEN, bd, 4)

    for a in blade_list:
        a.draw(screen)
    joint.draw(screen)

    font = pygame.font.SysFont('FixedSys', 40, True, False)
    text = font.render(f"U:SPEED UP  D:SPEED DOWN  SPEED:{speed}x", True, WHITE)
    screen.blit(text, [10, 10])

    pygame.display.flip()

    clock.tick(60)

pygame.quit()