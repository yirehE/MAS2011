# Reference : shmup! https://kidscancode.org/blog/2016/11/pygame_shmup_part_14/

# v1.1 에너지바 추가, 에너지 3단계 추가
# v1.2 특정 확률로 운석 좌우 이동 방향 반전
# v1.3 시간이 지날수록 운석 수 증가
# v1.3.1 for문 일부를 리스트컴프리헨션으로 바꿈
# v1.3.2 powerup시 bullet 생성을 리스트로 바꾸어 코드 간편화
# v1.4 상하 움직임 추가

# 상점 (파워업 지속시간, 이동속도, 체력)

import pygame
import random
import numpy as np
from os import path

img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

WIDTH = 600
HEIGHT = 900
FPS = 60
POWERUP_TIME = 5000
NAME = 'Guardian of Earth'

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARKBLUE = (200,200,255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)

# initialize pygame and create window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(f"{NAME}")
clock = pygame.time.Clock()

font_name = pygame.font.match_font('Verdana')
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, DARKBLUE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_power_bar(surf, x, y, power, time, current_time):
    BAR_LENGTH = 15
    BAR_HEIGHT = 400
    if power ==1:
        color = GREEN
        fill = BAR_HEIGHT
    elif power == 2:
        color = ORANGE
    elif power >= 3:
        color = RED
    if power != 1:
        fill = (1-(current_time - time)/POWERUP_TIME) * BAR_HEIGHT
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, BAR_LENGTH, fill)
    pygame.draw.rect(surf, color, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

def draw_coin(surf, x, y, img, coin):
    img_rect = img.get_rect()
    img_rect.x = x
    img_rect.y = y
    surf.blit(img, img_rect)
    draw_text(screen, f"{coin}", 25, x+60, y)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 6
        self.speedx = 0
        self.speedy = 0
        self.maxshield = 100
        self.shield = self.maxshield
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 2
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()
        self.coin = 5000

    def update(self):
        # timeout for powerups
        if self.power >= 2:
            if self.power >= 4 or pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
                self.power -= 1
                self.power_time = pygame.time.get_ticks()

        # unhide if hidden
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        self.speedx = 0
        self.speedy = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -self.speed
        if keystate[pygame.K_RIGHT]:
            self.speedx = self.speed
        if keystate[pygame.K_UP]:
            self.speedy = -self.speed
        if keystate[pygame.K_DOWN]:
            self.speedy = self.speed
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < HEIGHT/5:
            self.rect.top = HEIGHT/5

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.power == 2:
                bulletl = [Bullet(self.rect.left, self.rect.centery),
                          Bullet(self.rect.right, self.rect.centery)]
                all_sprites.add(*bulletl)
                bullets.add(*bulletl)
                shoot_sound.play()
            elif self.power >= 3:
                bulletl = [Bullet(self.rect.left, self.rect.centery),
                          Bullet(self.rect.right, self.rect.centery),
                          Bullet(self.rect.centerx, self.rect.top)]
                all_sprites.add(*bulletl)
                bullets.add(*bulletl)
                shoot_sound.play()

    def hide(self):
        # hide the player temporarily
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.bottom = random.randrange(-80, -20)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.speedx *= np.random.choice([1,-1],1,p=[.995,.005])[0]
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -100 or self.rect.right > WIDTH + 100:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load(path.join(img_dir, "BOSS.png")).convert()
        img = pygame.transform.scale(img, (288, 187))
        self.image = img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.top = 5
        self.lives = 50
        self.speedx = 3
        self.shoot_delay = 300
        self.last_shot = 0
        self.last_update = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = BossBullet(self.rect.centerx, self.rect.bottom)
            all_sprites.add(bullet)
            bossbullets.add(bullet)
        # shoot_sound.play()

    def hide(self):
        self.kill()

    def update(self):
        self.rect.x += self.speedx
        if self.rect.centerx > WIDTH or self.rect.centerx < 0:
            self.speedx *= -1
        self.shoot()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        # kill if it moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()

class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = boss_bullet_img
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = 5
    
    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = np.random.choice(['shield', 'gun', 'coin'], p=[.2,.2,.6 ])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 5

    def update(self):
        self.rect.y += self.speedy
        # kill if it moves off the top of the screen
        if self.rect.top > HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class Warning_message():
    def __init__(self):
        self.image = warning_img
        self.rect = self.image.get_rect()
        self.rect.center = [WIDTH/2, HEIGHT/3]
        self.time = 30

    def draw(self):
        if self.time>=0:
            self.image.set_alpha(abs(10 - self.time%20)*10)
            screen.blit(self.image, self.rect)
            self.time -= .2
            return True
        else:
            return False

def show_go_screen():
    waiting = True
    while waiting:
        screen.blit(background, background_rect)
        draw_text(screen, "G.O.E.", 64, WIDTH / 2, HEIGHT / 4)
        draw_text(screen, "Arrow keys move, Space to fire", 22,
                WIDTH / 2, HEIGHT / 2)
        draw_text(screen, "Press M to go market and other keys to begin", 18, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.flip()
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_m:
                    show_market()
                else:
                    waiting = False

def show_market():
    def item(name, x, y, cost, key):
        draw_text(screen, f"{name} ({key})", 20, x+100, y)
        img = pygame.image.load(path.join(img_dir, f"{name}.png")).convert()
        img = pygame.transform.scale(img, (200, 200))
        img_rect = img.get_rect()
        img_rect = [x,y+23]
        screen.blit(img, img_rect)
        draw_text(screen, f"COST : {cost}", 20, x+100, y+223)
    waiting = True
    while waiting:
        screen.blit(background, background_rect)
        draw_text(screen, "MARKET", 64, WIDTH / 2, HEIGHT / 12)
        # draw_text(screen, "Arrow keys move, Space to fire", 22,
        #           WIDTH / 2, HEIGHT / 2)
        draw_text(screen, "Press P to play", 18, WIDTH / 2, HEIGHT * 5/6)
        item('PowerUP Time',30,HEIGHT / 4 - 50, 50, 'T')
        item('SHIELD',WIDTH - 230 ,HEIGHT / 4 - 50, 50, 'H')
        item('SPEED',30,HEIGHT / 2, 50, 'S')
        item('SHOOT SPEED',WIDTH - 230,HEIGHT / 2, 50, 'F')
        clock.tick(FPS)
        draw_coin(screen, WIDTH - 100, 5, coin_img, player.coin)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_t:
                    if player.coin > 50:
                        player.coin -= 50
                        player.power_time += 200
                elif event.key == pygame.K_h:
                    if player.coin > 50:
                        player.coin -= 50
                        player.maxshield += 10
                elif event.key == pygame.K_s:
                    if player.coin > 50:
                        player.coin -= 50
                        player.speed += .5
                elif event.key == pygame.K_f:
                    if player.coin > 50:
                        player.coin -= 50
                        player.shoot_delay = max(player.shoot_delay-5,0)
                elif event.key == pygame.K_p:
                    waiting = False

# Load all game graphics
background = pygame.image.load(path.join(img_dir, "background_earth.jpg")).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir, "playerShip1_blue.png")).convert()
# player_img = pygame.image.load(path.join(img_dir, "playerShip1_orange.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(img_dir, "laserRed16.png")).convert()
boss_bullet_img = pygame.image.load(path.join(img_dir, "boss_bullet.png")).convert()
boss_bullet_img = pygame.transform.scale(boss_bullet_img, (13, 13))
meteor_img = pygame.image.load(path.join(img_dir, "meteor.png")).convert()
meteor_images = [pygame.transform.scale(meteor_img, (i, i)) for i in (100,45,30)]
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)
powerup_images = {}
coin_img = pygame.image.load(path.join(img_dir, "coin.png")).convert()
coin_img = pygame.transform.scale(coin_img, (30, 30))
powerup_images['coin'] = coin_img
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield_gold.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert()
warning_img = pygame.image.load(path.join(img_dir, "warning.png")).convert()
warning_img = pygame.transform.scale(warning_img, (600, 200))

