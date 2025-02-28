import pygame
import os
import random

# Настройки экрана
WIDTH, HEIGHT = 1920, 1080
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (50, 50, 50)
LIGHT_TEXT = (255, 255, 255)
DARK_TEXT = (200, 200, 200)
pygame.init()
pygame.mixer.init()
kills = 0
paused = False
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Игра")
clock = pygame.time.Clock()
game_running = False

db_file = "game_database.db"

BACKGROUND_IMAGE_PATH = "back.webp"

MUSIC_FILE_PATH = "back_music.mp3"

def draw_text(text, pos, color=WHITE, font_size=40):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)


class ImageButton:
    def __init__(self, x, y, image_path, text, action):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (200, 75))
        self.rect = self.image.get_rect(center=(x, y))
        self.action = action
        self.text = text

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        font = pygame.font.Font(None, 40)
        text_surface = font.render(self.text, True, LIGHT_TEXT)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.action()


def load_users():
    users = {}
    if os.path.exists(db_file):
        with open(db_file, "r") as file:
            for line in file:
                if ":" in line:
                    login, password = line.strip().split(":")
                    users[login] = password
    return users


def save_user(login, password):
    with open(db_file, "a") as file:
        file.write(f"{login}:{password}\n")


def draw_text(screen, text, pos, color=DARK_TEXT, font_size=30):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)


def draw_background(screen):
    background = pygame.image.load(BACKGROUND_IMAGE_PATH)
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))


def main_menu(screen):
    login_button = ImageButton(WIDTH // 2, HEIGHT // 2 - 50, "dark_fantasy_button.png", "Войти", login_screen)
    register_button = ImageButton(WIDTH // 2, HEIGHT // 2 + 50, "dark_fantasy_button.png", "Регистрация",
                                  register_screen)
    running = True
    while running:
        draw_background()
        login_button.draw(screen)
        register_button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            login_button.check_click(event)
            register_button.check_click(event)


def input_screen(title, prompts):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(title)
    font = pygame.font.Font(None, 50)
    inputs = ["" for _ in prompts]

    field_width, field_height = 500, 60
    spacing = 100
    start_y = HEIGHT // 2 - (len(prompts) * (field_height + spacing)) // 2

    rects = [(WIDTH // 2 - field_width // 2, start_y + i * (field_height + spacing), field_width, field_height)
             for i in range(len(prompts))]

    active_idx = 0

    running = True
    while running:
        draw_background()

        for i, prompt in enumerate(prompts):
            text_surface = font.render(prompt, True, LIGHT_TEXT)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, rects[i][1] - 40))
            screen.blit(text_surface, text_rect)

            pygame.draw.rect(screen, LIGHT_TEXT, rects[i], 2)
            input_surface = font.render(inputs[i], True, LIGHT_TEXT)
            screen.blit(input_surface, (rects[i][0] + 10, rects[i][1] + 15))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(rects):
                    if pygame.Rect(rect).collidepoint(event.pos):
                        active_idx = i
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if active_idx < len(inputs) - 1:
                        active_idx += 1
                    else:
                        return inputs
                elif event.key == pygame.K_BACKSPACE:
                    inputs[active_idx] = inputs[active_idx][:-1]
                else:
                    inputs[active_idx] += event.unicode


