'''
BULLET HELL VIBE CODING TEST

-Ausin Everman w/ MS Copilot on Win11  
Started: 08/05/25

Seeing how far vibe coding can go, especially for a more niche gaming
category as Bullet Hell/Danmaku.  
Goals are twofold: Can vibe coding, and AI specifically, build something
from scratch that mimics the likes of early Touhou? And two, can Python via
PyGame handle something like that with a minimum 60 FPS.

GOALS:
    - 500+ bullets, minimum
    - Complex, Danmaku bullet patterns
    - Boss rush only, minimum 3 bosses
    - Full music soundtrack
    - Full suite of sound effects

IDEAS:
    - At least two ships, traditional faster but weaker shots and slower but
      stronger shots, or maybe only one with switchable firing modes
    - Some kind of scoring system that rewards risk; buzzing maybe, even though
      I personally hate it? Possibly the only way if it's boss-rush only...
      time rewards are obvious. Maybe a sword mechanic a la Radiant:
          Sword parry -> powerup attack -> faster boss kill -> higher score
    - ??? (I'm sure there will be more)

TO-DO
    - Refactor code into def's
    - Tighten up main game loop
    - GRAPHICS!
    - SOUND!
    - Score system
    - Player attacks
    - Player death
'''

import pygame
import sys
import time
import math

# --- Time‐based sweep setup ---
start_time      = time.time()
SWEEP_AMPLITUDE = 30    # degrees
SWEEP_CENTER    = 90    # degrees
SWEEP_SPEED     = 15    # degrees per second

# --- PyGame Initialization ---
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Bullet Hell Vibe Coding Test")
font  = pygame.font.SysFont("Ariel", 60)
clock = pygame.time.Clock()

# --- Fullscreen dimensions ---
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

# --- Constants ---
PLAYER_SPEED         = 5
PLAYER_SIZE          = 50
HUD_WIDTH            = SCREEN_WIDTH // 4
HUD_LINE_WIDTH       = 8
PROJECTILE_SPEED     = 5
EMIT_INTERVAL        = 10     # ticks
MAX_PROJECTILES      = 100
PLAYER_BULLET_SPEED  = -8     # upward
PLAYER_FIRE_INTERVAL = 5      # ticks

# Enemy rectangle constants
ENEMY_WIDTH   = 200
ENEMY_HEIGHT  = 40
ENEMY_Y       = 50     # vertical position at top
ENEMY_SPEED   = 3      # horizontal speed

# --- Colors ---
WHITE        = (255, 255, 255)
GRAY         = (200, 200, 200)
BLACK        = (0, 0, 0)
RED          = (255, 0, 0)
BLUE         = (0, 0, 255)
HITBOX_COLOR = (173, 216, 230)

# --- Bullet class ---
class Bullet:
    def __init__(self, x, y, dx, dy, color=RED, radius=3):
        self.x      = x
        self.y      = y
        self.dx     = dx
        self.dy     = dy
        self.color  = color
        self.radius = radius

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, surface):
        pygame.draw.circle(surface, self.color,
                           (int(self.x), int(self.y)), self.radius)

    def is_off_screen(self):
        playfield_width = SCREEN_WIDTH - HUD_WIDTH
        return not (0 <= self.x <= playfield_width and 0 <= self.y <= SCREEN_HEIGHT)

    def get_rect(self):
        return pygame.Rect(
            int(self.x) - self.radius,
            int(self.y) - self.radius,
            self.radius * 2,
            self.radius * 2
        )

# --- Player class ---
class Player:
    def __init__(self, image_path, size, start_pos,
                 speed, fire_interval, playfield_width, playfield_height):
        raw_img            = pygame.image.load(image_path).convert_alpha()
        self.image         = pygame.transform.scale(raw_img, (size, size))
        self.rect          = self.image.get_rect(center=start_pos)
        self.speed         = speed
        self.min_x         = 0
        self.max_x         = playfield_width - size
        self.min_y         = 0
        self.max_y         = playfield_height - size
        self.fire_tick     = 0
        self.fire_interval = fire_interval
        self.bullets       = []
        self.hitbox_radius = 3

    def handle_input(self, keys):
        dx = dy = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += self.speed
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += self.speed

        self.rect.x = max(self.min_x, min(self.rect.x + dx, self.max_x))
        self.rect.y = max(self.min_y, min(self.rect.y + dy, self.max_y))

        return keys[pygame.K_SPACE]

    def update(self, space_pressed, bullet_speed):
        self.fire_tick += 1
        if space_pressed and self.fire_tick % self.fire_interval == 0:
            bx = self.rect.centerx
            by = self.rect.centery
            self.bullets.append(
                Bullet(bx, by, 0, bullet_speed, color=BLUE, radius=4)
            )
        if not space_pressed:
            self.fire_tick = 0

        for b in self.bullets:
            b.update()
        self.bullets = [b for b in self.bullets if not b.is_off_screen()]

    def draw(self, surface):
        for b in self.bullets:
            b.draw(surface)
        surface.blit(self.image, self.rect)
        cx, cy = self.rect.center
        pygame.draw.circle(surface, HITBOX_COLOR, (cx, cy), self.hitbox_radius)

    @property
    def hitbox_rect(self):
        cx, cy = self.rect.center
        r = self.hitbox_radius
        return pygame.Rect(cx - r, cy - r, 2 * r, 2 * r)

