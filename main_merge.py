import os
import sys
# import time

import pygame
import pytmx

from random import randint, choice

file_name1 = 'data/levels/level1.tmx'
file_name2 = 'data/levels/level2.tmx'

FPS = 60
STEP = 6
GRAVITY = 0.5
moving_left = False
moving_right = False
moving_down = False
jump = False
dash = False
dash_unlock = False
double_jump_unlock = False
double_jump_check = False
push_event = False
pygame.init()

size = WIDTH, HEIGHT = 1280, 720
map = None
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

pygame.display.set_caption('V.L.A.D')

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
mini_boss_group = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
background_group = pygame.sprite.Group()
ladder_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
trap_group = pygame.sprite.Group()
border_group = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
treasure_group = pygame.sprite.Group()
enemy_borders = pygame.sprite.Group()

pause_buttons_group = pygame.sprite.Group()
menu_sprite_group = pygame.sprite.Group()
death_screen_group = pygame.sprite.Group()
win_screen_group = pygame.sprite.Group()
inventory_sprites = pygame.sprite.Group()

enemies = []
level_count = 0


def load_image(name, color_key=None):
    try:
        image = pygame.image.load(name).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def remove_bg_from_tiles(image):
    color_key = image.get_at((0, 0))
    image.set_colorkey(color_key)
    return image


player_image = load_image('data/images/entities/player/hero.png', -1)
enemy_image = load_image('data/images/entities/enemy/enemy.png', -1)
mini_boss_image = load_image('data/images/entities/mini_boss/mini_boss.png', -1)
dash_image = load_image('data/images/items/key/0.png', -1)

play_pause_button = pygame.sprite.Sprite(pause_buttons_group)
play_pause_button.image = load_image('data/images/interface/pause/play_button.png', -1)
play_pause_button.rect = play_pause_button.image.get_rect()
play_pause_button.rect.x = WIDTH // 2 - play_pause_button.image.get_width() - 20
play_pause_button.rect.y = HEIGHT // 2 - play_pause_button.image.get_height() // 2
menu_pause_button = pygame.sprite.Sprite(pause_buttons_group)
menu_pause_button.image = load_image('data/images/interface/pause/menu_button.png', -1)
menu_pause_button.rect = menu_pause_button.image.get_rect()
menu_pause_button.rect.x = WIDTH // 2 + menu_pause_button.image.get_width() + 20
menu_pause_button.rect.y = HEIGHT // 2 - menu_pause_button.image.get_height() // 2

background_menu_image = load_image('data/images/interface/menu/background.png')
start_menu_button = pygame.sprite.Sprite(menu_sprite_group)
start_menu_button.image = load_image('data/images/interface/menu/start_button.png', -1)
start_menu_button.rect = start_menu_button.image.get_rect()
start_menu_button.rect.x = WIDTH // 2 - start_menu_button.image.get_width() // 2
start_menu_button.rect.y = HEIGHT // 2 - start_menu_button.image.get_height() // 2

background_death_screen = load_image('data/images/interface/death_screen/background.png')
restart_death_screen_button = pygame.sprite.Sprite(death_screen_group)
restart_death_screen_button.image = load_image('data/images/interface/death_screen/restart_button.png', -1)
restart_death_screen_button.rect = restart_death_screen_button.image.get_rect()
restart_death_screen_button.rect.x = WIDTH // restart_death_screen_button.image.get_width() - 20
restart_death_screen_button.rect.y = HEIGHT // restart_death_screen_button.image.get_width() - 20
menu_death_screen_button = pygame.sprite.Sprite(death_screen_group)
menu_death_screen_button.image = load_image('data/images/interface/death_screen/menu_button.png')
menu_death_screen_button.rect = menu_death_screen_button.image.get_rect()
menu_death_screen_button.rect.x = WIDTH // 2 + menu_death_screen_button.image.get_width() // 2 + 20
menu_death_screen_button.rect.y = HEIGHT // 4 * 3

background_win_sreen = load_image('data/images/interface/win_screen/background.png')
menu_win_screen_button = pygame.sprite.Sprite(win_screen_group)
menu_win_screen_button.image = load_image('data/images/interface/win_screen/menu_button.png')
menu_win_screen_button.rect = menu_win_screen_button.image.get_rect()
menu_win_screen_button.rect.x = WIDTH // 2 - menu_win_screen_button.image.get_width() // 2
menu_win_screen_button.rect.y = HEIGHT // 2 * 3 - menu_win_screen_button.image.get_height() // 2

bar_inventory_image = load_image('data/images/interface/inventory/bar/0.png')
select_bar_inventory_image = load_image('data/images/interface/inventory/select_bar/0.png')

first_level_music = pygame.mixer.music.load('data/music/first_level.mp3')
pygame.mixer.music.play(-1)


class Score:
    def __init__(self):
        self.score = 0.0
        self.exp = 0.0
        self.level = 1

    def add_score(self, value, coef):
        if coef == 0.0:
            self.score += value

            self.exp += value
        else:
            self.score += value * coef

            self.exp += value * coef

        self.check_level()

    def check_level(self):
        exp = self.exp

        if exp > 100:
            exp -= 100

            self.level += 1

        else:
            pass

        self.exp = exp

    def remove_score(self, value):
        self.score -= value


class Tile(pygame.sprite.Sprite):
    def __init__(self, image, pos_x, pos_y, tile_width, tile_height, layer=None):
        super().__init__(tiles_group, all_sprites)
        self.image = image
        if layer == 1:
            self.rect = pygame.Rect(pos_x, pos_y, tile_width, tile_height // 5)
        else:
            self.rect = pygame.Rect(pos_x, pos_y, tile_width, tile_height - 3)


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(border_group, all_sprites)
        if x1 == x2:
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


def terminate():
    pygame.quit()
    sys.exit()


projectile_frame = load_image('data/images/items/projectile/projectile.png').convert_alpha()


class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, step, direction, shooter, detonate_frames=None):
        pygame.sprite.Sprite.__init__(self)
        self.frames = [projectile_frame]
        self.detonate_frames = detonate_frames
        self.image = projectile_frame
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.start_x = pos_x
        self.d = 0
        if step == 'up':
            self.dx = 0
            self.dy = -8
            self.dn = 1
        elif step == 'down':
            self.dx = 0
            self.dy = 8
            self.dn = 1
        elif step == 'right':
            self.dx = 8
            self.dy = 0
            self.dn = 1
        elif step == 'left':
            self.dx = -8
            self.dy = 0
            self.dn = -1
        self.imnum = 1
        self.damage = 1
        self.shooter = shooter

    def update(self):
        self.imnum += self.dn
        center = self.rect.center
        if self.detonate_frames and self.d >= 96:
            self.frames = self.detonate_frames
        if self.imnum > len(self.frames):
            self.imnum = 1
        elif self.imnum < 0:
            self.imnum = len(self.frames)
        self.image = self.frames[self.imnum - 1]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=center)
        self.rect.x += self.dx * 2.25
        self.rect.y += self.dy * 2.25
        self.d += 8
        if self.d >= 192:
            self.kill()
        for wall in wall_group:
            if pygame.sprite.collide_mask(wall, self):
                self.kill()
        if self.rect.colliderect(player.rect):
            player.base_health.received_hit()
            self.kill()


