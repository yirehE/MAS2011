import pygame
import numpy as np
import math
from copy import deepcopy as copy
from os import path

asset_dir = path.join(path.dirname(__file__),'assets')

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
pygame.display.set_caption("Drawing")

# 윈도우 생성
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# 게임 화면 업데이트 속도
clock = pygame.time.Clock()

# 게임 종료 전까지 반복
done = False

SPEED = 1

def R(theta):
    rad = math.radians(theta)
    c,s = np.cos(rad), np.sin(rad)
    R_matrix = np.array(((c, -s,0), (s, c,0), (0,0,1)))
    return R_matrix

def S(x,y):
    S_matrix = np.array(((x, 0,0), (0, y,0), (0,0,1)))
    return S_matrix

def M(arr):
    a,b = arr
    M_matrix = np.array(((1,0,a),(0,1,b),(0,0,1)))
    return M_matrix

def orbit(theta, arr, x, y):
    arr = np.array(arr)
    return M(arr)@R(theta)@S(x,y)@M(arr*(-1))

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

class STAR():
    star = pygame.image.load(path.join(asset_dir, "star_r.png")).convert()

    def __init__(self,):
        px = np.random.random_sample()*(WINDOW_WIDTH)
        py = np.random.random_sample()*(WINDOW_HEIGHT)
        self.point = np.array([px, py])
        self.t = np.random.randint(0,100)
        self.star = STAR.star

    def draw(self, screen, time=0):
        self.star.set_alpha(abs(100-(self.t + time)%200))
        screen.blit(STAR.star, self.point)

class PLANET():
    def __init__(self, name, location, sun_loc):
        self.image = pygame.image.load(path.join(asset_dir, f"{name}.png"))
        self.rect = self.image.get_rect()
        self.rect.center = location
        self.rect_moved = copy(self.rect)
        self.sun_loc = sun_loc
        self.aspeed = SPEED

    def move(self, t):
        matrix = orbit(self.aspeed*t,arr=self.sun_loc,x=1,y=.6)
        a = matrix @(to_affine(self.rect.center).T)
        self.rect_moved.center = rev_affine(a.T)

    def draw(self,screen):
        screen.blit(self.image, self.rect_moved)

class MOON(PLANET):
    def __init__(self, name, origin_name, location:list, sun_loc:np.ndarray, origin:np.ndarray):
        super().__init__(name,location, sun_loc)
        self.origin = origin
        self.origin_name = origin_name

    def move(self, t):
        matrix = orbit(self.aspeed*t, arr=self.sun_loc, x=1, y=.6)
        a = matrix@M(np.array(self.sun_loc) - np.array(self.origin))@(to_affine(self.rect.center).T)
        self.rect_moved.center = rev_affine(a.T)

class Starship:
    IMAGE_SIZE = 70
    def __init__(self,):
        self.image = pygame.image.load(path.join(asset_dir, "starship.png"))
        self.x = np.random.random_sample()*(WINDOW_WIDTH-2*Starship.IMAGE_SIZE)
        self.y = np.random.random_sample()*(WINDOW_HEIGHT-2*Starship.IMAGE_SIZE)
        self.dx = 5*np.random.random_sample()
        self.dy = 5 - 10*np.random.random_sample()

    def move(self,):
        self.x += self.dx
        self.y += self.dy
        if self.x + Starship.IMAGE_SIZE > WINDOW_WIDTH or self.x<0:
            self.dx *=  -1
            self.image = pygame.transform.flip(self.image, True, False)
        if self.y + Starship.IMAGE_SIZE > WINDOW_HEIGHT or self.y<0:
            self.dy *=  -1
    
    def draw(self, screen):
        screen.blit(self.image, [self.x, self.y])

stars = [STAR() for _ in range(10)]
sun = pygame.image.load(path.join(asset_dir, "sun_r.png"))
sun = pygame.transform.scale(sun,(114,86))
sun_rect = sun.get_rect()
sun_rect.center = [WINDOW_WIDTH/2,WINDOW_HEIGHT/2]
venus = PLANET("venus",[700,650],np.array(sun_rect.center))
venus.aspeed = SPEED * 0.6
saturn = PLANET("saturn",[300,650],np.array(sun_rect.center))
saturn.aspeed = SPEED / 30
titan = MOON("moon", "saturn", [200,650], np.array(saturn.rect_moved.center), np.array(saturn.rect.center))
titan.aspeed = SPEED * 22
earth = PLANET("earth",[600,800],np.array(sun_rect.center))
moon = MOON("moon", "earth", [600,930], np.array(earth.rect_moved.center), np.array(earth.rect.center))
moon.aspeed = SPEED * 12
starship = Starship()

planets = [venus, earth, saturn]
moons = [moon, titan]

t = 0

while not done:
    t+=1
    # t %= 200
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
            
    screen.fill(BLACK)


    for s in stars:
        s.draw(screen, t)
    screen.blit(sun, sun_rect)
    for p in planets:
        p.move(t)
        p.draw(screen)
    for m in moons:
        exec(f"m.sun_loc = {m.origin_name}.rect_moved.center")
        m.move(t)
        m.draw(screen)
    starship.move()
    starship.draw(screen)

    pygame.display.flip()

    clock.tick(60)

# 게임 종료
pygame.quit()