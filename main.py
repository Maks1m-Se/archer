import pygame
import os
import math
import random
import time
import asyncio

pygame.font.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 1000, 500
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (174, 0, 168)
YELLOW = (255, 255, 0)

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Archery Game with Gravity and Moving Target")

BORDER = pygame.Rect(WIDTH // 2 - 5, 0, 10, HEIGHT)

HEALTH_FONT = pygame.font.SysFont('comicsans', 40)
WINNER_FONT = pygame.font.SysFont('comicsans', 100)

FPS = 60
VEL = 5
ARROW_VEL = 27 # Initial speed of the arrow
GRAVITY = 0.5   # Gravity effect on the arrow
MAX_ARROWS = 3
PLAYER_WIDTH, PLAYER_HEIGHT = 50, 50
ARROW_WIDTH, ARROW_HEIGHT = 30, 5  # Adjusted for arrow image size
#TARGET_VEL = 3  # Velocity of the moving target
ANGLE = 18  # Initial angle of the arrow in degrees
prev_second = 11 # var for ticks at the end

# Timer variables
max_time = 30


# Set up font
font = pygame.font.Font(None, 20)
end_font = pygame.font.Font(None, 50)


#Button Play Again
BUTTON_COLOR = (240, 0, 240)
BUTTON_HOVER_COLOR = (130, 100, 120)
BUTTON_TEXT_COLOR = (0, 0, 0)
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50

def draw_button(text, font, rect, color, hover_color, text_color):
    mouse_pos = pygame.mouse.get_pos()
    button_color = hover_color if rect.collidepoint(mouse_pos) else color
    pygame.draw.rect(WINDOW, button_color, rect)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    WINDOW.blit(text_surf, text_rect)

def is_button_clicked(rect):
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()
    return rect.collidepoint(mouse_pos) and mouse_click[0]

# Player, Arrow, Obsticles, Targets
PLAYER_IMAGE = pygame.image.load(os.path.join('images', 'archer_stickman.png'))
PLAYER = pygame.transform.scale(PLAYER_IMAGE, (PLAYER_WIDTH, PLAYER_HEIGHT))
ARROW_IMAGE = pygame.image.load(os.path.join('images', 'arrow.png'))
ARROW_IMAGE = pygame.transform.scale(ARROW_IMAGE, (ARROW_WIDTH, ARROW_HEIGHT))

hit_obst_sound = pygame.mixer.Sound(os.path.join('sounds', 'hit_obst.ogg'))
hit_targ_sound = pygame.mixer.Sound(os.path.join('sounds', 'hit_targ.ogg'))
game_over_sound = pygame.mixer.Sound(os.path.join('sounds', 'game_over.ogg'))
shot_sound = pygame.mixer.Sound(os.path.join('sounds', 'shot.ogg'))
time_ticks_sound = pygame.mixer.Sound(os.path.join('sounds', 'time_ticks.ogg'))
hit_obst_sound.set_volume(.2)

# Initial positions
PLAYER_POS = (50, HEIGHT // 2 - PLAYER_HEIGHT // 2)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = PLAYER
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = VEL

    def move(self, direction):
        if direction == "up" and self.rect.top > 0:
            self.rect.y -= self.vel
        if direction == "down" and self.rect.bottom < HEIGHT+55:
            self.rect.y += self.vel

    def draw(self, window):
        window.blit(self.image, self.rect.topleft)

class Target:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.width = width
        self.height = height
        self.color = PURPLE
        self.velocity = random.randint(0,5)
        self.direction = 1  # 1: down, -1: up
    
    def move(self):
        self.rect.y += self.velocity * self.direction
        if self.rect.top <= 0:
            self.rect.top = 0
            self.direction *= -1
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.direction *= -1
    
    def draw(self, window):
        pygame.draw.rect(window, self.color, self.rect)

class Obsticle:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.width = width
        self.height = height
        self.color = BLACK
        self.velocity = random.randint(0,5)
        self.direction = 1  # 1: down, -1: up
    
    def move(self):
        self.rect.y += self.velocity * self.direction
        if self.rect.top <= 0:
            self.rect.top = 0
            self.direction *= -1
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.direction *= -1
    
    def draw(self, window):
        pygame.draw.rect(window, self.color, self.rect)

def draw_window(player, arrows, targets, obsticles, score, total_time_text):
    WINDOW.fill(WHITE)
    pygame.draw.rect(WINDOW, BLACK, BORDER)

    # Draw player
    player.draw(WINDOW)

    # Draw arrows
    for arrow in arrows:
        # Calculate the angle based on current velocities
        current_angle = math.degrees(math.atan2(-arrow[2], arrow[3]))  # Invert y to match pygame coordinates
        rotated_arrow = pygame.transform.rotate(ARROW_IMAGE, current_angle)
        new_rect = rotated_arrow.get_rect(center=arrow[1].center)
        WINDOW.blit(rotated_arrow, new_rect.topleft)

    # Draw targets
    for target in targets:
        target.draw(WINDOW)

    # Draw obsticles
    for obsticle in obsticles:
        obsticle.draw(WINDOW)

    # Draw score
    score_text = HEALTH_FONT.render(f"Score: {score}", 1, BLACK)
    WINDOW.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))
    WINDOW.blit(total_time_text, (10, 10))

    pygame.display.update()