projectiles = pygame.sprite.Group()


class Boss(pygame.sprite.Sprite):
    def __init__(self, hero, pos_x, pos_y, scale):  # инициализация объекта класса Босс. передача аргумента гг
        super().__init__(boss_group, all_sprites)
        self.image = enemy_image
        self.scale = scale
        self.fall_y = 0
        self.in_air = False
        self.sight = 0
        self.attack_cooldown = 1
        self.moving = 'left'
        self.platform_check = False
        self.dash_speed = 0
        self.idle = False
        self.cur_animation = 0
        self.cur_frame = 0
        self.animation_list = []
        self.animation_cooldown = 0
        self.invulnerable_timer = 0
        self.target_x = 0
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.image = pygame.transform.scale(self.image, (self.width * self.scale, self.height * self.scale))
        self.rect = self.image.get_rect().move(
            pos_x, pos_y)
        self.base_health = Health(20)
        self.soul = Soul(0.5)
        self.charge = 0.0
        self.long_shot_cd = 0
        self.dead_cond = False
        self.hero = hero
        self.attack_buff = False
        animation_types = ['idle', 'run', 'attack_1', 'attack_2', 'death']
        for animation in animation_types:
            cur_animations_lst = []
            n = len(os.listdir(f'./data/images/entities/final_boss/{animation}'))
            for i in range(n):
                img = pygame.image.load(f'data/images/entities/final_boss/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img,
                                             (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
                cur_animations_lst.append(img)
            self.animation_list.append(cur_animations_lst)

    def deal_damage(self):  # Босс получил урон. Первая функция убирает одно хп, вторая - проверяет, мертв ли босс
        if self.invulnerable_timer == 0:
            self.base_health.received_hit()
            self.invulnerable_timer = FPS
        self.check_death_state()

    def give_short_damage(self):  # Босс наносит удар с близкого расстояния (ближний бой)
        self.soul.given_hit()

        if self.soul.soul_state is True:
            should_crit = True if randint(1, 2) == 10 else False

            if should_crit:
                self.hero.base_health.received_hit()
                self.hero.base_health.received_hit()
                self.soul.reset()
            else:
                self.hero.base_health.received_hit()
        else:
            self.hero.base_health.received_hit()
        self.hero.base_health.received_hit()
        self.charge_long_distance_shot()

    def give_long_damage(self):  # Босс наносит удар с дальнего расстояния (дальний бой)
        if self.long_shot_cd >= 1:
            hero_x = self.hero.rect.x
            self.target_x = hero_x
            sight = (self.target_x - self.rect.x)
            print(sight)
            if sight > 0:
                projectile = Projectile(self.rect.x + 35, self.rect.y + 50, 'right', None, self)
                all_sprites.add(projectile)
                projectiles.add(projectile)
            else:
                projectile = Projectile(self.rect.x - 35, self.rect.y + 50, 'left', None, self)
                all_sprites.add(projectile)
                projectiles.add(projectile)
            self.long_shot_cd = 0
        else:
            self.long_shot_cd += 0.015

        #  лонгшот должен отличаться от обычного удара и надо его эпик его нарисовать  #

    def charge_long_distance_shot(self):  # После нанесения урона вблизи, босс регенерирует возможность лонгшота
        self.charge += 25

    def is_dead(self):  # Геттер состояния босса
        return self.dead_cond

    def death_condition_met(self):  # Функция, которая вызывается при положительной проверке на смерть (выбор,
        # нужно ли что-либо дропать, также добавления очков и экспы игроку)
        print('Enemy (type=Boss) is dead.')

        should_drop_anything = None

        if randint(1, 10) == 1:
            should_drop_anything = True

        else:
            should_drop_anything = False
        self.kill()

        print("Death of Boss validated. Deleting boss.")

        del self

    def give_hero_score(self):  # Функция которая дает гг опыт и очки за победу над боссом
        basic_value = 100

        self.hero.exp.add_score(basic_value)

    def check_death_state(self):  # Функция, которая проверяет, жив ли босс
        hp = []

        for i in range(len(self.base_health.base_health)):
            hp.append(self.base_health.base_health[i])

        hp_set = set(hp)

        if hp_set == {0}:
            self.dead_cond = True

            print('Boss death condition met! Initiating basic response to death -> defcon method')

            self.death_condition_met()

        else:
            print('Boss is still alive.')

    def attack(self):
        self.give_short_damage()

    def move(self):
        dx = 0
        dy = 0
        hero_x = self.hero.rect.x
        self.target_x = hero_x
        self.rect.x += (self.target_x - self.rect.x) * 0.015
        if self not in enemy_group:
            print('s')
            return

        if randint(1, 100) == 1:
            self.idle = True
        if not self.idle:
            if randint(1, 50) == 1:
                self.moving = choice(['left', 'right'])
            if self.moving == 'left' and not self.dash_speed:
                dx = -STEP * 0.4
                self.sight = 1
            elif self.moving == 'right' and not self.dash_speed:
                dx = STEP * 0.4
                self.sight = 0
        if self.idle:
            if randint(1, 30) == 1:
                self.idle = False
        if abs(self.target_x - self.rect.x) >= 25 and self in enemy_group:
            self.give_long_damage()
            self.hero.invulnerable_timer = FPS
        # добавляем g (гравитацию)
        self.fall_y += GRAVITY
        if self.fall_y > 11:
            self.fall_y = 11
        dy += self.fall_y

        if self.dash_speed:
            self.fall_y = 0
            dx += 2 * self.dash_speed
            if self.sight:
                self.dash_speed += 0.5
            else:
                self.dash_speed -= 0.5

        # check current animation
        if self.idle:
            self.cur_animation = 0
        if dx != 0:
            self.cur_animation = 1
        if self.dash_speed or self.attack_cooldown < 0.2:
            self.cur_animation = 2
            # в этом состоянии моб должен бить гг

        # смотрим коллайды по x
        self.rect.x += dx
        if pygame.sprite.spritecollideany(self, platform_group):
            if dy > 0:
                self.rect.x -= dx
        if pygame.sprite.spritecollideany(self, wall_group) or pygame.sprite.spritecollideany(self,
                                                                                              vertical_borders) or \
                pygame.sprite.spritecollideany(self, enemy_borders):
            self.rect.x -= dx
            if self.moving == 'right':
                self.moving = 'left'
                self.sight = 1
            else:
                self.moving = 'right'
                self.sight = 0

        rect_l = pygame.Rect(self.rect[0] - self.width * 6, self.rect[1], self.width * 6, self.height)
        rect_r = pygame.Rect(self.rect[0] + self.width * 6, self.rect[1], self.width * 6, self.height)
        if self.hero.rect.colliderect(rect_l) and self.attack_cooldown >= 1 and self in enemy_group and randint(1,
                                                                                                                5) == 1:
            print('Моб атакует по левой стороне')
            self.in_attack = True
            self.sight = 1
            self.attack_dash(-1)
        if self.hero.rect.colliderect(rect_r) and self.attack_cooldown >= 1 and self in enemy_group and randint(1,
                                                                                                                5) == 1:
            print('Моб атакует по правой стороне')
            self.in_attack = True
            self.sight = 0
            self.attack_dash(1)

        # смотрим коллайды по y (где-то и по х, и по у)
        self.rect.y += dy

        if pygame.sprite.spritecollideany(self, player_group):
            if self.invulnerable_timer == 0 and (self.hero.dash_speed or self.hero.jump_on_enemy):
                self.deal_damage()
                self.invulnerable_timer = FPS * 0.5
                print('мобу наносится урон')
            elif self.hero.invulnerable_timer == 0 and not self.hero.dash_speed and self in enemy_group:
                self.attack()
                self.hero.invulnerable_timer = FPS
                print('гг наносится урон')
            self.hero.jump_on_enemy = False

        if pygame.sprite.spritecollideany(self, horizontal_borders):
            for i in self.base_health.base_health:
                if i == 1:
                    self.base_health.received_hit()

        if pygame.sprite.spritecollideany(self, wall_group):
            if dy < 0:
                # персонаж стукается головой об стену
                self.rect.y -= (dy + 0.1)
                self.fall_y = 0
            if dy > 0:
                # коллайд с землей
                self.jump_count = 0
                self.rect.y -= (dy + 0.1)
                self.fall_y = 0
                self.in_air = False
        else:
            if not pygame.sprite.spritecollideany(self, ladder_group) and not (
                    pygame.sprite.spritecollideany(self, platform_group)):
                self.in_air = True
                self.platform_check = False

        if pygame.sprite.spritecollideany(self, platform_group):
            flag = 0
            if dy > 0 and not self.platform_check:
                self.in_air = False
                self.rect.y -= (dy + 0.1)
                self.fall_y = 0
                self.jump_count = 0
                flag = 1
            if not flag:
                self.platform_check = True

        if pygame.sprite.spritecollideany(self, trap_group):
            self.fall_y = -11  # отскок от шипа (как прыжок)
            if self.invulnerable_timer == 0:
                self.base_health.received_hit()
                self.invulnerable_timer = FPS

        if self.attack_cooldown < 1:
            self.attack_cooldown += 0.005

        self.update()

    def update(self):
        # отрисовка спрайтов моба
        try:
            if self.animation_cooldown >= 1:
                self.image = self.animation_list[self.cur_animation][self.cur_frame]
                if self.sight:
                    self.image = pygame.transform.flip(self.image, 1, 0)
                self.cur_frame += 1
                if self.cur_frame >= len(self.animation_list[self.cur_animation]):
                    self.cur_frame = 0
                    self.animation_cooldown = 0
            else:
                if self.cur_animation == 2:
                    self.animation_cooldown += 0.08
                else:
                    self.animation_cooldown += 0.08
            if self.invulnerable_timer > 0:
                self.invulnerable_timer -= 1
        except Exception:
            self.cur_frame = 0

    def attack_dash(self, n):
        self.attack_cooldown = 0
        self.dash_speed = 8 * n


class MiniBoss(pygame.sprite.Sprite):
    def __init__(self, hero, pos_x, pos_y, scale):  # инициализация объекта класса Минибосс. передача аргумента гг
        super().__init__(mini_boss_group, all_sprites)
        self.image = mini_boss_image
        self.scale = scale
        self.fall_y = 0
        self.in_air = False
        self.sight = 0
        self.dash_cooldown = True
        self.dash_speed = 0
        self.n_dash = 1
        self.jump_count = 0
        self.platform_check = True
        self.cur_animation = 0
        self.cur_frame = 0
        self.animation_list = []
        self.animation_cooldown = 0
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.image = pygame.transform.scale(self.image, (self.width * self.scale, self.height * self.scale))
        self.rect = self.image.get_rect().move(
            pos_x, pos_y)

        self.base_health = Health(10)
        self.soul = Soul(0.33)
        self.charge = 0.0
        self.dead_cond = False
        self.hero = hero

        animation_types = ['idle', 'run']
        for animation in animation_types:
            cur_animations_lst = []
            n = len(os.listdir(f'./data/images/entities/mini_boss/{animation}'))
            for i in range(n):
                img = pygame.image.load(f'data/images/entities/mini_boss/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img,
                                             (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
                cur_animations_lst.append(img)
            self.animation_list.append(cur_animations_lst)

    def update(self):
        try:
            if self.animation_cooldown >= 1:
                self.image = self.animation_list[self.cur_animation][self.cur_frame]
                if self.sight:
                    self.image = pygame.transform.flip(self.image, 1, 0)
                self.cur_frame += 1
                if self.cur_frame >= len(self.animation_list[self.cur_animation]):
                    self.cur_frame = 0
                self.animation_cooldown = 0
            else:
                self.animation_cooldown += 0.12
        except Exception:
            self.cur_frame = 0

    def deal_damage(self):  # Минибосс получил урон. Первая функция убирает одно хп, вторая - проверяет, мертв ли он
        self.base_health.received_hit()

        self.check_death_state()

    def give_short_damage(self):  # Минибосс наносит удар с близкого расстояния (ближний бой)
        self.soul.given_hit()

        if self.soul.soul_state is True:
            should_crit = True if randint(1, 10) == 10 else False

            if should_crit:
                self.hero.base_health.received_hit()
                self.hero.base_health.received_hit()
                self.soul.reset()
            else:
                self.hero.base_health.received_hit()
        else:
            self.hero.base_health.received_hit()

        self.charge_long_distance_shot()

    def give_long_damage(self):  # Минибосс наносит удар с дальнего расстояния (дальний бой)
        if self.charge == 100:
            self.soul.given_hit()

            if self.soul.soul_state is True:
                should_crit = True if randint(1, 10) == 10 else False

                if should_crit:
                    self.hero.base_health.received_hit()
                    self.hero.base_health.received_hit()
                    self.soul.reset()
                else:
                    self.hero.base_health.received_hit()
            else:
                self.hero.base_health.received_hit()
            self.charge = 0.0
        else:
            print('Not charged yet.')

        #  лонгшот должен отличаться от обычного удара и надо его эпик его нарисовать

    def charge_long_distance_shot(self):  # После нанесения урона вблизи, минибосс регенерирует возможность лонгшота
        self.charge += 25

    def is_dead(self):  # Геттер состояния смерти минибосса
        return self.dead_cond

    def death_condition_met(self):  # Функция, которая вызывается при положительной проверке на смерть (выбор,
        # нужно ли что-либо дропать, также добавления очков и экспы игроку)
        print('Enemy (type=Miniboss) is dead.')

        should_drop_anything = None

        if randint(1, 10) == 1:
            should_drop_anything = True

        else:
            should_drop_anything = False

        if should_drop_anything:
            self.drop_items()

        self.give_hero_score()

        print("Death of miniboss validated. Deleting miniboss.")

        del self

    def drop_items(self):  # Функция которая отвечает за дроп предмета из минибосса
        item = None  # выберите рандомный айтем и присвойте его этой переменной

        # киньте этот айтем на поле и дайте игроку возможность его подобрать и пусть игрок подбирает

    def give_hero_score(self):  # Функция которая дает гг опыт и очки за победу над минибосса
        basic_value = randint(25, 40)

        self.hero.exp.add_score(basic_value)

    def check_death_state(self):  # Функция, которая проверяет, жив ли минибосс
        hp = []

        for i in range(len(self.base_health.base_health)):
            hp.append(self.base_health.base_health[i])

        hp_set = set(hp)

        if hp_set == {0}:
            self.dead_cond = True

            print('Mini boss death condition met! Initiating basic response to death -> defcon method')

            self.death_condition_met()

        else:
            print('Mini boss is still alive.')


class Enemy(pygame.sprite.Sprite):
    def __init__(self, hero, pos_x, pos_y, scale):
        super().__init__(enemy_group, all_sprites)
        self.image = enemy_image
        self.scale = scale
        self.fall_y = 0
        self.in_air = False
        self.sight = 0
        self.moving = 'left'
        self.attack_cooldown = 1
        self.dash_speed = 0
        self.idle = False
        self.cur_animation = 0
        self.cur_frame = 0
        self.animation_list = []
        self.animation_cooldown = 0
        self.invulnerable_timer = 0
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.image = pygame.transform.scale(self.image, (self.width * self.scale, self.height * self.scale))
        self.rect = self.image.get_rect().move(
            pos_x, pos_y)
        self.base_health = Health(3)
        self.soul = Soul(0.1)
        self.dead_cond = False
        self.hero = hero
        self.attack_buff = False
        animation_types = ['idle', 'run', 'attack']
        for animation in animation_types:
            cur_animations_lst = []
            n = len(os.listdir(f'./data/images/entities/enemy/{animation}'))
            for i in range(n):
                img = pygame.image.load(f'data/images/entities/enemy/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img,
                                             (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
                cur_animations_lst.append(img)
            self.animation_list.append(cur_animations_lst)

    def deal_damage(self):
        if self.invulnerable_timer == 0:
            self.base_health.received_hit()
            self.invulnerable_timer = FPS
        self.check_death_state()

    def give_damage(self):
        self.soul.given_hit()

        if self.soul.soul_state is True:
            should_crit = True if randint(1, 10) == 10 else False

            if should_crit:
                self.hero.base_health.received_hit()
                self.hero.base_health.received_hit()
                self.soul.reset()
            else:
                self.hero.base_health.received_hit()
        else:
            self.hero.base_health.received_hit()

    def is_dead(self):
        return self.dead_cond

    def death_condition_met(self):
        print('Enemy (type=Enemy) is dead.')

        should_drop_anything = None

        if randint(1, 10) == 1:
            should_drop_anything = True
        else:
            should_drop_anything = False

        if should_drop_anything:
            self.drop_items()

        print("Death of enemy validated. Deleting entity.")
        self.kill()
        del self

    def drop_items(self):
        item = None

    def give_hero_score(self):
        basic_value = randint(10, 25)

        self.hero.exp.add_score(basic_value)

    def check_death_state(self):
        hp = []

        for i in range(len(self.base_health.base_health)):
            hp.append(self.base_health.base_health[i])

        hp_set = set(hp)

        if hp_set == {0}:
            self.dead_cond = True

            print('Enemy death condition met! Initiating basic response to death -> defcon method')

            self.death_condition_met()

        else:
            print('Enemy is still alive.')

    def move(self):
        dx = 0
        dy = 0

        if randint(1, 100) == 1:
            self.idle = True
        if not self.idle:
            if randint(1, 50) == 1:
                self.moving = choice(['left', 'right'])
            if self.moving == 'left' and not self.dash_speed:
                dx = -STEP * 0.4
                self.sight = 1
            elif self.moving == 'right' and not self.dash_speed:
                dx = STEP * 0.4
                self.sight = 0
        if self.idle:
            if randint(1, 30) == 1:
                self.idle = False

        # добавляем g (гравитацию)
        self.fall_y += GRAVITY
        if self.fall_y > 11:
            self.fall_y = 11
        dy += self.fall_y

        if self.dash_speed:
            self.fall_y = 0
            dx += 2 * self.dash_speed
            if self.sight:
                self.dash_speed += 0.5
            else:
                self.dash_speed -= 0.5

        # check current animation
        if self.idle:
            self.cur_animation = 0
        if dx != 0:
            self.cur_animation = 1
        if self.dash_speed or self.attack_cooldown < 0.2:
            self.cur_animation = 2
            # в этом состоянии моб должен бить гг

        # смотрим коллайды по x
        self.rect.x += dx
        if pygame.sprite.spritecollideany(self, platform_group):
            if dy > 0:
                self.rect.x -= dx
        if pygame.sprite.spritecollideany(self, wall_group) or pygame.sprite.spritecollideany(self,
                                                                                              vertical_borders) or pygame.sprite.spritecollideany(
                self, enemy_borders):
            self.rect.x -= dx
            if self.moving == 'right':
                self.moving = 'left'
                self.sight = 1
            else:
                self.moving = 'right'
                self.sight = 0

        rect_l = pygame.Rect(self.rect[0] - self.width * 6, self.rect[1], self.width * 6, self.height)
        rect_r = pygame.Rect(self.rect[0] + self.width * 6, self.rect[1], self.width * 6, self.height)
        if self.hero.rect.colliderect(rect_l) and self.attack_cooldown >= 1 and self in enemy_group and randint(1, 5) == 1:
            print('Моб атакует по левой стороне')
            self.in_attack = True
            self.sight = 1
            self.attack_dash(-1)
        if self.hero.rect.colliderect(rect_r) and self.attack_cooldown >= 1 and self in enemy_group and randint(1, 5) == 1:
            print('Моб атакует по правой стороне')
            self.in_attack = True
            self.sight = 0
            self.attack_dash(1)

        # смотрим коллайды по y (где-то и по х, и по у)
        self.rect.y += dy

        if pygame.sprite.spritecollideany(self, player_group):
            if self.invulnerable_timer == 0 and (self.hero.dash_speed or self.hero.jump_on_enemy):
                self.deal_damage()
                self.invulnerable_timer = FPS * 0.5
                print('мобу наносится урон')
            elif self.hero.invulnerable_timer == 0 and not self.hero.dash_speed and self in enemy_group:
                self.hero.base_health.received_hit()
                self.hero.invulnerable_timer = FPS
                print('гг наносится урон')
            self.hero.jump_on_enemy = False

        if pygame.sprite.spritecollideany(self, horizontal_borders):
            for i in self.base_health.base_health:
                if i == 1:
                    self.base_health.received_hit()

        if pygame.sprite.spritecollideany(self, wall_group):
            if dy < 0:
                # персонаж стукается головой об стену
                self.rect.y -= (dy + 0.1)
                self.fall_y = 0
            if dy > 0:
                # коллайд с землей
                self.jump_count = 0
                self.rect.y -= (dy + 0.1)
                self.fall_y = 0
                self.in_air = False
        else:
            if not pygame.sprite.spritecollideany(self, ladder_group) and not (
                    pygame.sprite.spritecollideany(self, platform_group)):
                self.in_air = True
                self.platform_check = False

        if pygame.sprite.spritecollideany(self, platform_group):
            flag = 0
            if dy > 0 and not self.platform_check:
                self.in_air = False
                self.rect.y -= (dy + 0.1)
                self.fall_y = 0
                self.jump_count = 0
                flag = 1
            if not flag:
                self.platform_check = True

        if pygame.sprite.spritecollideany(self, trap_group):
            self.fall_y = -11  # отскок от шипа (как прыжок)
            if self.invulnerable_timer == 0:
                self.base_health.received_hit()
                self.invulnerable_timer = FPS

        if self.attack_cooldown < 1:
            self.attack_cooldown += 0.005

        self.update()

    def update(self):
        # отрисовка спрайтов моба
        try:
            if self.animation_cooldown >= 1:
                self.image = self.animation_list[self.cur_animation][self.cur_frame]
                if self.sight:
                    self.image = pygame.transform.flip(self.image, 1, 0)
                self.cur_frame += 1
                if self.cur_frame >= len(self.animation_list[self.cur_animation]):
                    self.cur_frame = 0
                    self.animation_cooldown = 0
            else:
                self.animation_cooldown += 0.08

            if self.invulnerable_timer > 0:
                self.invulnerable_timer -= 1
        except Exception:
            self.cur_frame = 0

    def attack_dash(self, n):
        self.attack_cooldown = 0
        self.dash_speed = 8 * n



class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, scale):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.scale = scale
        self.invulnerable_timer = 0
        self.fall_y = 0
        self.in_air = False
        self.sight = 0
        self.dash_cooldown = True
        self.dash_speed = 0
        self.n_dash = 1
        self.jump_count = 0
        self.platform_check = True
        self.cur_animation = 0
        self.cur_frame = 0
        self.animation_list = []
        self.item_cd = 0
        self.jump_on_enemy = False
        self.exp = Score()
        self.animation_cooldown = 0
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.image = pygame.transform.scale(self.image, (self.width * self.scale, self.height * self.scale))
        self.rect = self.image.get_rect().move(
            pos_x, pos_y)

        self.base_health = Health(5)
        self.soul = Soul(0.25)
        self.exp = Score()
        self.attack_buff = False
        self.items = {'medical': [], 'attack': [], 'defense': [], 'soul': [], 'key': [], 'misc': []}
        self.chosen_item = None

        animation_types = ['idle', 'run', 'jump', 'in_air', 'climb', 'dash']
        for animation in animation_types:
            cur_animations_lst = []
            n = len(os.listdir(f'./data/images/entities/player/{animation}'))
            for i in range(n):
                img = pygame.image.load(f'data/images/entities/player/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img,
                                             (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
                cur_animations_lst.append(img)
            self.animation_list.append(cur_animations_lst)

    #   print(self.animation_list)

    def used_medical_item(self, item):
        print('asdasd')
        self.base_health.restore_health(self)

        item_id = item.id

        index = 0
        for i in range(len(self.items['medical'])):
            if item_id == self.items['medical'][i].id:
                index = i

        self.items['medical'].pop(index)
        print(self.items)

    def used_soul_item(self, item):
        item_name = item.name

        if item_name == "increment":
            self.soul.usual_increment += 0.25
        elif item_name == 'base_charge':
            self.soul.charged()

        item_id = item.id

        index = 0
        for i in range(len(self.items['soul'])):
            if item_id == self.items['soul'][i].id:
                index = i

        self.items['soul'].pop(index)

    def used_misc_item(self, item):
        print("Can't use misc items.")

    def picked_up_item(self, item):
        print('I picked up item')
        if item.type == 'medical':
            self.items['medical'].append(item)

        elif item.type == 'attack':
            self.items['attack'].append(item)

        elif item.type == 'defense':
            self.items['defense'].append(item)

        elif item.type == 'soul':
            self.items['soul'].append(item)

        elif item.type == 'key':
            self.items['key'].append(item)

        else:
            self.items['misc'].append(item)
        print(self.items)

    def move(self, moving_left, moving_right, jump, moving_down, dash):

        # Расстояние, пройденное персонажем в один тик
        dx = 0
        dy = 0

        if moving_left:
            dx = -STEP
            self.sight = 1
        if moving_right:
            dx = STEP
            self.sight = 0

        # jump / double jump
        global double_jump_unlock, double_jump_check
        if (jump and not self.in_air) or (jump and double_jump_check and double_jump_unlock and self.in_air):
            if self.jump_count <= 1:
                self.jump_count += 1
                self.fall_y = -11
                double_jump_check = False

        # dash
        if dash and self.dash_cooldown and self.n_dash >= 1:
            if self.sight:
                self.dash_speed = -7
            else:
                self.dash_speed = 7
            self.dash_cooldown = False
            self.n_dash = 0
        if self.n_dash < 1:
            self.n_dash += 0.025

        if self.dash_speed:
            dx, dy = 0, 0
            self.fall_y = 0
            dx += STEP * self.dash_speed
            if self.sight:
                self.dash_speed += 1
            else:
                self.dash_speed -= 1

        # check current animation
        if dx == 0 and not self.in_air:
            self.cur_animation = 0
        if moving_left or moving_right:
            self.cur_animation = 1
        if self.in_air:
            self.cur_animation = 3
        if jump and not self.in_air:
            self.cur_animation = 2
        if self.dash_speed or self.n_dash <= 0.4:
            self.cur_animation = 5

        # добавляем g (гравитацию)
        self.fall_y += GRAVITY
        if self.fall_y > 11:
            self.fall_y = 11

        dy += self.fall_y

        # смотрим коллайды по x
        self.rect.x += dx

        if pygame.sprite.spritecollideany(self, platform_group):
            if dy > 0:
                self.rect.x -= dx

        if pygame.sprite.spritecollideany(self, wall_group) or pygame.sprite.spritecollideany(self, vertical_borders):
            self.rect.x -= dx

        # смотрим коллайды по y
        self.rect.y += dy

        if pygame.sprite.spritecollideany(self, horizontal_borders):
            for i in self.base_health.base_health:
                if i == 1:
                    self.received_hit()

        if pygame.sprite.spritecollideany(self, enemy_group):
            if dy > 0.5:
                self.fall_y = -11
                self.jump_on_enemy = True


        if pygame.sprite.spritecollideany(self, ladder_group):
            self.jump_count = 0
            self.fall_y = 0
            self.in_air = False
            self.dash_cooldown = True
            self.rect.y -= dy + 0.1
            if not moving_down:
                if jump:
                    self.fall_y = -11
                    self.rect.y -= STEP * 0.6
                    self.cur_animation = 4
                    if pygame.sprite.spritecollideany(self, wall_group):
                        self.rect.y -= STEP * 0.6
                else:
                    self.cur_animation = 0
            else:
                self.rect.y += STEP * 0.6
                self.cur_animation = 4
                if pygame.sprite.spritecollideany(self, wall_group):
                    self.rect.y -= STEP * 0.6

        if pygame.sprite.spritecollideany(self, wall_group):
            if dy < 0:
                # персонаж стукается головой об стену
                self.rect.y -= (dy + 0.1)
                self.fall_y = 0
            if dy > 0:
                # коллайд с землей
                self.jump_count = 0
                if not self.dash_speed:
                    self.dash_cooldown = True
                self.rect.y -= (dy + 0.1)
                self.fall_y = 0
                self.in_air = False
        else:
            if not pygame.sprite.spritecollideany(self, ladder_group) and not (
                    pygame.sprite.spritecollideany(self, platform_group)):
                self.in_air = True
                self.platform_check = False

        if pygame.sprite.spritecollideany(self, platform_group):
            flag = 0
            if dy > 0 and not self.platform_check:
                self.in_air = False
                self.rect.y -= (dy + 0.1)
                self.fall_y = 0
                self.jump_count = 0
                if not self.dash_speed:
                    self.dash_cooldown = True
                flag = 1
            if not flag:
                self.platform_check = True

        if pygame.sprite.spritecollideany(self, trap_group) and self.dash_speed == 0:
            self.fall_y = -11  # отскок от шипа (как прыжок)
            if self.invulnerable_timer == 0:
                self.base_health.received_hit()
                self.invulnerable_timer = FPS
            # функционал работает мега криво и кринжово, надо что-то придумать

        if pygame.sprite.spritecollideany(self, exit_group):
            for i in all_sprites:
                i.kill()
            global player, item, level_count
            level_count += 1
            player, item = generate_level(file_name2, level_count)

        # print(self.in_air)
        # print(self.fall_y)
        #print(self.jump_on_enemy)

        self.update()

    def update(self):
        # отрисовка спрайтов игрока
        try:
            if self.animation_cooldown >= 1:
                self.image = self.animation_list[self.cur_animation][self.cur_frame]
                if self.sight:
                    self.image = pygame.transform.flip(self.image, 1, 0)
                self.cur_frame += 1
                if self.cur_frame >= len(self.animation_list[self.cur_animation]):
                    self.cur_frame = 0
                self.animation_cooldown = 0
            else:
                self.animation_cooldown += 0.12
            if self.invulnerable_timer > 0:
                self.invulnerable_timer -= 1
        except Exception:
            self.cur_frame = 0

        if self.dash_speed:
            self.animation_cooldown = 1
            self.cur_animation = 5

    def restore_health(self):
        self.base_health.restore_health(self)

    def damage(self, enemy):
        self.soul.given_hit()

        if self.soul.soul_state is True:
            should_crit = True if randint(1, 10) == 10 else False

            if should_crit:
                enemy.deal_damage()
                enemy.deal_damage()
                self.soul.reset()
            else:
                enemy.deal_damage()
        else:
            enemy.deal_damage()

            if self.attack_buff:
                enemy.deal_damage()
                self.attack_buff = False

        self.exp.add_score(25, 1)

    def received_hit(self):
        self.base_health.received_hit()

    def used_defensive_item(self, item):
        times = item.def_value

        for i in range(times):
            self.base_health.add_health()
            print(player.base_health.base_health)
        item_id = item.id

        index = 0
        for i in range(len(self.items['defense'])):
            if item_id == self.items['defense'][i].id:
                index = i

        self.items['defense'].pop(index)

    def used_attack_item(self, item):
        self.attack_buff = True

        item_id = item.id

        index = 0
        for i in range(len(self.items['attack'])):
            if item_id == self.items['attack'][i].id:
                index = i

        self.items['attack'].pop(index)

    def update_cd(self):
        self.item_cd += 1

    def used_key(self, key):
        global push_event
        self.update_cd()
        print('sa')
        if key and push_event and self.item_cd == 1:
            self.items['key'].pop(-1)
            # открытие сундука, поздравление игрока
            push_event = False
            return True

        else:
            print(key, push_event, self.item_cd)
            print("Can't use key here. There are no chests nearby.")
            return None

    def can_use_key(self):
        return True if self.chosen_item == 'key' else False


class HealthBar(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__(all_sprites)
        self.image = pygame.image.load('./data/images/interface/healthbar/hp_active/0.png')
        self.player = player
        self.cur_hp = player.base_health.base_health
        self.scale = 2
        self.animation_list = []
        self.animation_cooldown = 1
        self.cur_animation = 0
        self.cur_frame = 0
        self.rect = self.image.get_rect()
        self.pos_x = player.rect.x
        self.pos_y = player.rect.y

        animation_types = ['hp_inactive', 'hp_active', 'hp_damage', 'hp_heal']
        for animation in animation_types:
            cur_animations_lst = []
            n = len(os.listdir(f'./data/images/interface/healthbar/{animation}'))
            for i in range(n):
                img = pygame.image.load(f'data/images/interface/healthbar/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img,
                                             (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
                cur_animations_lst.append(img)
            self.animation_list.append(cur_animations_lst)

    def update(self, target):
        self.cur_hp = player.base_health.base_health
        for i in range(len(self.cur_hp)):
            self.image = self.animation_list[self.cur_hp[i]][0]

            self.rect = self.image.get_rect()
            screen.blit(self.image, (-15 + 64 * i, -15))

            # без анимаций получения урона и хилла(((


new_item = None
'''player.used_key(res)
                    push_event = False
                    # Replace the treasure chest with a new item
                    item_choice = choice([-1, -2, -3, -4])
                    global new_item
                    new_item = WorldItem(item_choice, self.pos_x, self.pos_y, self.scale)
                    item_group.add(new_item)
                    self.kill()'''


class WorldItem(pygame.sprite.Sprite):
    def __init__(self, item_type, pos_x, pos_y, scale):
        super().__init__(item_group, all_sprites)
        self.item_type = item_type
        self.scale = scale
        self.item_lst = ['treasure', 'key', 'dash', 'double_jump', 'defence_item', 'medical_item', 'soul_item']
        self.animation_list_items = []
        self.cur_frame = 0
        self.animation_cooldown = 0
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.scale = scale
        self.type = ""
        for animation in self.item_lst:
            cur_animations_lst = []
            n = len(os.listdir(f'./data/images/items/{animation}'))
            for i in range(n):
                img = load_image((f'data/images/items/{animation}/{i}.png'), -1)
                img = pygame.transform.scale(img,
                                             (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
                cur_animations_lst.append(img)
            self.animation_list_items.append(cur_animations_lst)

        self.image = self.animation_list_items[self.item_type][self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.image.get_rect().move(
            pos_x, pos_y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        pygame.transform.scale(self.image, (self.width // 2, self.height // 2))

    def update(self):
        # функционал (гг находится рядом с предметом)
        global dash_unlock, double_jump_unlock, player
        if pygame.sprite.spritecollideany(self, player_group):
            if self.item_lst[self.item_type] == 'dash' and self in item_group:
                dash_unlock = True
                self.kill()
            if self.item_lst[self.item_type] == 'double_jump' and self in item_group:
                double_jump_unlock = True
                self.kill()
            if self.item_lst[self.item_type] == 'key' and self in item_group:
                # добавление ключа в инвентарь
                self.type = 'key'
                player.picked_up_item(self)
                self.kill()
            if self.item_lst[self.item_type] == 'medical_item' and self in item_group:
                self.type = 'medical'
                player.picked_up_item(self)
                self.kill()
            if self.item_lst[self.item_type] == 'defence_item' and self in item_group:
                self.type = 'defense'
                player.picked_up_item(self)
                self.kill()
            if self.item_lst[self.item_type] == 'soul_item' and self in item_group:
                self.type = 'soul'
                player.picked_up_item(self)
                self.kill()
            if self.item_lst[self.item_type] == 'treasure' and self in item_group:
                global push_event
                res = player.can_use_key()
                # коллайд с сундуком, вызов функции открытия
                if res and push_event:
                    player.used_key(res)  # игрок открыл сундук
                    d = {-1: 'medical', -2: 'defense', -3: 'soul', -4: 'double_jump'}
                    self.type = d[choice([-1, -2, -3, -4])]  # игроку выпал рандомный айтем и
                    # он моментально его подобрал (он не увидит что за айтем, пока не откроет инвентарь)
                    player.picked_up_item(self)  # игрок подобрал айтем
                    self.kill()
                    return

        # анимации айтемов на уровне
        try:
            if self.animation_cooldown >= 1:
                self.image = self.animation_list_items[self.item_type][self.cur_frame]
                self.cur_frame += 1
                if self.cur_frame >= len(self.animation_list_items[self.item_type]):
                    self.cur_frame = 0
                self.animation_cooldown = 0
            else:
                if self.item_type == 2:
                    self.animation_cooldown += 0.02
                else:
                    self.animation_cooldown += 0.15
        except Exception:
            self.cur_frame = 0


class Health:
    def __init__(self, amount):
        self.base_health = []

        for i in range(amount):
            self.base_health.append(1)

    def received_hit(self):
        for i in range(len(self.base_health) - 1, -1, -1):

            if self.base_health[i] == 1:

                self.base_health[i] = 0

                if set(self.base_health) == {0}:
                    print("Hero is dead.")
                #    player.kill()

                break

    def restore_health(self, hero):
            for i in range(len(self.base_health)):

                if self.base_health[i] == 0:
                    self.base_health[i] = 1
                    print(i)
                    hero.soul_state = False
                    break

    def add_health(self):
        self.base_health = [1] + self.base_health


class Soul:
    def __init__(self, usual_increment):
        self.soul_state = False
        self.soul_cond = 0.0
        self.usual_increment = usual_increment

    def given_hit(self):
        self.soul_cond += self.usual_increment
        if self.soul_cond >= 1:
            self.soul_cond = 1
            self.soul_state = True

    def reset(self):
        self.soul_state = False
        self.soul_cond = 0

    def charged(self):
        self.soul_state = True
        self.soul_cond = 1

class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.camera = pygame.Rect(0, 0, WIDTH, HEIGHT)

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        return obj.rect.move(self.camera.topleft)

    # позиционировать камеру на объекте target
    def update(self, target):
        x = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        y = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)
        x = min(0, x)  # Левая сторона
        y = min(0, y)  # Верхняя сторона
        if level_count == 0:
            SCALE = 6
        elif level_count == 2:
            SCALE = 3
        x = max(-(map.width * map.tilewidth * SCALE - WIDTH), x)  # Правая сторона
        y = max(-(map.height * map.tilewidth * SCALE - HEIGHT), y)  # Нижняя сторона

        self.camera = pygame.Rect(x, y, WIDTH, HEIGHT)


enemies = []


def generate_level(filename, LEVEL_COUNT):
    global map, all_sprites
    try:
        all_sprites = pygame.sprite.Group()
        if LEVEL_COUNT == 0:
            SCALE, scale_player, item_type = 6, 1.7, 2
        elif LEVEL_COUNT == 1:
            SCALE, scale_player, item_type = 6, 1.7, 3

        map = pytmx.load_pygame(filename)
        tile_size = map.tilewidth
        Border(0, map.height * tile_size * SCALE, map.width * tile_size * SCALE, map.height * tile_size * SCALE)
        Border(0, 0, 0, map.height * tile_size * SCALE)
        Border(map.width * tile_size * SCALE, 0, map.width * tile_size * SCALE, map.height * tile_size * SCALE)
        new_player = None
        new_items = []
        for layer in range(14):
            for y in range(map.height):
                for x in range(map.width):
                    image = map.get_tile_image(x, y, layer)
                    if image:
                        if layer == 11 or layer == 12 or layer == 4 or layer == 2 or layer == 6:
                            remove_bg_from_tiles(image)
                        temp = Tile(pygame.transform.scale(image, (tile_size * SCALE, tile_size * SCALE)),
                                    x * tile_size * SCALE,
                                    y * tile_size * SCALE, int(tile_size * SCALE), int(tile_size * SCALE), layer)
                        if layer == 10:
                            new_player = Player((x * tile_size * SCALE), (y * tile_size * SCALE), scale_player)
                        if layer == 9:
                            temp.add(enemy_borders)
                        if layer == 8:
                            temp.add(treasure_group)
                            new_items.append(WorldItem(0, (x * 8 * SCALE - 5), (y * 8 * SCALE - 5), 2.2))
                        if layer == 7:
                            new_items.append(WorldItem(1, (x * 8 * SCALE), (y * 8 * SCALE) - 50, 1))
                        if layer == 6:
                            new_items.append(WorldItem(item_type, (x * 8 * SCALE + 5), (y * 8 * SCALE) - 70, 4.5))
                        if layer == 5:
                            temp.add(exit_group)
                        if layer == 12 and LEVEL_COUNT == 0:
                            mini_boss = MiniBoss(new_player, x * 8 * SCALE, y * 8 * SCALE - 55,7)

                        if layer == 11 and LEVEL_COUNT == 0:
                            enemy = Enemy(new_player, x * 8 * SCALE, y * 8 * SCALE - 55, 2)
                            enemies.append(enemy)

                        if layer == 13:
                            boss = Boss(new_player, x * 8 * SCALE, y * 8 * SCALE - 70, 4)
                            enemies.append(boss)
                            enemy_group.add(boss)
                        if layer == 4:
                            temp.add(trap_group)
                        if layer == 3:
                            temp.add(wall_group)
                        if layer == 2:
                            temp.add(ladder_group)
                        if layer == 1:
                            temp.add(platform_group)
                        if layer == 0:
                            temp.add(background_group)
                        temp.add(all_sprites)
        print(1)
        return new_player, new_items
    except Exception as f:
        print(f)


def check_enemy_on_screen(enemy, target):
    x = (target.rect.x + target.rect.w // 2 - WIDTH // 2)
    y = (target.rect.y + target.rect.h // 2 - HEIGHT // 2)
    vision_rect = pygame.Rect(x - 200, y - 200, 1680, 1120)
    if enemy.rect.colliderect(vision_rect):
        enemy.move()


def stop_moving():
    global moving_left, moving_right, jump, moving_down, dash
    moving_left = False
    moving_right = False
    jump = False
    moving_down = False
    dash = False


def menu():
    pygame.mixer.music.stop()
    stop_moving()
    global menu_running, running
    while menu_running:
        screen.blit(background_menu_image, (0, 0))
        menu_sprite_group.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                menu_running = False
            if pygame.mouse.get_pressed()[0]:
                if start_menu_button.rect.collidepoint(event.pos):
                    menu_running = False
                    player, items = generate_level(file_name1, level_count)
                    hpBar = HealthBar(player)
                    pygame.mixer.music.play(-1)
                    return player, items, hpBar
        pygame.display.flip()


def death_screen():
    global death_screen_running, running, menu_running
    stop_moving()
    while death_screen_running:  # экран смерти
        screen.blit(background_death_screen, (0, 0))
        death_screen_group.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                death_screen_running = False
            if pygame.mouse.get_pressed()[0]:
                if restart_death_screen_button.rect.collidepoint(event.pos):
                    player, items = generate_level(file_name1, level_count)
                    hpBar = HealthBar(player)
                    death_screen_running = False
                    return player, items, hpBar
                if menu_death_screen_button.rect.collidepoint(event.pos):
                    menu_running = True
                    death_screen_running = False
        pygame.display.flip()


def win_screen():
    global win_screen_running, running, death_screen_running, menu_running
    stop_moving()
    while win_screen_running:  # финальный экран
        win_screen_group.draw(screen)
        font = pygame.font.Font(None, 50)
        text = font.render(f"SCORE: {player.exp}", True, (100, 255, 100))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, WIDTH // 2 - text.get_height() // 2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                death_screen_running = False
            if pygame.mouse.get_pressed()[0]:
                if menu_win_screen_button.rect.collidepoint(event.pos):
                    menu_running = True
                    win_screen_running = False
        pygame.display.flip()


def pause_screen():
    global pause_running, running, menu_running, moving_left, moving_right, jump, moving_down, dash
    while pause_running:
        screen.fill((0, 0, 0))
        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply(sprite))
        surf = pygame.Surface((WIDTH, HEIGHT))
        surf.fill((255, 255, 255))
        surf.set_alpha(100)
        pause_buttons_group.draw(screen)
        screen.blit(surf, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause_running = False
            if event.type == pygame.QUIT:
                running = False
                pause_running = False
            if pygame.mouse.get_pressed()[0]:
                if play_pause_button.rect.collidepoint(event.pos):
                    pause_running = False
                if menu_pause_button.rect.collidepoint(event.pos):
                    menu_running = True
                    pause_running = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    moving_left = False
                if event.key == pygame.K_d:
                    moving_right = False
                if event.key == pygame.K_SPACE or event.key == pygame.K_w:
                    jump = False
                if event.key == pygame.K_s:
                    moving_down = False
                if event.key == pygame.K_LSHIFT and dash_unlock:
                    dash = False
        pygame.display.flip()


a = {
    'medical': [load_image('data/images/items/medical_item/0.png', -1), pygame.Rect(WIDTH // 2, HEIGHT * 0.25, 95, 95)],
    'attack': [load_image('data/images/items/attack_item/0.png', -1), pygame.Rect(WIDTH // 2 + 95 + 2, HEIGHT * 0.25, 95, 95)],
    'defense': [load_image('data/images/items/defence_item/0.png', -1), pygame.Rect(WIDTH // 2 + 95 * 2 + 4, HEIGHT * 0.25, 95, 95)],
    'soul': [load_image('data/images/items/soul_item/0.png', -1), pygame.Rect(WIDTH // 2, HEIGHT * 0.25 + 95 + 2, 95, 95)],
    'key': [load_image('data/images/items/key_item/0.png', -1), pygame.Rect(WIDTH // 2 + 95 + 2, HEIGHT * 0.25 + 95 + 2, 95, 95)],
    'misc': [load_image('data/images/items/misc_item/0.png', -1), pygame.Rect(WIDTH // 2 + 95 * 2 + 4, HEIGHT * 0.25 + 95 + 2, 95, 95)]}


def inventory():
    global running, inventory_running, player
    inventory_running = True  # global inventory_running
    highlight = False
    stop_moving()
    rect = []
    while inventory_running:
        screen.fill((0, 0, 0))
        if highlight:
            screen.blit(select_bar_inventory_image, rect)
        for i in player.items.keys():
            if len(player.items[i]) > 0:
                screen.blit(a[i][0], a[i][1])
            screen.blit(bar_inventory_image, (a[i][1][0], a[i][1][1]))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                inventory_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    inventory_running = False
            if pygame.mouse.get_pressed()[0]:
                for i in a.keys():
                    if a[i][1].collidepoint(event.pos) and len(player.items[i]) > 0:
                        player.chosen_item = i
                        highlight = True
                        rect = a[i][1][0], a[i][1][1]

            pygame.display.flip()


if __name__ == '__main__':
    running = True
    menu_running = True
    camera = Camera()
    pause_running = False
    win_screen_running = False
    death_screen_running = False
    inventory_running = False
    room = 4
    while running:
        if menu_running:
            res = menu()
            if res:
                player, items, hpBar = res
        if sum(player.base_health.base_health) == 0 and running:
            death_screen_running = True
            res = death_screen()
            if res:
                player, items, hpBar = res
        if win_screen_running:
            win_screen()
        if inventory_running:
            inventory()
        screen.fill(pygame.Color("black"))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause_running = True
                pause_screen()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    moving_left = True
                if event.key == pygame.K_d:
                    moving_right = True
                if event.key == pygame.K_SPACE or event.key == pygame.K_w:
                    jump = True
                if event.key == pygame.K_s:
                    moving_down = True
                if event.key == pygame.K_LSHIFT and dash_unlock:
                    dash = True
                if event.key == pygame.K_f:
                    inventory_running = True
                    print('inventory')
                if event.key == pygame.K_e:
                    try:
                        push_event = True
                        if len(player.items[player.chosen_item]) > 0:
                            if player.chosen_item == 'medical':
                                player.used_medical_item(player.items[player.chosen_item][-1])
                            if player.chosen_item == 'attack':
                                player.used_attack_item(player.items[player.chosen_item][-1])
                            if player.chosen_item == 'defense':
                                player.used_defensive_item(player.items[player.chosen_item][-1])
                            if player.chosen_item == 'soul':
                                player.used_soul_item(player.items[player.chosen_item][-1])
                            if player.chosen_item == 'misc':
                                player.used_misc_item(player.items[player.chosen_item][-1])
                    except Exception:
                        push_event = False
                        print(player.items)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    moving_left = False
                if event.key == pygame.K_d:
                    moving_right = False
                if event.key == pygame.K_SPACE or event.key == pygame.K_w:
                    jump = False
                    double_jump_check = True
                if event.key == pygame.K_s:
                    moving_down = False
                if event.key == pygame.K_LSHIFT and dash_unlock:
                    dash = False
                if event.key == pygame.K_e:
                    push_event = False
                if event.type == pygame.K_f:
                    pass  # закрытие инвентаря

            if event.type == pygame.MOUSEMOTION:
                pass
        player.move(moving_left, moving_right, jump, moving_down, dash)
        camera.update(player)
        for i in items:
            i.update()
        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply(sprite))
        hpBar.update(player)
        for enemy in enemies:
            check_enemy_on_screen(enemy, player)
        if room >= 3:
            projectiles.update()
            room = 0
        projectiles.draw(screen)
        room += 1

        # Обновление экрана
        pygame.display.flip()
        clock.tick(FPS)

terminate()