# --- Instantiate player ---
playfield_width  = SCREEN_WIDTH - HUD_WIDTH
playfield_height = SCREEN_HEIGHT
player = Player(
    image_path       = "assets/images/player_ship.png",
    size             = PLAYER_SIZE,
    start_pos        = (playfield_width // 2, playfield_height // 2),
    speed            = PLAYER_SPEED,
    fire_interval    = PLAYER_FIRE_INTERVAL,
    playfield_width  = playfield_width,
    playfield_height = playfield_height
)

# --- Projectile storage & emit state ---
enemy_projectiles  = []
tick_counter = 0

# --- Enemy state ---
enemy_x   = 0
enemy_dir = 1   # 1 = right, -1 = left

# --- Initial emitter (overwritten each frame) ---
emitter_x = enemy_x + ENEMY_WIDTH // 2
emitter_y = ENEMY_Y + ENEMY_HEIGHT

def emit_projectiles():
    """Emit a sweeping cone of bullets from (emitter_x, emitter_y)."""
    elapsed     = time.time() - start_time
    sweep_angle = SWEEP_CENTER + SWEEP_AMPLITUDE * math.sin(
        math.radians(elapsed * SWEEP_SPEED * 360 / 60)
    )
    for angle in range(int(sweep_angle - 30), int(sweep_angle + 31), 10):
        rad = math.radians(angle)
        dx  = math.cos(rad) * PROJECTILE_SPEED
        dy  = math.sin(rad) * PROJECTILE_SPEED
        enemy_projectiles.append(Bullet(emitter_x, emitter_y, dx, dy))

# --- Main loop ---
running = True
while running:
    dt = clock.tick(60)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
           event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    # Player input & update
    keys = pygame.key.get_pressed()
    space_pressed = player.handle_input(keys)
    player.update(space_pressed, PLAYER_BULLET_SPEED)

    # Move enemy and bounce
    enemy_x += ENEMY_SPEED * enemy_dir
    right_limit = SCREEN_WIDTH - HUD_WIDTH - ENEMY_WIDTH
    if enemy_x <= 0 or enemy_x >= right_limit:
        enemy_dir *= -1
        enemy_x = max(0, min(enemy_x, right_limit))

    # Reposition emitter under center-bottom of enemy
    emitter_x = enemy_x + ENEMY_WIDTH // 2
    emitter_y = ENEMY_Y + ENEMY_HEIGHT

    # Enemy projectile emission
    tick_counter += 1
    if tick_counter % EMIT_INTERVAL == 0 and len(enemy_projectiles) < MAX_PROJECTILES:
        emit_projectiles()

    # Update enemy projectiles
    for p in enemy_projectiles:
        p.update()
    enemy_projectiles = [p for p in enemy_projectiles if not p.is_off_screen()]

    # Collision detection
    hit = any(player.hitbox_rect.colliderect(p.get_rect()) for p in enemy_projectiles)

    # Drawing
    screen.fill(WHITE)

    # Draw enemy rectangle
    enemy_rect = pygame.Rect(enemy_x, ENEMY_Y, ENEMY_WIDTH, ENEMY_HEIGHT)
    pygame.draw.rect(screen, BLACK, enemy_rect)
    pygame.draw.rect(screen, WHITE, enemy_rect, 2)

    # Draw player and bullets
    player.draw(screen)
    for p in enemy_projectiles:
        p.draw(screen)

    # Show "HIT" when collision occurs
    if hit:
        hit_text = font.render("HIT", True, RED)
        hit_rect = hit_text.get_rect(center=enemy_rect.center)
        screen.blit(hit_text, hit_rect)

    # Draw HUD panel
    hud_rect = pygame.Rect(SCREEN_WIDTH - HUD_WIDTH, 0, HUD_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, GRAY, hud_rect)
    pygame.draw.rect(screen, BLACK, hud_rect, HUD_LINE_WIDTH)

    # HUD: FPS & projectile count
    fps = int(clock.get_fps())
    total_proj = len(player.bullets) + len(enemy_projectiles)
    fps_text  = font.render(f"FPS: {fps}", True, BLACK)
    proj_text = font.render(f"Projectiles: {total_proj}", True, BLACK)
    screen.blit(fps_text,  (20, 20))
    screen.blit(proj_text, (20, 80))

    pygame.display.flip()

pygame.quit()
sys.exit()