def show_message(screen, message, color, duration=800):
    screen.fill(BLACK)
    draw_background()
    font = pygame.font.Font(None, 60)
    text_surface = font.render(message, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()
    pygame.time.wait(duration)


def login_screen():
    users = load_users()
    login, password = input_screen("Вход", ["Введите логин:", "Введите пароль:"])
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    draw_background()
    if users.get(login) == password:
        show_message(screen, "Вход выполнен!", (0, 255, 0))
        pygame.display.flip()
        pygame.time.wait(800)
        create_main_menu(screen)
    else:
        show_message(screen, "Ошибка входа!", (255, 0, 0))
        pygame.display.flip()
        pygame.time.wait(800)
        main_menu(screen)


def create_main_menu(screen):
    global game_running
    button_text = "Начать"
    start_button = ImageButton(WIDTH // 2, HEIGHT // 2 - 100, "dark_fantasy_button.png", button_text, start_game)
    settings_button = ImageButton(WIDTH // 2, HEIGHT // 2, "dark_fantasy_button.png", "Настройки", settings_screen)
    exit_button = ImageButton(WIDTH // 2, HEIGHT // 2 + 100, "dark_fantasy_button.png", "Выйти", exit_game)

    running = True
    while running:
        draw_background()
        start_button.draw(screen)
        settings_button.draw(screen)
        exit_button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            start_button.check_click(event)
            settings_button.check_click(event)
            exit_button.check_click(event)


def start_game():
    game_loop()


def settings_screen():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Настройки")
    global music_playing
    global music_volume
    music_button = ImageButton(WIDTH // 2, HEIGHT // 2 - 50, "dark_fantasy_button.png",
                               "Выключить музыку" if music_playing else "Включить музыку", toggle_music)
    volume_slider_rect = pygame.Rect(WIDTH // 4, HEIGHT // 2 + 50, WIDTH // 2, 20)
    volume_slider_thumb = pygame.Rect(WIDTH // 4 + (WIDTH // 2) * (music_volume / 100), HEIGHT // 2 + 40, 20, 40)
    back_button = ImageButton(WIDTH // 2, HEIGHT // 2 + 150, "dark_fantasy_button.png", "Назад", go_back_to_game)

    while True:
        draw_background()
        music_button.text = "Выкл музыку" if music_playing else "Вкл музыку"
        music_button.draw(screen)
        pygame.draw.rect(screen, LIGHT_TEXT, volume_slider_rect)
        pygame.draw.rect(screen, BLACK, volume_slider_thumb)
        draw_text(screen, f"Громкость: {int(music_volume)}%", (WIDTH // 2 - 75, HEIGHT // 2 + 130), LIGHT_TEXT)
        back_button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            music_button.check_click(event)
            back_button.check_click(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return


def go_back_to_game():
    return


def toggle_music():
    global music_playing
    if music_playing:
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()
    music_playing = not music_playing


def go_back_to_main_menu():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    create_main_menu(screen)


def exit_game():
    pygame.quit()
    exit()


def register_screen():
    users = load_users()
    login, password, confirm_password = input_screen("Регистрация",
                                                     ["Придумайте логин:", "Введите пароль:", "Подтвердите пароль:"])
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    draw_background()
    if login in users:
        draw_text(screen, "Логин занят!", (200, 250), (255, 0, 0))
    elif password != confirm_password:
        draw_text(screen, "Пароли не совпадают!", (200, 250), (255, 0, 0))
    else:
        save_user(login, password)
        draw_text(screen, "Регистрация успешна!", (200, 250), (0, 255, 0))
        pygame.display.flip()
        pygame.time.wait(800)
        main_menu(screen)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((100, 100))  # Увеличен размер в 2 раза
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        self.hp = 100
        self.damage = 5
        self.speed = 5
        self.attack_cooldown = 0.5
        self.last_attack_time = 0
        self.attack_range = self.rect.width * 2  # Атака в 2 раза больше размера

    def attack(self, direction, monsters):
        global kills
        now = pygame.time.get_ticks() / 1000
        if now - self.last_attack_time >= self.attack_cooldown:
            self.last_attack_time = now
            for monster in list(monsters):
                if (direction == "left" and monster.rect.x < self.rect.x and abs(
                        monster.rect.x - self.rect.x) <= self.attack_range) or \
                        (direction == "right" and monster.rect.x > self.rect.x and abs(
                            monster.rect.x - self.rect.x) <= self.attack_range):
                    monster.hp -= self.damage
                    if monster.hp <= 0:
                        monsters.remove(monster)
                        kills += 1

    def update(self, keys):
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            if not self.rect.colliderect(player.rect):
                self.rect.x += self.speed

# Классы монстров
class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y, hp, damage, speed):
        super().__init__()
        self.image = pygame.Surface((80, 80))  # Увеличен размер в 2 раза
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = hp
        self.damage = damage
        self.speed = speed
        self.attack_cooldown = 1
        self.last_attack_time = 0

    def update(self, player):
        self.rect.x += self.speed
        if self.rect.colliderect(player.rect):
            now = pygame.time.get_ticks() / 1000
            if now - self.last_attack_time >= self.attack_cooldown:
                self.last_attack_time = now
                player.hp -= self.damage


def pause_menu():
    global paused
    paused = True
    while paused:
        screen.fill(BLACK)
        draw_text(screen, "Пауза", (WIDTH // 2 - 50, HEIGHT // 2 - 100))
        exit_button = ImageButton(WIDTH // 2, HEIGHT // 2, "dark_fantasy_button.png", "Выйти", exit_game)
        settings_button = ImageButton(WIDTH // 2, HEIGHT // 2 + 100, "dark_fantasy_button.png", "Настройки",
                                      settings_screen)
        exit_button.draw(screen)
        settings_button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            exit_button.check_click(event)
            settings_button.check_click(event)


def spawn_wave(wave):
    monsters = pygame.sprite.Group()
    count_walkers = 5 + (wave - 1)  # Каждый новый уровень добавляет 1 монстра

    for _ in range(count_walkers):
        x = random.choice([-50, WIDTH + 50])
        monsters.add(Monster(x, HEIGHT - 100, 5, 10, random.choice([-2, 2])))

    return monsters


def draw_background():
    background = pygame.image.load(BACKGROUND_IMAGE_PATH)
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))


# Главная игровая функция
def game_loop():
    global paused, kills
    paused = False
    player = Player()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    wave = 1
    kills = 0
    wave_start_time = pygame.time.get_ticks() / 1000
    monsters = spawn_wave(wave) or pygame.sprite.Group()
    running = True

    while running:
        keys = pygame.key.get_pressed()
        player.update(keys)

        if paused:
            pause_menu()
        draw_background()
        all_sprites.update(keys)
        monsters.update(player)
        all_sprites.draw(screen)
        monsters.draw(screen)

        elapsed_time = int(pygame.time.get_ticks() / 1000 - wave_start_time)
        draw_text(screen, f"Волна: {wave}", (20, 20))
        draw_text(screen, f"Таймер: {elapsed_time}", (20, 60))
        draw_text(screen, f"Убийства: {kills}", (20, 100))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    player.attack("left", monsters)
                elif event.button == 3:
                    player.attack("right", monsters)

        if not monsters.sprites():
            wave += 1
            wave_start_time = pygame.time.get_ticks() / 1000
            monsters = spawn_wave(wave) or pygame.sprite.Group()

        clock.tick(60)


def toggle_pause():
    global paused
    paused = not paused


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    music_playing = True
    music_volume = 10

    pygame.mixer.music.load(MUSIC_FILE_PATH)
    pygame.mixer.music.set_volume(music_volume / 100)
    pygame.mixer.music.play(-1, 0.0)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Система входа")
    main_menu(screen)
