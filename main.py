import pygame
import random
import sys
import json

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Doofus Adventure")
clock = pygame.time.Clock()

# Game settings
DOOFUS_SIZE = 50
PULPIT_SIZE = 90

# Load JSON configuration
with open('doofus_diary.json', 'r') as file:
    diary = json.load(file)

# Initial game settings
initial_speed = diary['player_data']['speed']
initial_min_pulpit_destroy_time = 4  # 4 seconds
initial_max_pulpit_destroy_time = 4  # 4 seconds
initial_pulpit_spawn_time = diary['pulpit_data']['pulpit_spawn_time']

# Level settings
levels = [
    {"speed": initial_speed, "min_destroy_time": initial_min_pulpit_destroy_time, "max_destroy_time": initial_max_pulpit_destroy_time, "spawn_time": initial_pulpit_spawn_time},
    {"speed": initial_speed + 1, "min_destroy_time": initial_min_pulpit_destroy_time - 1, "max_destroy_time": initial_max_pulpit_destroy_time - 1, "spawn_time": initial_pulpit_spawn_time - 1},
    {"speed": initial_speed + 2, "min_destroy_time": initial_min_pulpit_destroy_time - 2, "max_destroy_time": initial_max_pulpit_destroy_time - 2, "spawn_time": initial_pulpit_spawn_time - 2}
]

current_level = 0

class Doofus:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2, HEIGHT//2, DOOFUS_SIZE, DOOFUS_SIZE)
        self.color = (255, 255, 255)  # White color

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

class Pulpit:
    def __init__(self, x, y, timer):
        self.rect = pygame.Rect(x, y, PULPIT_SIZE, PULPIT_SIZE)
        self.timer = timer
        self.color = (0, 255, 0)  # Green color

    def update(self):
        self.timer -= 1
        return self.timer <= 0

    def draw_timer(self, surface):
        time_left = max(0, self.timer // 60)
        font = pygame.font.SysFont('arial', 24, bold=True)
        timer_surface = font.render(f'{time_left}', True, (255, 0, 0))  # Red color for timer
        # Display timer in the top-left corner of the pulpit
        surface.blit(timer_surface, (self.rect.x + 5, self.rect.y + 5))

def generate_pulpit(last_pulpit=None):
    if last_pulpit is None:
        x, y = WIDTH//2 - PULPIT_SIZE//2, HEIGHT//2 - PULPIT_SIZE//2
    else:
        directions = [(PULPIT_SIZE, 0), (-PULPIT_SIZE, 0), (0, PULPIT_SIZE), (0, -PULPIT_SIZE)]
        direction = random.choice(directions)
        x, y = last_pulpit.rect.x + direction[0], last_pulpit.rect.y + direction[1]
        x = max(0, min(WIDTH - PULPIT_SIZE, x))
        y = max(0, min(HEIGHT - PULPIT_SIZE, y))
    timer = random.randint(levels[current_level]['min_destroy_time'] * 60, levels[current_level]['max_destroy_time'] * 60)
    return Pulpit(x, y, timer)

def draw_text(surface, text, size, color, x, y):
    font = pygame.font.SysFont('arial', size, bold=True)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

def start_screen():
    screen.fill((0, 150, 0))  # Dark green background
    draw_text(screen, 'Doofus Adventure', 64, (255, 255, 255), WIDTH // 2, HEIGHT // 2 - 50)
    draw_text(screen, 'Press Enter to Start', 36, (255, 255, 255), WIDTH // 2, HEIGHT // 2 + 50)
    pygame.display.flip()

def game_over_screen(score):
    screen.fill((200, 0, 0))  # Red background
    draw_text(screen, 'Game Over!', 64, (255, 255, 255), WIDTH // 2, HEIGHT // 2 - 50)
    draw_text(screen, f'Your Score: {score}', 36, (255, 255, 255), WIDTH // 2, HEIGHT // 2 + 50)
    draw_text(screen, 'Press Enter to Restart', 36, (255, 255, 255), WIDTH // 2, HEIGHT // 2 + 100)
    pygame.display.flip()

def level_up_screen():
    screen.fill((0, 0, 200))  # Blue background
    draw_text(screen, f'Level {current_level + 1} Complete!', 64, (255, 255, 255), WIDTH // 2, HEIGHT // 2 - 50)
    draw_text(screen, 'Press Enter to Continue', 36, (255, 255, 255), WIDTH // 2, HEIGHT // 2 + 50)
    pygame.display.flip()

# Initialize game objects
doofus = Doofus()
pulpits = [generate_pulpit()]
score = 0

# Game state
START_SCREEN = 0
PLAYING = 1
GAME_OVER = 2
LEVEL_UP = 3
game_state = START_SCREEN

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    
    if game_state == START_SCREEN:
        start_screen()
        if keys[pygame.K_RETURN]:
            game_state = PLAYING
            doofus = Doofus()
            pulpits = [generate_pulpit()]
            score = 0
            current_level = 0
    
    elif game_state == PLAYING:
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            doofus.move(-levels[current_level]['speed'], 0)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            doofus.move(levels[current_level]['speed'], 0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            doofus.move(0, -levels[current_level]['speed'])
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            doofus.move(0, levels[current_level]['speed'])

        for pulpit in pulpits[:]:
            if pulpit.update():
                pulpits.remove(pulpit)
                score += 1

        if len(pulpits) < 2 and (not pulpits or pulpits[-1].timer <= levels[current_level]['spawn_time'] * 60):
            pulpits.append(generate_pulpit(pulpits[-1]))

        if not any(pulpit.rect.colliderect(doofus.rect) for pulpit in pulpits):
            game_state = GAME_OVER

        if score >= 7:
            if current_level < len(levels) - 1:
                game_state = LEVEL_UP
            else:
                game_state = GAME_OVER

        screen.fill((0, 0, 0))  # Black background
        for pulpit in pulpits:
            pygame.draw.rect(screen, pulpit.color, pulpit.rect)
            pulpit.draw_timer(screen)
        pygame.draw.rect(screen, doofus.color, doofus.rect)

        score_text = pygame.font.SysFont('arial', 36).render(f'Score: {score}', True, (255, 255, 255))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

        pygame.display.flip()
        clock.tick(60)
    
    elif game_state == GAME_OVER:
        game_over_screen(score)
        if keys[pygame.K_RETURN]:
            game_state = START_SCREEN

    elif game_state == LEVEL_UP:
        level_up_screen()
        if keys[pygame.K_RETURN]:
            current_level += 1
            game_state = PLAYING
            doofus = Doofus()
            pulpits = [generate_pulpit()]
            score = 0
