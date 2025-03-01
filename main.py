import random

import pygame
import os


WIDTH, HEIGHT = 1920, 1080
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (50, 50, 50)
LIGHT_TEXT = (255, 255, 255)
DARK_TEXT = (200, 200, 200)
db_file = "game_database.db"
BACKGROUND_IMAGE_PATH = "back.webp"
MUSIC_FILE_PATH = "back_music.mp3"
GAME_BACK = "back.jpg"


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


class Player:
    def __init__(self):
        self.image = pygame.Surface((50, 100))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 50))
        self.speed = 5
        self.hp = 100
        self.max_hp = 100
        self.damage = 5
        self.attack_cooldown = 100
        self.last_attack_time = 0

    def move(self, keys, monsters):
        dx = 0
        if keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_d]:
            dx = self.speed

        self.rect.x += dx
        for monster in monsters:
            if self.rect.colliderect(monster.rect):
                self.rect.x -= dx

    def attack(self, monsters):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.last_attack_time = current_time
            attack_rect = pygame.Rect(self.rect.x - self.rect.width * 2, self.rect.y, self.rect.width * 4, self.rect.height)
            for monster in monsters[:]:
                if attack_rect.colliderect(monster.rect):
                    monster.hp -= self.damage
                    if monster.hp <= 0:
                        monsters.remove(monster)
                        return 1
        return 0


class Monster:
    def __init__(self, x):
        self.image = pygame.Surface((50, 100))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(midbottom=(x, HEIGHT - 50))
        self.hp = 10
        self.damage = 5
        self.speed = 2
        self.last_attack_time = 0
        self.attack_cooldown = 2000

    def move_towards_player(self, player):
        if self.rect.x < player.rect.x:
            self.rect.x += self.speed
        elif self.rect.x > player.rect.x:
            self.rect.x -= self.speed

    def attack(self, player):
        current_time = pygame.time.get_ticks()
        if self.rect.colliderect(player.rect) and current_time - self.last_attack_time >= self.attack_cooldown:
            self.last_attack_time = current_time
            player.hp -= self.damage


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
        draw_background(screen)
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
        draw_background(screen)
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
    draw_background(screen)
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
    draw_background(screen)
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
    start_button = ImageButton(WIDTH // 2, HEIGHT // 2 - 100, "dark_fantasy_button.png", "Начать", start_game)
    settings_button = ImageButton(WIDTH // 2, HEIGHT // 2, "dark_fantasy_button.png", "Настройки", settings_screen)
    exit_button = ImageButton(WIDTH // 2, HEIGHT // 2 + 100, "dark_fantasy_button.png", "Выйти", exit_game)
    running = True
    while running:
        draw_background(screen)
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
    back_button = ImageButton(WIDTH // 2, HEIGHT // 2 + 150, "dark_fantasy_button.png", "Назад", go_back_to_main_menu)
    running = True
    while running:
        draw_background(screen)
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
            if event.type == pygame.MOUSEBUTTONDOWN:
                if volume_slider_rect.collidepoint(event.pos):
                    music_volume = (event.pos[0] - volume_slider_rect.left) / volume_slider_rect.width * 100
                    music_volume = max(0, min(music_volume, 100))
                    pygame.mixer.music.set_volume(music_volume / 100)
                    volume_slider_thumb.x = volume_slider_rect.left + (volume_slider_rect.width * (music_volume / 100))
            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    if volume_slider_rect.collidepoint(event.pos):
                        music_volume = (event.pos[0] - volume_slider_rect.left) / volume_slider_rect.width * 100
                        music_volume = max(0, min(music_volume, 100))
                        pygame.mixer.music.set_volume(music_volume / 100)
                        volume_slider_thumb.x = volume_slider_rect.left + (
                                volume_slider_rect.width * (music_volume / 100))


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
    draw_background(screen)

    if login in users:
        show_message(screen, "Логин занят!", (255, 0, 0))
    elif password != confirm_password:
        show_message(screen, "Пароли не совпадают!", (255, 0, 0))
    else:
        save_user(login, password)
        show_message(screen, "Регистрация успешна!", (0, 255, 0))
        main_menu(screen)


def draw_ui(screen, player, wave, kills, time_elapsed):
    font = pygame.font.Font(None, 40)
    hp_text = font.render(f"HP: {player.hp}/{player.max_hp}", True, LIGHT_TEXT)
    screen.blit(hp_text, (20, 20))
    wave_text = font.render(f"Wave: {wave}", True, LIGHT_TEXT)
    screen.blit(wave_text, (20, 60))
    kills_text = font.render(f"Kills: {kills}", True, LIGHT_TEXT)
    screen.blit(kills_text, (20, 100))
    timer_text = font.render(f"Time: {time_elapsed // 1000}s", True, LIGHT_TEXT)
    screen.blit(timer_text, (20, 140))


def game_loop():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Игра")
    background = pygame.image.load(GAME_BACK)
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    player = Player()
    monsters = []
    wave = 1
    monster_count = 5
    kills = 0
    wave_timer = pygame.time.get_ticks()
    running = True
    clock = pygame.time.Clock()
    game_over = False

    def spawn_wave():
        nonlocal monsters, monster_count, wave_timer
        monsters = [Monster(random.choice([random.randint(0, WIDTH // 3), random.randint(WIDTH * 2 // 3, WIDTH)])) for _ in range(monster_count)]
        monster_count += 1 if wave < 10 else 3
        wave_timer = pygame.time.get_ticks()

    spawn_wave()

    while running:
        screen.blit(background, (0, 0))
        keys = pygame.key.get_pressed()
        player.move(keys, monsters)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (1, 3):
                    kills += player.attack(monsters)

        if game_over:
            font = pygame.font.Font(None, 80)
            text = font.render(f"Вы проиграли! Вы пережили {wave} волн.", True, (255, 0, 0))
            screen.blit(text, (WIDTH // 3, HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(3000)
            return

        for monster in monsters[:]:
            monster.move_towards_player(player)
            monster.attack(player)
            if monster.hp <= 0:
                monsters.remove(monster)
                kills += 1

        if not monsters:
            wave += 1
            spawn_wave()

        if player.hp <= 0:
            game_over = True

        screen.blit(player.image, player.rect)
        for monster in monsters:
            screen.blit(monster.image, monster.rect)

        draw_ui(screen, player, wave, kills, pygame.time.get_ticks())
        pygame.display.flip()
        clock.tick(60)


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
