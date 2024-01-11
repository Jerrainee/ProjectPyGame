import os
import sys
# import time

import pygame
import pytmx

from random import randint, choice

file_name1 = 'data/levels/level1.tmx'
file_name2 = 'data/levels/level3.tmx'

FPS = 60
STEP = 6
GRAVITY = 0.5
moving_left = False
moving_right = False
moving_down = False
jump = False
dash = False
dash_unlock = False
double_jump_unlock = True
double_jump_check = False
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


player_image = load_image('data/images/entities/player/hero.png', -1)
dash_image = load_image('data/images/items/key/0.png', -1)


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


class Boss:
    def __init__(self, hero):  # инициализация объекта класса Босс. передача аргумента гг
        self.base_health = Health(20)
        self.soul = Soul(0.5)
        self.charge = 0.0
        self.dead_cond = False
        self.hero = hero

    def deal_damage(self):  # Босс получил урон. Первая функция убирает одно хп, вторая - проверяет, мертв ли босс
        self.base_health.received_hit()

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

        self.charge_long_distance_shot()

    def give_long_damage(self):  # Босс наносит удар с дальнего расстояния (дальний бой)
        if self.charge == 100:
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
            self.charge = 0.0
        else:
            print('Not charged yet.')

        #  лонгшот должен отличаться от обычного удара и надо его эпик его нарисовать

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

        if should_drop_anything:
            self.drop_items()

        self.give_hero_score()

        print("Death of Boss validated. Deleting boss.")

        del self

    def drop_items(self):  # Функция которая отвечает за дроп предмета из босса
        item = None  # выберите рандомный айтем и присвойте его этой переменной

        # киньте этот айтем на поле и дайте игроку возможность его подобрать и пусть игрок подбирает

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


class MiniBoss:
    def __init__(self, hero):  # инициализация объекта класса Минибосс. передача аргумента гг
        self.base_health = Health(10)
        self.soul = Soul(0.33)
        self.charge = 0.0
        self.dead_cond = False
        self.hero = hero

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


