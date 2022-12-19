import pygame
import sys
import random
import numpy as np
import time
import pickle


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, image_name):
        super().__init__()
        image = pygame.image.load(image_name).convert_alpha()
        self.image = pygame.transform.scale(image, (15, 15))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.y -= 5
        if self.rect.y == 0:
            self.kill()


class Player:
    def __init__(self):
        super().__init__()
        player_left = pygame.image.load('doodle_left.png').convert_alpha()
        left = pygame.transform.scale(player_left, (60, 60))
        player_right = pygame.image.load('doodle_right.png').convert_alpha()
        right = pygame.transform.scale(player_right, (60, 60))
        player_up = pygame.image.load('doodle_up.png').convert_alpha()
        up = pygame.transform.scale(player_up, (40, 40))
        self.player_pos = [left, right, up]
        self.image = self.player_pos[1]
        self.rect = pygame.Rect(0, 0, 50, 50)
        self.rect.center = (150, 800)
        self.gravity = 0
        self.jump_sound = pygame.mixer.Sound('jump.wav')
        self.jump_sound.set_volume(0.5)
        self.rocket_sound = pygame.mixer.Sound('rocket.mp3')
        self.rocket_sound.set_volume(0.5)
        self.score = 0
        self.fire_timer = time.time()

    def move(self):
        key = pygame.key.get_pressed()
        # movement
        if key[pygame.K_LEFT] and self.rect.x >= 0:
            self.rect.x -= 10
            self.image = self.player_pos[0]
        if key[pygame.K_RIGHT] and self.rect.x <= 400:
            self.rect.x += 10
            self.image = self.player_pos[1]
        # finite space
        if self.rect.x < 0:
            self.rect.x = 400
        if self.rect.x > 400:
            self.rect.x = 0
        # jumping
        if key[pygame.K_SPACE] and self.rect.bottom >= 800:
            self.gravity = -20
            self.jump_sound.play()

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 800:
            self.rect.bottom = 800

    def collisions(self):
        # collision with platforms
        global platforms_group
        dy = self.gravity
        for platform in platforms_group:
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, 60, 60):
                if platform.type == 'Brown':
                    image = pygame.image.load('./Pictures/Platforms/Broken.png').convert_alpha()
                    if self.rect.bottom < platform.rect.centery:
                        if self.gravity > 0:
                            platform.image = pygame.transform.scale(image, (80, 20))

                            type = random.randint(0, 2)
                            x = random.randint(0, 320)
                            y = -800 / max_platforms
                            image_name = images[type]
                            platform_type = platform_types[type]
                            platforms_group.add(Platform(x, y, image_name, platform_type))
                            platform.kill()
                else:
                    if self.rect.bottom <= platform.rect.centery:
                        if self.gravity > 0:
                            self.jump_sound.play()
                            # self.rect.bottom = platform.rect.top
                            dy = 0
                            self.gravity = -20
        # s stands for scroll
        s = 0
        if self.rect.y <= 500:
            if self.gravity < 0:
                s = -dy
        # collision with booster
        rocket_start = time.time()
        global booster
        for booster in boosters:
            if booster.rect.colliderect(self.rect.x, self.rect.y + dy, 60, 60):
                with_rocket = pygame.image.load('with_rocket.png').convert_alpha()
                self.image = pygame.transform.scale(with_rocket, (60, 60))
                self.gravity -= 40
                rocket_start = time.time()
                self.rocket_sound.play()
                booster.kill()
                # check if there is enough fuel to fly
        if time.time() - rocket_start > 5:
            self.image = self.player_pos[0]
        # return scroll variable to update screen
        return s

    def fire(self):
        key = pygame.key.get_pressed()
        global bullets
        # movement
        if key[pygame.K_UP]:
            self.image = self.player_pos[2]
            if time.time() - self.fire_timer > 0.5:
                self.fire_timer = time.time()
                bullets.add(Bullet(self.rect.x, self.rect.y + 5, 'bullet.png'))

    def draw(self, screen):
        screen.blit(pygame.transform.scale(self.image, (60, 60)), (self.rect.x - 12, self.rect.y - 5))
        pygame.draw.rect(screen, (255, 255, 255), self.rect, -1)

    def update(self, scroll):
        self.collisions()
        self.move()
        self.apply_gravity()
        self.fire()
        self.draw(screen)
        self.rect.y += scroll
        if self.score < self.score - self.gravity and self.gravity < 0:
            self.score -= self.gravity


