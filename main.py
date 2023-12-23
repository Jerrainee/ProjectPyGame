import sys

import pygame
import pytmx

file_name = 'data/levels/level1.tmx'

FPS = 60
STEP = 5
GRAVITY = 1
pygame.init()

size = WIDTH, HEIGHT = 1280, 720

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


player_image = load_image('data/images/entities/player/mar.png', -1)


class Tile(pygame.sprite.Sprite):
    def __init__(self, image, pos_x, pos_y, tile_width, tile_height):
        super().__init__(tiles_group, all_sprites)
        self.image = image
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        # print(pos_x, pos_y)


def terminate():
    pygame.quit()
    sys.exit()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.direction = False
        self.fall_y = 3
        self.in_air = False
        self.rect = self.image.get_rect().move(
            pos_x, pos_y)

    def update(self, *args, **kwargs):
        key = args[0]
        move = (0, 0)
        if key[pygame.K_w] or key[pygame.K_SPACE]:
            move = (0, -STEP * 3)
        if key[pygame.K_s]:
            move = (0, STEP)
        if key[pygame.K_a]:
            move = (-STEP, 0)
            self.direction = True
        if key[pygame.K_d]:
            move = (STEP, 0)
            self.direction = False

        self.rect = self.rect.move(*move)
      #  self.gravity()

        if pygame.sprite.spritecollideany(self, wall_group):
            move = (-move[0], -move[1])
            self.rect = self.rect.move(*move)
        if pygame.sprite.spritecollideany(self, ladder_group):
            if key[pygame.K_w]:
                move = (0, -STEP)
                print('лестница вверх')
                self.rect = self.rect.move(*move)

    def gravity(self):
     #   self.fall_y += GRAVITY
        if pygame.sprite.spritecollideany(self, wall_group) and self.fall_y != 0:
            move = (0, -3)
            self.rect = self.rect.move(*move)
            self.fall_y = 0
        else:
            self.fall_y = 3
        move = (0, self.fall_y)

        self.rect = self.rect.move(*move)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 100

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


def generate_level(filename):
    try:
        map = pytmx.load_pygame(filename)
        tile_size = map.tilewidth
        new_player = None
        for layer in range(4):
            for y in range(map.height):
                for x in range(map.width):
                    image = map.get_tile_image(x, y, layer)
                    if image:
                        temp = Tile(pygame.transform.scale(image, (tile_size * 5, tile_size * 5)), x * tile_size * 5,
                                    y * tile_size * 5, 8, 8)
                        if layer == 1:
                            temp.add(ladder_group)
                        if layer == 3:
                            new_player = Player((x * 8 * 5) - 1, (y * 8 * 5) - 1)
                        if layer == 2:
                            temp.add(wall_group)
                        if layer == 0:
                            temp.add(background_group)
                        temp.add(all_sprites)
        print(1)
        return new_player
    except Exception as f:
        print(f)


player = generate_level(file_name)

if __name__ == '__main__':
    running = True
    camera = Camera()
    pygame.key.set_repeat(1, 15)
    while running:
        screen.fill(pygame.Color("black"))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                player.update(pygame.key.get_pressed())
    #    player.gravity()
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        tiles_group.draw(screen)
        player_group.draw(screen)

        pygame.display.update()
        clock.tick(FPS)
terminate()
