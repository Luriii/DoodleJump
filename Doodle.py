import pygame, sys
import random


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
                            platform.kill()
                            type = random.randint(0, 2)
                            x = random.randint(0, 320)
                            y = -800 / max_platforms
                            image_name = images[type]
                            platform_type = platform_types[type]
                            platforms_group.add(Platform(x, y, image_name, platform_type))

                else:
                    if self.rect.bottom <= platform.rect.centery:
                        if self.gravity > 0:
                            self.jump_sound.play()
                            self.rect.bottom = platform.rect.top
                            dy = 0
                            self.gravity = -20
        s = 0 # s stands for scroll
        if self.rect.y <= 500:
                            self.gravity -= 30
        s = 0  # s stands for scroll
        if self.rect.y <= 300:
            if self.gravity < 0:
                s = -dy
        # collision with booster
        # global booster
        # for booster in boosters:
        #     if booster.rect.colliderect(self.rect.x, self.rect.y + dy, 60, 60):
        #         with_rocket = pygame.image.load('with_rocket.png').convert_alpha()
        #         rocketman = pygame.transform.scale(with_rocket, (60, 60))
        #         self.image = rocketman
        #         self.gravity -= 40
        #         self.rocket_sound.play()
        return s

    def fire(self):
        key = pygame.key.get_pressed()
        global bullets
        # movement
        if key[pygame.K_UP]:
            self.image = self.player_pos[2]
            bullets.add(Bullet(self.rect.x, self.rect.y + 5, 'bullet.png'))

    def draw(self, screen):
        screen.blit(pygame.transform.scale(self.image, (60, 60)), (self.rect.x - 12, self.rect.y - 5))
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

    def update(self):
        self.collisions()
        self.move()
        self.apply_gravity()
        self.fire()
        self.draw(screen)


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
    # 3 platform types: state(green), moving (blue), destructive (brown)
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


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()

        if type == 'OneEyed':
            monster_1 = pygame.image.load('Pictures/OneEyed.png').convert_alpha()
            self.frames = [monster_1]
            y_pos = 210
        elif type == 'Large Blue':
            monster_2 = pygame.image.load('Pictures/Large Blue Monster.png').convert_alpha()
            self.frames = [monster_2]
            y_pos = 210
        else:
            monster_3 = pygame.image.load('Pictures/Butterfly.png').convert_alpha()
            self.frames = [monster_3]
            y_pos = 300

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom=(random.randint(900, 1100), y_pos))

    def animation_state(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animation_state()
        self.rect.x -= 6
        self.destroy()

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()


# create background
def draw_background():
    screen.blit(background, (0, 0))
    screen.blit(background, (0, 800))


def display_score():
    current_time = int(pygame.time.get_ticks() / 1000) - start_time
    score_surf = test_font.render('Score: {}'.format(current_time), False, (0, 0, 0))
    score_rect = score_surf.get_rect(center=(350, 20))
    screen.blit(score_surf, score_rect)
    return current_time


# Initial preset of a game
pygame.init()
screen = pygame.display.set_mode((400, 800))
pygame.display.set_caption('Doodle_Jump')
clock = pygame.time.Clock()
test_font = pygame.font.Font(None, 30)
game_active = False
start_time = 0
score = 0
max_platforms = 10
# bg_music = pygame.mixer.Sound('audio/music.wav')
# bg_music.play(loops=-1)

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

rocket_index = random.randint(0, 9)


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
            type = random.randint(0, 2)
            x = random.randint(0, 320)
            y = -800 / max_platforms
            platform.rect.x = x
            platform.rect.y = y
            image_name = images[type]
            platform_type = platform_types[type]
            image = pygame.image.load(image_name).convert_alpha()
            platform.image = pygame.transform.scale(image, (80, 20))
            platform.type = platform_type


for i in range(1, max_platforms):
    type = random.randint(0, 2)
    x = random.randint(0, 320)
    y = 800 / max_platforms * i
    './Pictures/Platforms/platform.png'
    platforms_group.add(Platform(x, y, images[type], platform_types[type]))
    if i == rocket_index:
        rocket_x = x
        rocket_y = y
# Booster
boosters = pygame.sprite.Group()
boosters.add(Boosters(rocket_x, rocket_y - 30))
# Background
background_pos = 0
background = pygame.image.load('background.png').convert()

# Intro screen
doodle = pygame.image.load('doodle_right.png').convert_alpha()
doodle_rect = doodle.get_rect(midbottom=(200, 800))

game_name = test_font.render('Doodle Jump', False, (0, 0, 0))
game_name_rect = game_name.get_rect(center=(200, 450))

game_message = test_font.render('Press space to jump', False, (0, 0, 0))
message_space = game_message.get_rect(center=(200, 500))
game_message_left = test_font.render('Press left arrow to move left', False, (0, 0, 0))
message_left = game_message.get_rect(center=(150, 550))
game_message_right = test_font.render('Press left arrow to move left', False, (0, 0, 0))
message_right = game_message.get_rect(center=(150, 600))

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                start_time = int(pygame.time.get_ticks() / 1000)
                game_active = True

    if game_active:
        draw_background()
        if background_pos >= 800:
            background_pos = 0
        # background_pos += 10
        # screen.blit(background, (0, 0))
        score = display_score()
        player.draw(screen)
        scroll = player.collisions()
        player.update()
        floor_collision()
        platforms_group.draw(screen)
        platforms_group.update(scroll)
        update_platforms()
        bullets.draw(screen)
        bullets.update()

    else:
        screen.blit(background, (0, 0))
        screen.blit(doodle, doodle_rect)
        if score == 0:
            screen.blit(game_name, game_name_rect)
            screen.blit(game_message, message_space)
            screen.blit(game_message_left, message_left)
            screen.blit(game_message_right, message_right)
        else:
            score_message = test_font.render('Your score: {}'.format(score), False, (0, 0, 0))
            score_message_rect = score_message.get_rect(center=(200, 375))
            screen.blit(score_message, score_message_rect)

    pygame.display.update()
    clock.tick(60)