def handle_arrows(arrows):
    for arrow in arrows:
        arrow[1].x += arrow[3]  # Horizontal velocity
        arrow[2] += GRAVITY  # Gravity increases vertical velocity
        arrow[1].y += arrow[2]  # Update y position with vertical velocity
        if arrow[1].x > WIDTH or arrow[1].y > HEIGHT*1.5 or arrow[1].y < -HEIGHT*0.5:
            arrows.remove(arrow)

def check_collision_targ(arrows, targets):
    hit_targets = []
    for target in targets:
        for arrow in arrows:
            if target.rect.colliderect(arrow[1]):
                hit_targ_sound.play()
                arrows.remove(arrow)
                hit_targets.append(target)
                break
    return hit_targets

def check_collision_obst(arrows, obsticles):
    hit_obsticles = []
    for obsticle in obsticles:
        for arrow in arrows:
            if obsticle.rect.colliderect(arrow[1]):
                hit_obst_sound.play()
                arrows.remove(arrow)
                hit_obsticles.append(obsticle)
                break
    return hit_obsticles


## Game Loop ##
async def main():
    global max_time, prev_second, waiting_for_quit
    waiting_for_quit = True  # Reset the flag for each new game session
    player = Player(*PLAYER_POS)
    arrows = []
    score = 0
    clock = pygame.time.Clock()
    run = True
    start_time = time.time()
    elapsed_time = 0

    # Create initial targets
    targets = [
        Target(WIDTH - 100, HEIGHT // 4, 50, 33),
        Target(WIDTH - 100, HEIGHT // 4, 70, 42),
        Target(WIDTH - 300, HEIGHT // 4, 60, 50)
    ]

    # Create initial obsticles
    obsticles = [
        Obsticle(WIDTH * .6 , HEIGHT // 4, random.randint(15,25), random.randint(15,25)),
        Obsticle(WIDTH * .7, HEIGHT // 5, random.randint(15,30), random.randint(15,30)),
        Obsticle(WIDTH * .55, HEIGHT // 7, random.randint(25,35), random.randint(25,35))
    ]



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
                    arrow_rect = pygame.Rect(player.rect.right, player.rect.centery, ARROW_WIDTH, ARROW_HEIGHT)
                    arrows.append([ARROW_IMAGE, arrow_rect, init_vel_y, init_vel_x])  # [Image, Rect, vertical velocity, horizontal velocity]

        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_UP]:
            player.move("up")
        if keys_pressed[pygame.K_DOWN]:
            player.move("down")

        handle_arrows(arrows)

        # Move and draw targets
        for target in targets:
            target.move()

        # Move and draw obsticles
        for obsticle in obsticles:
            obsticle.move()

        hit_targets = check_collision_targ(arrows, targets)
        if hit_targets:
            score += len(hit_targets)
            targets = [target for target in targets if target not in hit_targets]
            if not targets:
                # Respawn targets if all are hit
                targets = [
                    Target(random.randint(WIDTH // 2, WIDTH - 50), random.randint(0, HEIGHT - 50), random.randint(30, 70), random.randint(30, 70))
                    for _ in range(3)
                ]
        
        hit_obsticles = check_collision_obst(arrows, obsticles)
        if hit_obsticles:
            score -= len(hit_obsticles)
            obsticles = [obsticle for obsticle in obsticles if obsticle not in hit_obsticles]
            if not obsticles:
                # Respawn obsticle if all are hit
                obsticles = [
                    Obsticle(random.randint(WIDTH // 2, WIDTH - 50), random.randint(0, HEIGHT - 50), random.randint(30, 70), random.randint(30, 70))
                    for _ in range(3)
                ]

        elapsed_time = max_time - (time.time() - start_time)

        if elapsed_time <= 10:
            next_second = int(elapsed_time)
            if prev_second != next_second:
                time_ticks_sound.play()
            
            prev_second = next_second
            

        if elapsed_time <= 0:
            await end(score)
            break

        # Display the total time across all levels
        total_time_text = font.render(f"Time left: {int(elapsed_time)} s", True, BLACK)
        

        draw_window(player, arrows, targets, obsticles, score, total_time_text)

        await asyncio.sleep(0)


## End Loop #
waiting_for_quit = True
async def end(score):
    global waiting_for_quit
    pygame.mixer.stop()
    game_over_sound.play()

    # End game screen
    WINDOW.fill((210, 210, 230))
    end_text = end_font.render(f"Game finished!\nTotal Points: {score}", True, BLACK)
    end_text_rect = end_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    WINDOW.blit(end_text, end_text_rect)

    # Button rect
    button_rect = pygame.Rect(WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 2 + 20, BUTTON_WIDTH, BUTTON_HEIGHT)
    draw_button("Play Again", end_font, button_rect, BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR)

    pygame.display.flip()

    while waiting_for_quit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting_for_quit = False
            if is_button_clicked(button_rect):
                waiting_for_quit = False
                await main()  # Restart the game

        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())


# Quit the game
pygame.quit()