class Boosters(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        rocket_image = pygame.image.load('jetpack.png').convert_alpha()
        rocket = pygame.transform.scale(rocket_image, (40, 40))
        self.image = rocket
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Platform(pygame.sprite.Sprite):
    # 3 platform types: static (green), moving (blue), broken (brown)
    def __init__(self, x, y, image_name, type):
        super().__init__()
        image = pygame.image.load(image_name).convert_alpha()
        self.image = pygame.transform.scale(image, (80, 20))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = type
        self.change_x = 1

    def update(self, scroll):
        self.rect.y += scroll
        if self.type == 'Blue':
            if self.rect.x >= 320 or self.rect.x <= 0:
                self.change_x *= -1
            self.rect.x += self.change_x
        else:
            pass


class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        if type == 'OneEyed':
            monster_1 = pygame.image.load('Pictures/OneEyed.png').convert_alpha()
            self.image = pygame.transform.scale(monster_1, (80, 80))
        elif type == 'LargeBlue':
            monster_2 = pygame.image.load('Pictures/Large Blue Monster.png').convert_alpha()
            self.image = pygame.transform.scale(monster_2, (80, 80))
        elif type == 'ButterFly':
            monster_3 = pygame.image.load('Pictures/Butterfly.png').convert_alpha()
            self.image = pygame.transform.scale(monster_3, (80, 80))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # for movement
        self.pos_change = 0
        self.dx = 1

    # check for a collision with bullets
    def dodging_from_bullets(self):
        global bullets
        for bullet in bullets:
            if bullet.rect.colliderect(self.rect.x, self.rect.y, 80, 80):
                self.kill()

    def move(self):
        if self.pos_change < 40:
            self.rect.x += self.dx
            self.pos_change += 1
        else:
            self.dx = -self.dx
            self.pos_change = 0

    def update(self):
        self.move()
        self.dodging_from_bullets()


# create background
def draw_background():
    screen.blit(background, (0, 0))
    screen.blit(background, (0, 800))


def display_score():
    # global stop_time
    # player.score = int(pygame.time.get_ticks() / 1000) - start - stop_time
    player.score += player.collisions()
    score_surf = test_font.render('Score: {}'.format(player.score), False, (0, 0, 0))
    score_rect = score_surf.get_rect(center=(350, 20))
    screen.blit(score_surf, score_rect)
    return player.score


# Initial preset of a game

def floor_collision():
    global player
    global game_active
    if player.rect.y >= 750:
        game_active = False


# updating platform group when the background moved up
def update_platforms():
    global platforms_group, platform_types, images
    for platform in platforms_group:
        if platform.rect.y >= 800:
            platform.kill()
    if len(platforms_group) < max_platforms:
        type = np.random.randint(0, 3, max_platforms)
        x = np.random.randint(0, 320, max_platforms)
        y = np.arange(-800, 0, 800 / max_platforms)
        for i in range(1, len(type) - 1):
            if type[i] == 2 and type[i] == type[i + 1] and type[i] == type[i - 1]:
                type[i] = random.randint(0, 1)
        for i in range(len(type)):
            platforms_group.add(Platform(x[i], y[i], images[type[i]], platform_types[type[i]]))


def spawn_monsters():
    global monsters, monster_types, monster_timer
    if time.time() - monster_timer > 30:
        monster_timer = time.time()
        m_type = random.randint(0, 2)
        m_x = random.randint(0, 320)
        m_y = random.randint(0, 700)
        monsters.add(Monster(m_x, m_y, monster_types[m_type]))


def catch_pause():
    key = pygame.key.get_pressed()
    global pause, game_active
    if key[pygame.K_p]:
        pause = True
        game_active = False


def catch_continue():
    key = pygame.key.get_pressed()
    global pause, game_active, saved, loaded
    if key[pygame.K_c]:
        pause = False
        game_active = True
        saved = False
        loaded = False


def catch_save():
    key = pygame.key.get_pressed()
    global player, saved
    if key[pygame.K_s]:
        data = player.score
        with open("savegame", "wb") as f:
            pickle.dump(data, f)
        saved = True


def load():
    global game_active, loaded
    with open('savegame', "rb") as f:
        data = pickle.load(f)
    # game_active = True
    loaded = True
    return data


if __name__ == "__main__":

    pygame.init()
    screen = pygame.display.set_mode((400, 800))
    pygame.display.set_caption('Doodle_Jump')
    clock = pygame.time.Clock()
    test_font = pygame.font.Font(None, 30)
    game_active = False
    pause = False
    loaded = False
    saved = False
    start_time = 0
    scroll = 0
    score = 0

    max_platforms = 15
    bg_music = pygame.mixer.Sound('music.mp3')
    bg_music.play(loops=-1)
    bg_music.set_volume(0.5)

    # Screen
    HEIGHT = 800
    WIDTH = 320
    # Player
    player = Player()

    # Bullets
    bullets = pygame.sprite.Group()

    # Starting platform
    platforms_group = pygame.sprite.Group()
    platform = platforms_group.add(Platform(150, 730, './Pictures/Platforms/platform.png', 'Green'))
    platform_types = ['Green', 'Blue', 'Brown']
    images = ['./Pictures/Platforms/platform.png',
              './Pictures/Platforms/Blue.jpg',
              './Pictures/Platforms/Brown.jpg']

    # Monsters
    monster_timer = time.time()
    monsters = pygame.sprite.Group()
    monster_types = ['OneEyed', 'LargeBlue', 'ButterFly']

    for i in range(1, max_platforms):
        type = random.randint(0, 2)
        x = random.randint(0, 320)
        y = 600 / max_platforms * i
        platforms_group.add(Platform(x, y, images[type], platform_types[type]))

    # Booster
    boosters = pygame.sprite.Group()
    # Background
    background_pos = 0
    background = pygame.image.load('background.png').convert()

    # Intro screen
    doodle = pygame.image.load('doodle_right.png').convert_alpha()
    doodle_rect = doodle.get_rect(midbottom=(200, 800))

    game_name = test_font.render('Doodle Jump', False, (0, 0, 0))
    game_name_rect = game_name.get_rect(center=(200, 150))

    game_message = test_font.render('Press space to jump', False, (0, 0, 0))
    message_space = game_message.get_rect(center=(200, 450))
    game_message_left = test_font.render('Press left arrow to move left', False, (0, 0, 0))
    message_left = game_message.get_rect(center=(150, 500))
    game_message_right = test_font.render('Press left arrow to move left', False, (0, 0, 0))
    message_right = game_message.get_rect(center=(150, 550))
    # game_message_save = test_font.render('Press s to save', False, (0, 0, 0))
    # message_save = game_message.get_rect(center=(200, 300))
    game_message_load = test_font.render('Press l to load last saved game', False, (0, 0, 0))
    message_load = game_message.get_rect(center=(150, 350))
    game_message_pause = test_font.render('Press p to pause', False, (0, 0, 0))
    message_pause = game_message.get_rect(center=(200, 400))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_l and game_active == False and pause == False:
                    player.score = load()
                    score = player.score
                    # start_time = -score
                    loaded = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and game_active == False and pause == False:
                    if not loaded:
                        player.score = 0
                        score = 0
                        start_time = int(pygame.time.get_ticks() / 1000)
                    platforms_characteritics = []
                    platforms_group = pygame.sprite.Group()
                    rocket_index = random.randint(0, max_platforms)

                    type = np.random.randint(0, 3, 2 * max_platforms)
                    x = np.random.randint(0, 320, 2 * max_platforms)
                    y = np.arange(-800, 800, 1600 / (2 * max_platforms))
                    type[0] = random.randint(0, 1)
                    type[1] = random.randint(0, 1)
                    for i in range(1, len(type) - 1):
                        if type[i] == 2 and type[i] == type[i + 1] and type[i] == type[i - 1]:
                            type[i] = random.randint(0, 1)
                    for i in range(len(type)):
                        platforms_characteritics.append([x[i], y[i], platform_types[type[i]]])
                        './Pictures/Platforms/platform.png'
                        platforms_group.add(Platform(x[i], y[i], images[type[i]], platform_types[type[i]]))
                        if i == rocket_index and type[i] == 0:
                            rocket_x = x[i]
                            rocket_y = y[i]
                    # clock.tick(60)
                    game_active = True
                    saved = False
                    loaded = False

        if game_active and pause == False:
            draw_background()
            score = display_score()
            player.draw(screen)
            platforms_group.draw(screen)
            scroll = player.collisions()
            player.update(scroll)
            floor_collision()

            platforms_group.update(scroll)
            monsters.draw(screen)
            monsters.update()
            update_platforms()
            spawn_monsters()
            bullets.draw(screen)
            bullets.update()
            boosters.draw(screen)
            boosters.update()
            catch_pause()
        else:
            start_time = int(pygame.time.get_ticks())
            for bullet in bullets:
                bullet.kill()
            screen.blit(background, (0, 0))
            screen.blit(doodle, doodle_rect)
            if score == 0:
                screen.blit(game_name, game_name_rect)
                screen.blit(game_message, message_space)
                screen.blit(game_message_left, message_left)
                screen.blit(game_message_right, message_right)
                screen.blit(game_message_load, message_load)
                # screen.blit(game_message_save, message_save)
                screen.blit(game_message_pause, message_pause)
            else:
                if loaded:
                    score_message = test_font.render('Your score: {}'.format(score), False, (0, 0, 0))
                    score_message_rect = score_message.get_rect(center=(200, 375))
                    screen.blit(score_message, score_message_rect)
                    loaded_message = test_font.render('Loaded. Press space to continue', False, (0, 0, 0))
                    loaded_message_rect = loaded_message.get_rect(center=(200, 475))
                    screen.blit(loaded_message, loaded_message_rect)
                    # catch_continue()
                else:
                    score_message = test_font.render('Your score: {}'.format(score), False, (0, 0, 0))
                    score_message_rect = score_message.get_rect(center=(200, 375))
                    screen.blit(score_message, score_message_rect)
                    save_message = test_font.render('Press s to save score', False, (0, 0, 0))
                    save_message_rect = save_message.get_rect(center=(200, 475))
                    screen.blit(save_message, save_message_rect)
                    catch_save()
                    if saved:
                        saved_message = test_font.render('Saved. Press space to restart', False, (0, 0, 0))
                        saved_message_rect = saved_message.get_rect(center=(200, 150))
                        screen.blit(saved_message, saved_message_rect)
                    if pause:
                        pause_message = test_font.render('Press c to continue', False, (0, 0, 0))
                        pause_message_rect = pause_message.get_rect(center=(200, 275))
                        screen.blit(pause_message, pause_message_rect)
                        catch_continue()

        pygame.display.update()
        clock.tick(60)
