# ----------------------------
# Constants & Initialization
# ----------------------------

import settings
import pygame
import math

pygame.init()

# --- Get display information before setting the mode
info = pygame.display.Info()
settings.WIDTH = info.current_w
settings.HEIGHT = info.current_h
SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

CLOCK = pygame.time.Clock()

# --- Font for counters
FONT = pygame.font.SysFont("Arial", 18)
CENTER = (settings.WIDTH // 2, settings.HEIGHT // 2)

# --- Circle settings
RADIUS = 800 // 2  # diameter to radius
COLOR = (128, 128, 128)  # bright red
THICKNESS = 2        # outline thickness

# --- Bullet settings
BULLET_RADIUS = 4
BULLET_COLOR = (255, 100, 255)
STRAIGHT_SPEED = 4
ORBIT_EXPAND_SPEED = 2
BASE_ROT_SPEED = math.radians(10) / settings.FPS_TARGET  # 10° per second

# --- Sinusoidal movement settings
SINE_AMPLITUDE = 6
SINE_FREQUENCY = 0.15

# --- Screen-edge radius for full diagonal line
EDGE_RADIUS = math.hypot(settings.WIDTH / 2, settings.HEIGHT / 2)

# --- Emission settings
EMISSION_INTERVAL = 30  # frames between spawns
ORBIT_CYCLE_LIMIT = 5   # orbiting emissions before fly-out

# --- Precompute screen-corner radius for line emitter
EDGE_RADIUS = math.hypot(settings.WIDTH/2, settings.WIDTH/2)

# ----------------------------
# Main Game Loop
# ----------------------------

from typing import Tuple, List
from cube import *
from hud import *
from beat_pulse import BeatPulseController
from player import Player
from bullet_system import *
from emitter_manager import *

def main():
    
    # --- Initialize game assets
    manager = EmitterManager()
    init_emitters(manager)
    cube = CubeRenderer(center=CENTER)
    hud = HUDRenderer(font=FONT)
    pulse = BeatPulseController("assets/audio/test1_125bpm.wav")
    player = Player(100, 100)

    running = True
    while running:
        CLOCK.tick(settings.FPS_TARGET)
        SCREEN.fill((0, 0, 0))

        pygame.draw.circle(SCREEN, COLOR, CENTER, RADIUS, THICKNESS)

        # --- Cube updates
        dt = CLOCK.get_time() / 1000.0
        cube.update(dt)
        cube.draw(SCREEN)

        # --- Grid overlay
        grid_color = (40, 40, 40)
        spacing = 100
        for x in range(0, settings.WIDTH, spacing):
            pygame.draw.line(SCREEN, grid_color, (x, 0), (x, settings.HEIGHT))
        for y in range(0, settings.HEIGHT, spacing):
            pygame.draw.line(SCREEN, grid_color, (0, y), (settings.WIDTH, y))

        # --- Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # --- Toggle each pattern independently
                elif event.key == pygame.K_1:
                    manager.toggle("straight")
                elif event.key == pygame.K_2:
                    manager.toggle("orbiting")
                elif event.key == pygame.K_3:
                    manager.toggle("sine")
                elif event.key == pygame.K_4:
                    manager.toggle("line")
                elif event.key == pygame.K_5:
                    manager.toggle("curve")
                    
        keys = pygame.key.get_pressed()
        player.handle_input(keys)

        enemy_center = (settings.WIDTH // 2, settings.HEIGHT // 2)

        player.update(keys)
        player.draw(SCREEN)

        manager.update()
        manager.draw(SCREEN)
        
        # --- Pulse cube based
        amp = pulse.update(dt)
        cube.base_size = 10 * amp + 5

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