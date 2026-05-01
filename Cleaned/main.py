"""Main game loop for Bullet Hell Vibe Coding."""

import settings
import pygame
import math
from typing import Tuple, List

from cube import CubeRenderer
from hud import HUDRenderer
from beat_pulse import BeatPulseController
from player import Player
from bullet_system import *
from emitter_manager import EmitterManager, initEmitters


def main():
    """Main game loop."""
    # Initialize pygame
    pygame.init()
    info = pygame.display.Info()
    settings.WIDTH = info.current_w
    settings.HEIGHT = info.current_h
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    
    # UI
    font = pygame.font.SysFont("Arial", 18)
    center = (settings.WIDTH // 2, settings.HEIGHT // 2)
    
    # Circle overlay
    radius = 400
    color = (128, 128, 128)
    thickness = 2
    
    # Initialize game systems
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

        # Draw circle overlay
        pygame.draw.circle(screen, color, center, radius, thickness)

        # Update and draw cube
        dt = clock.get_time() / 1000.0
        cubeRenderer.update(dt)
        cubeRenderer.draw(screen)

        # Draw grid
        gridColor = (40, 40, 40)
        spacing = 100
        for x in range(0, settings.WIDTH, spacing):
            pygame.draw.line(screen, gridColor, (x, 0), (x, settings.HEIGHT))
        for y in range(0, settings.HEIGHT, spacing):
            pygame.draw.line(screen, gridColor, (0, y), (settings.WIDTH, y))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Toggle patterns
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

        # Update player
        keys = pygame.key.get_pressed()
        playerCharacter.handleInput(keys)
        playerCharacter.update(keys)
        playerCharacter.draw(screen)

        # Update and draw bullets
        manager.update()
        manager.draw(screen)
        
        # Update audio-reactive effects
        amplitude = beatPulse.update(dt)
        cubeRenderer.baseSize = 10 * amplitude + 5

        # Draw HUD
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
