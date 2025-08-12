import pygame
from typing import Tuple, List

class HUDRenderer:
    def __init__(self, font: pygame.font.Font, position: Tuple[int, int] = (10, 10), color: Tuple[int, int, int] = (255, 255, 255)):
        self.font = font
        self.x, self.y = position
        self.color = color

    def draw(self, surface: pygame.Surface, fps: float, bullet_count: int) -> None:
        fps_text = self.font.render(f"FPS: {fps:.1f}", True, self.color)
        bullet_text = self.font.render(f"Bullets: {bullet_count}", True, self.color)

        surface.blit(fps_text, (self.x, self.y))
        surface.blit(bullet_text, (self.x, self.y + 20))