# Load all game sounds
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'pew.wav'))
shield_sound = pygame.mixer.Sound(path.join(snd_dir, 'pow4.wav'))
power_sound = pygame.mixer.Sound(path.join(snd_dir, 'pow5.wav'))
expl_sounds = [pygame.mixer.Sound(path.join(snd_dir, snd)) for snd in ['expl3.wav', 'expl6.wav']]
player_die_sound = pygame.mixer.Sound(path.join(snd_dir, 'rumble1.ogg'))
pygame.mixer.music.load(path.join(snd_dir, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
pygame.mixer.music.set_volume(0.4)

pygame.mixer.music.play(loops=-1)
# Game loop
game_over = True
running = True
player = Player()
flag = False
b = True
# boss = Boss()

while running:
    if not game_over:
        if (pygame.time.get_ticks() - t) % 300 == 0:
            newmob()

        if len(mobs)%7 == 2 and b:
            warning = Warning_message()
            flag = warning.draw()
            b = False

        if len(mobs)%7 == 3 and not b:
            boss = Boss()
            boss.lives += 10*boss_count
            all_sprites.add(boss)
            b = True

    if game_over:
        show_go_screen()
        game_over = False
        player.shield = player.maxshield
        player.lives = 2
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        bossbullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        all_sprites.add(player)
        t = pygame.time.get_ticks()
        boss_count = 0         
        for i in range(7):
            newmob()
        score = 0

    # keep loop running at the right speed
    clock.tick(FPS)
    # Process input (events)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False

    # Update
    all_sprites.update()

    # check to see if a bullet hit a mob
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.3:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        newmob()

    # check to see if a mob hit the player
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 3
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newmob()
        if player.shield <= 0:
            player_die_sound.play()
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = player.maxshield

    # check to see if a boss bullet hit the player
    hits = pygame.sprite.spritecollide(player, bossbullets, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= 30
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        if player.shield <= 0:
            player_die_sound.play()
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = player.maxshield

    try:
        # check to see if a bullet hit the boss
        hits = pygame.sprite.spritecollide(boss, bullets, True, pygame.sprite.collide_mask)
        for hit in hits:
            expl = Explosion(hit.rect.center, 'sm')
            all_sprites.add(expl)
            boss.lives -= 1
            if boss.lives <= 0:
                death_explosion = Explosion(boss.rect.center, 'player')
                # boss.hide()
                boss.rect.right = 0
                boss_count += 1
                all_sprites.remove(boss)
                all_sprites.add(death_explosion)
    except:
        pass

    # check to see if player hit a powerup
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield += random.randrange(10, 30)
            shield_sound.play()
            if player.shield >= player.maxshield:
                player.shield = player.maxshield
        if hit.type == 'gun':
            player.powerup()
            power_sound.play()
        if hit.type == 'gun':
            player.coin += 1

    # if the player died and the explosion has finished playing
    if player.lives == 0 and not death_explosion.alive():
        game_over = True

    # Draw / render
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    if flag:
        flag = warning.draw()
    all_sprites.draw(screen)
    draw_text(screen, f"{(pygame.time.get_ticks() - t)/1000:.1f}s", 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield/player.maxshield*100)
    draw_power_bar(screen, 5, 30, player.power, player.power_time, pygame.time.get_ticks())
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)
    draw_coin(screen, WIDTH - 100, 40, coin_img, player.coin)
    # *after* drawing everything, flip the display
    pygame.display.flip()

pygame.quit()