class Enemy:
    def __init__(self, hero):  # инициализация объекта класса Враг (обычный). передача аргумента гг
        self.base_health = Health(3)
        self.soul = Soul(0.1)
        self.dead_cond = False
        self.hero = hero

    def deal_damage(self):  # Враг получил урон. Первая функция убирает одно хп, вторая - проверяет, мертв ли он
        self.base_health.received_hit()

        self.check_death_state()

    def give_damage(self):  # Враг наносит удар с близкого расстояния (ближний бой) - 1 вариант атаки для данного типа
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

    def is_dead(self):  # Геттер состояния смерти врага
        return self.dead_cond

    def death_condition_met(self):  # Функция, которая вызывается при положительной проверке на смерть (выбор,
        # нужно ли что-либо дропать, также добавления очков и экспы игроку)
        print('Enemy (type=Enemy) is dead.')

        should_drop_anything = None

        if randint(1, 10) == 1:
            should_drop_anything = True

        else:
            should_drop_anything = False

        if should_drop_anything:
            self.drop_items()

        self.give_hero_score()

        print("Death of enemy validated. Deleting entity.")

        del self

    def drop_items(self):  # Функция которая отвечает за дроп предмета из врага
        item = None  # выберите рандомный айтем и присвойте его этой переменной

        # киньте этот айтем на поле и дайте игроку возможность его подобрать и пусть игрок его подбирает

    def give_hero_score(self):  # Функция которая дает гг опыт и очки за победу над врагом
        basic_value = randint(10, 25)

        self.hero.exp.add_score(basic_value)

    def check_death_state(self):  # Функция, которая проверяет, жив ли враг
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


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, scale):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.scale = scale
        self.fall_y = 0
        self.in_air = False
        self.sight = 0
        self.dash_cooldown = True
        self.dash_speed = 0
        self.n_dash = 1
        self.jump_count = 0
        self.cur_animation = 0
        self.cur_frame = 0
        self.animation_list = []
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

        animation_types = ['idle', 'run', 'jump', 'in_air', 'climb', 'dash']
        for animation in animation_types:
            cur_animations_lst = []
            n = len(os.listdir(f'data/images/entities/player/{animation}'))
            for i in range(n):
                img = pygame.image.load(f'data/images/entities/player/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img,
                                             (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
                cur_animations_lst.append(img)
            self.animation_list.append(cur_animations_lst)

    #   print(self.animation_list)

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

        if pygame.sprite.spritecollideany(self, wall_group) or pygame.sprite.spritecollideany(self, vertical_borders):
            self.rect.x -= dx

        # коллайд гг с мобом по x
        if pygame.sprite.spritecollideany(self, enemy_group):
            if self.dash_speed:
                pass
                # коллайд по х с дэшем, моб должен получить урон
            else:
                pass
                # коллайд по х без дэша, гг получает урон

        # смотрим коллайды по y
        self.rect.y += dy

        if pygame.sprite.spritecollideany(self, horizontal_borders):
            pass  # гг выпал за рамки уровня, смерть

        if pygame.sprite.spritecollideany(self, enemy_group):
            self.fall_y = -11 # отскок от моба (как прыжок)
            # гг прыгнул на голову моба, моб должен получить урон

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
            if not pygame.sprite.spritecollideany(self, ladder_group):
                self.in_air = True

        if pygame.sprite.spritecollideany(self, trap_group) and self.dash_speed == 0:
            self.fall_y = -11 # отскок от шипа (как прыжок)
            # Получение урона от шипа !
            # функционал работает мега криво и кринжово, надо что-то придумать

        if pygame.sprite.spritecollideany(self, exit_group):
            for i in all_sprites:
                i.kill()
            global player, item, level_count
            level_count += 1
            player, item = generate_level(file_name2, level_count)

        # print(self.in_air)
        # print(self.fall_y)

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

    def used_key(self):
        key = False  # проверка на ключ
        if key:
            self.items['key'].pop()
            # открытие сундука, поздравление игрока
            return True

        else:
            print("Can't use key here. There are no chests nearby.")
            return None

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
            n = len(os.listdir(f'data/images/interface/healthbar/{animation}'))
            for i in range(n):
                img = pygame.image.load(f'data/images/interface/healthbar/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img,
                                             (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
                cur_animations_lst.append(img)
            self.animation_list.append(cur_animations_lst)

    def update(self, target):
        self.cur_hp = player.base_health.base_health
        for i in range(len(self.cur_hp)):
            if self.cur_hp[i] == 0:
                self.cur_animation = 0
            if self.cur_hp[i] == 1:
                self.cur_animation = 1
            try:
                if self.animation_cooldown >= 1:
                    self.image = self.animation_list[self.cur_animation][self.cur_frame]
                    self.cur_frame += 1
                    if self.cur_frame >= len(self.animation_list):
                        self.cur_frame = 0
                    self.animation_cooldown = 0
                else:
                    self.animation_cooldown += 0.12

            except Exception:
                self.cur_frame = 0

            self.rect = self.image.get_rect()
            screen.blit(self.image, (5 + 64 * i, 5))
            # self.width = self.image.get_width()
            # self.height = self.image.get_height()                 # Не работает ! Я отключил вызов в цикле running
            # self.rect.x = 5 + 64 * i
            # self.rect.y = 2100
            # self.rect = self.image.get_rect().move(
            #   self.pos_x, self.pos_y)





def used_medical_item(self, item):
    item_name = item.name

    if item_name == 'heal':
        self.base_health.restore_health(self)

    elif item_name == 'hp':
        self.base_health.add_health()

    item_id = item.id

    index = 0
    for i in range(len(self.items['medical'])):
        if item_id == self.items['medical'][i].id:
            index = i

    self.items['medical'].pop(index)


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


class Item(pygame.sprite.Sprite):
    def __init__(self, item_type, pos_x, pos_y, scale):
        super().__init__(item_group, all_sprites)
        self.item_type = item_type
        self.scale = scale
        self.item_lst = ['treasure', 'key', 'dash', 'double_jump']
        self.animation_list_items = []
        self.cur_frame = 0
        self.animation_cooldown = 0

        for animation in self.item_lst:
            cur_animations_lst = []
            n = len(os.listdir(f'data/images/items/{animation}'))
            for i in range(n):
                img = load_image((f'data/images/items/{animation}/{i}.png'), -1)
                img = pygame.transform.scale(img,
                                             (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
                cur_animations_lst.append(img)
            self.animation_list_items.append(cur_animations_lst)
        print(self.animation_list_items)

        self.image = self.animation_list_items[self.item_type][self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.image.get_rect().move(
            pos_x, pos_y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        pygame.transform.scale(self.image, (self.width // 2, self.height // 2))

    #  screen.blit(pygame.transform.flip(self.image, False, False), self.rect)

    def update(self):
        # функционал
        global dash_unlock, double_jump_unlock
        if pygame.sprite.spritecollideany(self, player_group):
            if self.item_lst[self.item_type] == 'dash':
                dash_unlock = True
                self.kill()
            if self.item_lst[self.item_type] == 'double_jump':
                double_jump_unlock = True
                self.kill()
            if self.item_lst[self.item_type] == 'key':
                # добавление ключа в инвентарь
                self.kill()
            if self.item_lst[self.item_type] == 'treasure':
                # коллайд с сундуком, вызов функции открытия
                if Player.used_key:
                    self.kill()

        # анимации айтемов на уровне
        try:
            if self.animation_cooldown >= 1:
                self.image = self.animation_list_items[self.item_type][self.cur_frame]
                self.cur_frame += 1
                if self.cur_frame >= len(self.animation_list_items[self.item_type]):
                    self.cur_frame = 0
                self.animation_cooldown = 0
            else:
                self.animation_cooldown += 0.12
        except Exception:
            self.cur_frame = 0


class Health:
    def __init__(self, amount):
        self.base_health = []

        for i in range(amount):
            self.base_health.append(1)

    def received_hit(self):
        for i in range(len(self.base_health) - 1, 0, -1):

            if self.base_health[i] == 1:

                self.base_health[i] = 0

                if set(self.base_health) == {0}:
                    print("Hero is dead.")

                break
        else:
            print("Hero is dead.")

    def restore_health(self, hero):
        if hero.soul.soul_state or 'heal' in hero.items:  # надо добавить айтемы в игру!!!!

            for i in range(len(self.base_health) - 1):

                if self.base_health[i] == 0:
                    self.base_health[i] = 1
                    hero.soul_state = False
                    break
            else:
                print("Base health already satisfied.")
        else:
            print("Soul state criteria is not met.")

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
        self.soul_cond = 0.0

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


def generate_level(filename, LEVEL_COUNT):
    global map
    try:
        if LEVEL_COUNT == 0:
            SCALE, n, scale_player, scale_item, item_type = 6, 1, 1.7, 1, 2
        elif LEVEL_COUNT == 1:
            SCALE, n, scale_player, scale_item, item_type = 3, 2, 1.5, 1, 3
        map = pytmx.load_pygame(filename)
        tile_size = map.tilewidth
        Border(0, map.height * tile_size * SCALE, map.width * tile_size * SCALE, map.height * tile_size * SCALE)
        Border(0, 0, 0, map.height * tile_size * SCALE)
        Border(map.width * tile_size * SCALE, 0, map.width * tile_size * SCALE, map.height * tile_size * SCALE)
        new_player = None
        new_items = []
        for layer in range(13):
            for y in range(map.height):
                for x in range(map.width):
                    image = map.get_tile_image(x, y, layer)
                    if image:
                        temp = Tile(pygame.transform.scale(image, (tile_size * SCALE, tile_size * SCALE)),
                                    x * tile_size * SCALE,
                                    y * tile_size * SCALE, int(8 * n * SCALE), int(8 * n * SCALE), layer)
                        if layer == 12:
                            new_player = Player((x * 8 * n * SCALE), (y * 8 * n * SCALE), scale_player)
                        if layer == 10:
                            temp.add(treasure_group)
                            new_items.append(Item(0, (x * 8 * SCALE - 5), (y * 8 * SCALE - 5), 2.2))
                        if layer == 9:
                            new_items.append(Item(1, (x * 8 * SCALE), (y * 8 * SCALE) - 50, 1))
                        if layer == 8:
                            new_items.append(Item(item_type, (x * 8 * SCALE), (y * 8 * SCALE) - 50, scale_item))
                        #   temp.add(item_group)
                        if layer == 7:
                            temp.add(exit_group)
                        if layer == 6:
                            # мини босс
                            # тут должнен быть вызван его класс, чтобы он появился
                            temp.add(enemy_group)
                        if layer == 5:
                            # обычные враги
                            # тут должнен быть вызван их класс, чтобы они появились
                            temp.add(enemy_group)
                        if layer == 4:
                            temp.add(trap_group)
                        if layer == 3:
                            temp.add(wall_group)
                        if layer == 2:
                            temp.add(ladder_group)
                        if layer == 1:
                            temp.add(wall_group)
                        if layer == 0:
                            temp.add(background_group)
                        temp.add(all_sprites)
        print(1)
        return new_player, new_items
    except Exception as f:
        print(f)


player, items = generate_level(file_name1, level_count)

if __name__ == '__main__':
    running = True
    camera = Camera()
    hpBar = HealthBar(player)
    pause = False
    while running:
        screen.fill(pygame.Color("black"))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause = True

                while pause:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            pause = False
                        if event.type == pygame.QUIT:
                            running = False
                            pause = False
                        if event.type == pygame.KEYUP:
                            if event.key == pygame.K_a:
                                moving_left = False
                            if event.key == pygame.K_d:
                                moving_right = False
                            if event.key == pygame.K_SPACE or event.key == pygame.K_w:
                                jump = False
                            if event.key == pygame.K_s:
                                moving_down = False
                            if event.key == pygame.K_q and dash_unlock:
                                dash = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    moving_left = True
                if event.key == pygame.K_d:
                    moving_right = True
                if event.key == pygame.K_SPACE or event.key == pygame.K_w:
                    jump = True
                if event.key == pygame.K_s:
                    moving_down = True
                if event.key == pygame.K_q and dash_unlock:
                    dash = True
                if event.key == pygame.K_e:
                    action = True

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
                if event.key == pygame.K_q and dash_unlock:
                    dash = False
                if event.key == pygame.K_e:
                    action = False

            if event.type == pygame.K_e:
                # отображение инвенторя
                print('inventory')
                pass

        player.move(moving_left, moving_right, jump, moving_down, dash)
        camera.update(player)
        for i in items:
            i.update()
        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply(sprite))
        hpBar.update(player)

        # Обновление экрана
        pygame.display.flip()
        pygame.display.update()
        clock.tick(FPS)
terminate()
