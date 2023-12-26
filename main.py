import sys

import pygame
import pytmx

file_name = 'data/levels/level1.tmx'

LEVEL_COUNT = 0
FPS = 60
STEP = 5
GRAVITY = 0.5
moving_left = False
moving_right = False
moving_down = False
jump = False
dash = False
dash_unlock = False
dash_cooldown = False
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
item_group = pygame.sprite.Group()


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
dash_image = load_image('data/images/items/dash.png', -1)


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
        self.fall_y = 0
        self.in_air = False
        self.sight = 0
        self.rect = self.image.get_rect().move(
            pos_x, pos_y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def move(self, moving_left, moving_right, jump, moving_down, dash):
        dx = 0
        dy = 0

        if moving_left:
            dx = -STEP
            self.sight = 0
        if moving_right:
            dx = STEP
            self.sight = 1
        if jump and self.in_air == False:
            print('jump')
            self.fall_y = -10.5
            self.in_air = True
            jump = False
        if dash:
            if self.sight:
                dx = STEP * 6
            else:
                dx = -STEP * 6

        self.fall_y += GRAVITY
        if self.fall_y > 11:
            self.fall_y = 11
        dy += self.fall_y

        self.rect.x += dx
        if pygame.sprite.spritecollideany(self, wall_group):
            self.rect.x -= dx
        #    self.fall_y = 1
        self.rect.y += dy
        if pygame.sprite.spritecollideany(self, wall_group):
            if self.fall_y < 0:
                self.rect.y -= (dy - 0.1)
                self.fall_y = 0
            if self.fall_y > 0:
                self.rect.y -= (dy + 0.1)
                self.fall_y = 0
                self.in_air = False
        else:
            self.in_air = True
          #  print("in_air")
        if pygame.sprite.spritecollideany(self, ladder_group):
        #    self.rect.y -= dy * 0.2
            self.in_air = False
            if jump:
                dy -= 1
            if moving_down:
                dy += 5
class Items(pygame.sprite.Sprite):
    def __init__(self, n, item_type, pos_x, pos_y):
        super().__init__(item_group, all_sprites)
        self.image = item_type
        self.n = n
        self.item_lst = ['dash', 'walk_jump, double_jump']
        self.rect = self.image.get_rect().move(
            pos_x, pos_y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        pygame.transform.scale(self.image, (self.width // 2,  self.height // 2))
      #  screen.blit(pygame.transform.flip(self.image, False, False), self.rect)


    def update(self):
        if pygame.sprite.spritecollideany(self, player_group):
            if self.item_lst[self.n] == 'dash':
                global dash_unlock
                dash_unlock = True
                self.kill()



class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

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
        new_item = None
        for layer in range(7):
            for y in range(map.height):
                for x in range(map.width):
                    image = map.get_tile_image(x, y, layer)
                    if image:
                        temp = Tile(pygame.transform.scale(image, (tile_size * 5, tile_size * 5)), x * tile_size * 5,
                                    y * tile_size * 5, 8, 8)
                        if layer == 6:
                            new_player = Player((x * 8 * 5), (y * 8 * 5) - 75)
                        if layer == 5:
                            if LEVEL_COUNT == 0:
                                new_item = Items(0, dash_image, (x * 8 * 5), (y * 8 * 5) - 50)
                            temp.add(item_group)
                        if layer == 4:
                            pass
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
        return new_player, new_item
    except Exception as f:
        print(f)



player, item = generate_level(file_name)

if __name__ == '__main__':
    running = True
    camera = Camera()
    while running:
        screen.fill(pygame.Color("black"))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
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
        item.update()
        for sprite in all_sprites:
            camera.apply(sprite)
        tiles_group.draw(screen)
        player_group.draw(screen)
        item_group.draw(screen)

        pygame.display.update()
        clock.tick(FPS)
terminate()
