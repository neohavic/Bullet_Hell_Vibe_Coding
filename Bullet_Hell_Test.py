'''
BULLET HELL VIBE CODING TEST

-Ausin Everman w/ MS Copilot on Win11
Started: 08/05/25

Seeing how far vibe coding can go, especially for a more niche gaming category as Bullet Hell/Danmaku.
Goals are twofold: Can vibe coding, and AI specifically, build something from scratch that mimics the likes
of early Touhou? And two, can Python via PyGame handle something like that with a minimum 60 FPS.

GOALS: 
    -500+ bullets, minimum
    -Complex, Danmaku bullet patterns
    -Boss rush only, minimum 3 bosses
    -Full music sound track
    -Full suite of sound effects

IDEAS:
    -At least two ships, traditional faster but weaker shots and slower but stronger shots, or maybe only one
    with switchable firing modes
    -Some kind of scoring system that rewards risk; buzzing maybe, even though I personally hate it? Possibly
    the only way if its boss-rush only... time rewards are obvious. Maybe a sword mechanic a la Radiant:
        Sword parry -> powerup attack -> faster boss kill -> higher score
    -??? (I'm sure there will be more)
          
TO-DO
    -Refactor code into def's
    -Tighten up main game loop (see above)
    -GRAPHICS!
    -SOUND!
    -Score system
    -Player attacks
    -Player death

'''

import pygame
import sys
import time
import math

# At the top of your code
start_time = time.time()
SWEEP_AMPLITUDE = 30  # degrees
SWEEP_CENTER = 90     # degrees
SWEEP_SPEED = 15      # degrees per second

# Initialize PyGame
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
font = pygame.font.SysFont(None, 60)

# Fullscreen setup
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("Bullet Hell Vibe Coding Test")

# Constants
PLAYER_SPEED = 5
PLAYER_SIZE = 50  # 50% smaller
HUD_WIDTH = SCREEN_WIDTH // 4  # 25% of screen width
HUD_LINE_WIDTH = 8

# Load and scale player image
player_image = pygame.image.load("assets/images/player_ship.png").convert_alpha()
player_image = pygame.transform.scale(player_image, (PLAYER_SIZE, PLAYER_SIZE))
player_rect = player_image.get_rect()

# Player setup (center-left of playable area)
player_rect.center = (
    (SCREEN_WIDTH - HUD_WIDTH) // 2,
    SCREEN_HEIGHT // 2
)

# Projectile setup
projectiles = []
PROJECTILE_SPEED = 5
EMIT_INTERVAL = 10  # ticks
MAX_PROJECTILES = 100
tick_counter = 0

# Emitter position (center-top of playfield)
emitter_x = (SCREEN_WIDTH - HUD_WIDTH) // 2
emitter_y = 0

def emit_projectiles():
    # Time-based oscillation
    elapsed = time.time() - start_time
    sweep_angle = SWEEP_CENTER + SWEEP_AMPLITUDE * math.sin(
        math.radians(elapsed * SWEEP_SPEED * 360 / 60)
    )

    # Emit in a 60° cone centered on sweep_angle
    cone_start = sweep_angle - 30
    cone_end = sweep_angle + 30
    angles_deg = range(int(cone_start), int(cone_end) + 1, 10)

    for angle in angles_deg:
        angle_rad = math.radians(angle)
        dx = math.cos(angle_rad) * PROJECTILE_SPEED
        dy = math.sin(angle_rad) * PROJECTILE_SPEED
        projectiles.append({
            "x": emitter_x,
            "y": emitter_y,
            "dx": dx,
            "dy": dy
        })

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)

# Clock
clock = pygame.time.Clock()

# Main loop
running = True
while running:
    dt = clock.tick(60)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False

    # Get key states
    keys = pygame.key.get_pressed()

    # Movement
    dx = dy = 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        dx -= PLAYER_SPEED
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        dx += PLAYER_SPEED
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        dy -= PLAYER_SPEED
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        dy += PLAYER_SPEED

    player_rect.x += dx
    player_rect.y += dy

    # Emit projectiles every EMIT_INTERVAL ticks
    tick_counter += 1
    if tick_counter % EMIT_INTERVAL == 0 and len(projectiles) < MAX_PROJECTILES:
        emit_projectiles()

    # Update projectile positions
    for p in projectiles:
        p["x"] += p["dx"]
        p["y"] += p["dy"]

    # Cull projectiles outside playfield
    projectiles = [
        p for p in projectiles
        if 0 <= p["x"] <= SCREEN_WIDTH - HUD_WIDTH and 0 <= p["y"] <= SCREEN_HEIGHT
    ]

    # Clamp player within playfield
    max_x = SCREEN_WIDTH - HUD_WIDTH - player_rect.width
    player_rect.x = max(0, min(player_rect.x, max_x))
    player_rect.y = max(0, min(player_rect.y, SCREEN_HEIGHT - player_rect.height))

    # Draw background
    screen.fill(WHITE)

    # Draw HUD box
    hud_rect = pygame.Rect(SCREEN_WIDTH - HUD_WIDTH, 0, HUD_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, GRAY, hud_rect)
    pygame.draw.rect(screen, BLACK, hud_rect, HUD_LINE_WIDTH)

    # Draw player image
    screen.blit(player_image, player_rect)

    # Define hitbox rect
    hitbox_size = 6
    hitbox_rect = pygame.Rect(
        player_rect.centerx - hitbox_size // 2,
        player_rect.centery - hitbox_size // 2,
        hitbox_size,
        hitbox_size
        )
    # Draw player's hitbox as a light magenta box
    pygame.draw.rect(screen, (173, 216, 230), hitbox_rect)

    # Check for collisions
    hit = False
    for p in projectiles:
        projectile_rect = pygame.Rect(int(p["x"]) - 1, int(p["y"]) - 1, 4, 4)
        if hitbox_rect.colliderect(projectile_rect):
            hit = True
            break

    # Draw projectiles
    for p in projectiles:
        pygame.draw.circle(screen, (255, 0, 0), (int(p["x"]), int(p["y"])), 3)
        if hit:
            text_surface = font.render("HIT", True, (255, 0, 0))
            text_rect = text_surface.get_rect(center=hud_rect.center)
            screen.blit(text_surface, text_rect)

    # Update display
    pygame.display.flip()

# Quit PyGame
pygame.quit()
sys.exit()