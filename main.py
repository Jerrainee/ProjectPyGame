import os
import sys

import pygame
import pytmx

file_name1 = 'data/levels/level1.tmx'
file_name3 = 'data/levels/level3.tmx'

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
pygame.init()

size = WIDTH, HEIGHT = 1280, 720
map = None

screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

pygame.display.set_caption('Название игры')

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
mob_group = pygame.sprite.Group()
background_group = pygame.sprite.Group()
ladder_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
trap_group = pygame.sprite.Group()
border_group = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()


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
        self.cur_animation = 0
        self.cur_frame = 0
        self.animation_list = []
        self.animation_cooldown = 0
        self.check = True
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.image = pygame.transform.scale(self.image, (self.width * self.scale, self.height * self.scale))
        self.rect = self.image.get_rect().move(
            pos_x, pos_y)

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
        dx = 0
        dy = 0

        if moving_left:
            dx = -STEP
            self.sight = 1
            if not self.dash_speed:
                self.cur_animation = 1
                self.check = True
        if moving_right:
            dx = STEP
            self.sight = 0
            if not self.dash_speed:
                self.cur_animation = 1
                self.check = True
        if jump and not self.in_air:
            self.cur_animation = 2
            self.fall_y = -11
            self.in_air = True
            self.check = True

        if not moving_left and not moving_right and not jump and not self.dash_speed and self.check:
            self.cur_animation = 0
            self.check = False

        # dash
        if dash and self.dash_cooldown and self.n_dash >= 1:
            self.cur_animation = 5
            if self.sight:
                self.dash_speed = -7
            else:
                self.dash_speed = 7
            self.dash_cooldown = False
            self.n_dash = 0
        if self.n_dash < 1:
            self.n_dash += 0.025
        if not self.in_air and self.dash_speed == 0:
            self.dash_cooldown = True

        elif self.in_air and self.check:

            self.cur_animation = 3
            self.check = False

        self.fall_y += GRAVITY
        if self.fall_y > 11:
            self.fall_y = 11

        if self.dash_speed:
            self.fall_y = 0.1
            self.rect.x += STEP * self.dash_speed
            if pygame.sprite.spritecollideany(self, wall_group):
                self.rect.x -= STEP * self.dash_speed
            if self.sight:
                self.dash_speed += 1
            else:
                self.dash_speed -= 1

        dy += self.fall_y

        self.rect.x += dx

        if pygame.sprite.spritecollideany(self, wall_group):
            self.rect.x -= dx
        #    self.fall_y = 1

        self.rect.y += dy

        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.rect.x -= dx

        if pygame.sprite.spritecollideany(self, horizontal_borders):
            pass  # смэрть

        if pygame.sprite.spritecollideany(self, ladder_group):
            self.in_air = False
            self.check = True
            if not moving_down:
                self.rect.y -= dy
                if jump:
                    self.rect.y -= STEP * 0.8
                    self.cur_animation = 4
                else:
                    self.cur_animation = 0
            else:
                self.cur_animation = 4

        if pygame.sprite.spritecollideany(self, wall_group):
            self.check = True
            if self.fall_y < 0:
                self.rect.y -= (dy + 0.1)
                self.fall_y = 0
            if self.fall_y > 0:
                self.rect.y -= (dy + 0.1)
                self.fall_y = 0
                self.in_air = False
        else:
            self.in_air = True
        if pygame.sprite.spritecollideany(self, trap_group):
            screen.fill(pygame.Color("red"))
            self.rect.x -= dx * 2
            self.rect.y -= dy * 2

        if pygame.sprite.spritecollideany(self, exit_group):
            for i in all_sprites:
                i.kill()
            LEVEL_COUNT = 2
            global player, item
            player, item = generate_level(file_name3, LEVEL_COUNT)

        self.update()

    def update(self):
        # global temp
        try:
            if self.animation_cooldown >= 1:
                self.image = self.animation_list[self.cur_animation][self.cur_frame]
                if self.sight:
                    self.image = pygame.transform.flip(self.image, 1, 0)
                self.cur_frame += 1
                if self.cur_frame >= len(self.animation_list[self.cur_animation]):
                    self.cur_frame = 0
                #    temp.add(all_sprites)
                self.animation_cooldown = 0
            else:
                self.animation_cooldown += 0.12
        except Exception:
            self.cur_frame = 0

        if self.cur_animation == 5 and self.dash_speed == 0:
            self.cur_animation = 0
        if self.dash_speed:
            self.animation_cooldown = 1
            self.cur_animation = 5


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
        global dash_unlock, double_jump_unlock
        if pygame.sprite.spritecollideany(self, player_group):
            if self.item_lst[self.item_type] == 'dash':
                dash_unlock = True
                self.kill()
            if self.item_lst[self.item_type] == 'double_jump':
                double_jump_unlock = True
                self.kill()
            if self.item_lst[self.item_type] == 'key':
                self.kill()

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
        print(y)
        if level_count == 0:
            SCALE = 6
        elif level_count == 2:
            SCALE = 3
        x = max(-(map.width * map.tilewidth * SCALE - WIDTH), x)  # Правая сторона
        y = max(-(map.height * map.tilewidth * SCALE - HEIGHT), y)  # Нижняя сторона
        print(y, -(map.height * map.tilewidth * SCALE - HEIGHT))

        self.camera = pygame.Rect(x, y, WIDTH, HEIGHT)


def generate_level(filename, LEVEL_COUNT):
    global map
    try:
        if LEVEL_COUNT == 0:
            SCALE, n, scale_player, scale_item = 6, 1, 1.7, 1
        elif LEVEL_COUNT == 2:
            SCALE, n, scale_player, scale_item = 3, 2, 1.5, 1
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
                        if layer == 8:
                            new_items.append(Item(1, (x * 8 * SCALE), (y * 8 * SCALE) - 50, scale_item))
                        if layer == 7:
                            if LEVEL_COUNT == 0:
                                new_items.append(Item(2, (x * 8 * SCALE), (y * 8 * SCALE) - 50, scale_item))
                        #      temp.add(item_group)
                        if layer == 6:
                            temp.add(exit_group)
                        if layer == 5:
                            temp.add(mob_group)
                        # if layer == 4:
                        #     temp.add(trap_group)
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


level_count = 0
player, items = generate_level(file_name1, level_count)

if __name__ == '__main__':
    running = True
    camera = Camera()
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
        player.move(moving_left, moving_right, jump, moving_down, dash)
        camera.update(player)
        for i in items:
            i.update()
        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply(sprite))

        pygame.display.update()
        clock.tick(FPS)
terminate()
