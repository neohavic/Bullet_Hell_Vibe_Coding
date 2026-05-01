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
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

clock = pygame.time.Clock()

# --- Font for counters
font = pygame.font.SysFont("Arial", 18)
center = (settings.WIDTH // 2, settings.HEIGHT // 2)

# --- Circle settings
radius = 800 // 2  # diameter to radius
color = (128, 128, 128)  # bright red
thickness = 2        # outline thickness

# --- Bullet settings
bulletRadius = 4
bulletColor = (255, 100, 255)
straightSpeed = 4
orbitExpandSpeed = 2
baseRotSpeed = math.radians(10) / settings.FPS_TARGET  # 10° per second

# --- Sinusoidal movement settings
sineAmplitude = 6
sineFrequency = 0.15

# --- Screen-edge radius for full diagonal line
edgeRadius = math.hypot(settings.WIDTH / 2, settings.HEIGHT / 2)

# --- Emission settings
emissionInterval = 30  # frames between spawns
orbitCycleLimit = 5   # orbiting emissions before fly-out

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
    initEmitters(manager)
    cubeRenderer = CubeRenderer(center=center)
    hudRenderer = HUDRenderer(font=font)
    beatPulse = BeatPulseController("assets/audio/test1_125bpm.wav")
    playerCharacter = Player(100, 100)

    running = True
    while running:
        clock.tick(settings.FPS_TARGET)
        screen.fill((0, 0, 0))

        pygame.draw.circle(screen, color, center, radius, thickness)

        # --- Cube updates
        dt = clock.get_time() / 1000.0
        cubeRenderer.update(dt)
        cubeRenderer.draw(screen)

        # --- Grid overlay
        gridColor = (40, 40, 40)
        spacing = 100
        for x in range(0, settings.WIDTH, spacing):
            pygame.draw.line(screen, gridColor, (x, 0), (x, settings.HEIGHT))
        for y in range(0, settings.HEIGHT, spacing):
            pygame.draw.line(screen, gridColor, (0, y), (settings.WIDTH, y))

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
        playerCharacter.handleInput(keys)

        enemyCenter = (settings.WIDTH // 2, settings.HEIGHT // 2)

        playerCharacter.update(keys)
        playerCharacter.draw(screen)

        manager.update()
        manager.draw(screen)
        
        # --- Pulse cube based
        amplitude = beatPulse.update(dt)
        cubeRenderer.baseSize = 10 * amplitude + 5

        # --- HUD
        bulletCount = sum(
            len(manager.emitters[name].bullets)
            for name, active in manager.active.items()
            if active
        )
        hudRenderer.draw(screen, clock.get_fps(), bulletCount)

        pygame.display.flip()

    pygame.quit()
    
if __name__ == "__main__":
    main()
