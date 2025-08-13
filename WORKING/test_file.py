import pygame
import math
from typing import Tuple, List
from cube import *
from hud import *


# ----------------------------
# Constants & Initialization
# ----------------------------
pygame.init()
WIDTH, HEIGHT = 900, 900
SCREEN       = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK        = pygame.time.Clock()
FPS_TARGET   = 60

from bullet_system import WIDTH, HEIGHT, EmitterManager, init_emitters

# Font for counters
FONT         = pygame.font.SysFont("Arial", 18)
CENTER       = (WIDTH // 2, HEIGHT // 2)

# Circle settings
RADIUS = 800 // 2  # diameter to radius
COLOR = (128, 128, 128)  # bright red
THICKNESS = 2        # outline thickness

# Bullet settings
BULLET_RADIUS      = 4
BULLET_COLOR       = (255, 100, 255)
STRAIGHT_SPEED     = 4
ORBIT_EXPAND_SPEED = 2
BASE_ROT_SPEED     = math.radians(10) / FPS_TARGET  # 10° per second

# Sinusoidal movement settings
SINE_AMPLITUDE     = 6
SINE_FREQUENCY     = 0.15

# Screen-edge radius for full diagonal line
EDGE_RADIUS        = math.hypot(WIDTH, HEIGHT) / 2

# Emission settings
EMISSION_INTERVAL = 30  # frames between spawns
ORBIT_CYCLE_LIMIT = 5   # orbiting emissions before fly-out

# Precompute screen-corner radius for line emitter
EDGE_RADIUS = math.hypot(WIDTH/2, HEIGHT/2)

# ----------------------------
# Main Game Loop
# ----------------------------
def main():
    
    # --- Initialize game assets
    manager = EmitterManager()
    init_emitters(manager)
    cube = CubeRenderer(center=CENTER)
    hud = HUDRenderer(font=FONT)

    running = True
    while running:
        CLOCK.tick(FPS_TARGET)
        SCREEN.fill((0, 0, 0))

        pygame.draw.circle(SCREEN, COLOR, CENTER, RADIUS, THICKNESS)

        # --- Cube updates
        dt = CLOCK.get_time() / 1000.0
        cube.update(dt)
        cube.draw(SCREEN)

        # --- Grid overlay
        grid_color = (40, 40, 40)
        spacing = 100
        for x in range(0, WIDTH, spacing):
            pygame.draw.line(SCREEN, grid_color, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, spacing):
            pygame.draw.line(SCREEN, grid_color, (0, y), (WIDTH, y))

        # --- Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # toggle each pattern independently
                if event.key == pygame.K_1:
                    manager.toggle("straight")
                elif event.key == pygame.K_2:
                    manager.toggle("orbiting")
                elif event.key == pygame.K_3:
                    manager.toggle("sine")
                elif event.key == pygame.K_4:
                    manager.toggle("line")
                elif event.key == pygame.K_5:
                    manager.toggle("curve")

        manager.update()

        manager.draw(SCREEN)

        # --- HUD
        bullet_count = sum(
            len(manager.emitters[name].bullets)
            for name, active in manager.active.items()
            if active
        )
        hud.draw(SCREEN, CLOCK.get_fps(), bullet_count)

        pygame.display.flip()

    pygame.quit()
if __name__ == "__main__":
    main()