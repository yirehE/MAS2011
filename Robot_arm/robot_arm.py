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

class ARM:
    def __init__(self,arr):
        self.rec = arr

    def draw(self, screen):
        pygame.draw.polygon(screen, RED, self.rec, 2)

class JOINT:
    def __init__(self,arms=[], joints=[], point=[]):
        self.armlist = arms
        self.jointlist = joints
        self.point = point
        self.color = BLUE
    
    def move(self,key,auto=False):
        theta=0
        if auto:
            theta = np.random.choice([-3,3],p=[.8,.2])
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    theta = -3
                elif event.key == pygame.K_DOWN:
                    theta = 3
        if theta:
            for arm in self.armlist:
                a = MR(theta, self.point)@(to_affine(arm.rec).T)
                arm.rec = rev_affine(a.T)
            for joint in self.jointlist:
                j = MR(theta, self.point)@(to_affine(joint.point).T)
                joint.point = rev_affine(j.T)
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.point, 8)

ar = np.array([[350, 500], [500, 500], [500, 800], [350, 800]])
jp = np.array([425,550])
jpp = np.array([425,750])
ar2 = rev_affine((MR(-120,jp)@(to_affine(ar).T)).T)
jp2 = rev_affine((MR(-120,jp)@(to_affine(jpp).T)).T)
ar3 = rev_affine((MR(-120,jp2)@(to_affine(ar2).T)).T)
jp3 = rev_affine((MR(-120,jp2)@(to_affine(jp).T)).T)
ar4 = rev_affine((MR(-120,jp3)@(to_affine(ar3).T)).T)
arm_list = [ARM(ar),ARM(ar2),ARM(ar3),ARM(ar4)]
joint_list = []
joint_list.append(JOINT([arm_list[3]], point=jp3))
joint_list.append(JOINT(arm_list[2:], joints=joint_list[:], point=jp2))
joint_list.append(JOINT(arm_list[1:], joints=joint_list[:],point=jp))


auto = False
i=2

while not done:
    joint = joint_list[i]
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                auto = True
            elif event.key == pygame.K_2:
                auto = False
            elif event.key == pygame.K_LEFT:
                i = min(2,i+1)
            elif event.key == pygame.K_RIGHT:
                i = max(0,i-1)
    joint.move(event,auto)
            
    screen.fill(BLACK)

    for a in arm_list:
        a.draw(screen)
    for j in joint_list:
        j.draw(screen)
    
    font = pygame.font.SysFont('FixedSys', 40, True, False)
    text = font.render(f"1:auto   2:keyboard    Automode:{auto}    joint:{2-i}", True, WHITE)
    screen.blit(text, [10, 10])

    pygame.display.flip()

    clock.tick(60)

pygame.quit()