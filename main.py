import pygame
import os
import math

pygame.font.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 900, 500
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Archery Game with Gravity and Moving Target")

BORDER = pygame.Rect(WIDTH // 2 - 5, 0, 10, HEIGHT)

HEALTH_FONT = pygame.font.SysFont('comicsans', 40)
WINNER_FONT = pygame.font.SysFont('comicsans', 100)

FPS = 60
VEL = 5
ARROW_VEL = 20  # Initial speed of the arrow
GRAVITY = 0.5   # Gravity effect on the arrow
MAX_ARROWS = 3
PLAYER_WIDTH, PLAYER_HEIGHT = 50, 50
ARROW_WIDTH, ARROW_HEIGHT = 10, 5
TARGET_VEL = 3  # Velocity of the moving target
ANGLE = 30  # Initial angle of the arrow in degrees

shot_sound = pygame.mixer.Sound(os.path.join('sounds', 'shot.mp3'))
hit_sound = pygame.mixer.Sound(os.path.join('sounds', 'hit.mp3'))


PLAYER_IMAGE = pygame.image.load(os.path.join('images', 'archer_stickman.png'))
PLAYER = pygame.transform.scale(PLAYER_IMAGE, (PLAYER_WIDTH, PLAYER_HEIGHT))

# Initial positions
PLAYER_POS = (50, HEIGHT // 2 - PLAYER_HEIGHT // 2)
TARGET_WIDTH, TARGET_HEIGHT = 50, 50
TARGET_POS = [WIDTH - TARGET_WIDTH - 20, HEIGHT // 2 - TARGET_HEIGHT // 2]
target_direction = 1  # 1: down, -1: up

def draw_window(player, arrows, score):
    WINDOW.fill(WHITE)
    pygame.draw.rect(WINDOW, BLACK, BORDER)

    # Draw player
    WINDOW.blit(player.image, player.rect.topleft)

    # Draw arrows
    for arrow in arrows:
        pygame.draw.rect(WINDOW, BLACK, arrow[0])

    # Draw target
    pygame.draw.rect(WINDOW, RED, TARGET_POS + [TARGET_WIDTH, TARGET_HEIGHT])

    # Draw score
    score_text = HEALTH_FONT.render(f"Score: {score}", 1, BLACK)
    WINDOW.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))

    pygame.display.update()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = PLAYER
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = VEL

    def move(self, direction):
        if direction == "up" and self.rect.top > 0:
            self.rect.y -= self.vel
        if direction == "down" and self.rect.bottom < HEIGHT:
            self.rect.y += self.vel

    def draw(self, window):
        window.blit(self.image, self.rect.topleft)

def handle_arrows(arrows):
    for arrow in arrows:
        arrow[0].x += arrow[2]  # Horizontal velocity
        arrow[1] += GRAVITY  # Gravity increases vertical velocity
        arrow[0].y += arrow[1]  # Update y position with vertical velocity
        if arrow[0].x > WIDTH or arrow[0].y > HEIGHT or arrow[0].y < 0:
            arrows.remove(arrow)

def check_collision(arrows, target_rect):
    for arrow in arrows:
        if target_rect.colliderect(arrow[0]):
            hit_sound.play()
            arrows.remove(arrow)
            return True
    return False

def move_target():
    global target_direction
    TARGET_POS[1] += TARGET_VEL * target_direction
    if TARGET_POS[1] <= 0 or TARGET_POS[1] + TARGET_HEIGHT >= HEIGHT:
        target_direction *= -1

def main():
    player = Player(*PLAYER_POS)
    arrows = []
    score = 0
    clock = pygame.time.Clock()
    run = True

    # Calculate the initial velocity components based on the angle
    angle_rad = math.radians(ANGLE)
    init_vel_x = ARROW_VEL * math.cos(angle_rad)
    init_vel_y = -ARROW_VEL * math.sin(angle_rad)

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and len(arrows) < MAX_ARROWS:
                    # Create an arrow with initial velocities
                    shot_sound.play()
                    arrow = pygame.Rect(player.rect.right, player.rect.centery, ARROW_WIDTH, ARROW_HEIGHT)
                    arrows.append([arrow, init_vel_y, init_vel_x])  # [Rect, vertical velocity, horizontal velocity]

        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_UP]:
            player.move("up")
        if keys_pressed[pygame.K_DOWN]:
            player.move("down")

        handle_arrows(arrows)

        target_rect = pygame.Rect(TARGET_POS + [TARGET_WIDTH, TARGET_HEIGHT])
        if check_collision(arrows, target_rect):
            score += 1

        move_target()
        draw_window(player, arrows, score)

if __name__ == "__main__":
    main()
