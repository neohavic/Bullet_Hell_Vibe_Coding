import pygame
from typing import Tuple, List

class HUDRenderer:
    def __init__(self, font: pygame.font.Font, position: Tuple[int, int] = (10, 10), color: Tuple[int, int, int] = (255, 255, 255)):
        self.font = font
        self.x, self.y = position
        self.color = color
        self.debug_logs: List[str] = []
        self.max_lines = 5  # Show last 5 debug messages

    def log(self, message: str) -> None:
        self.debug_logs.append(message)
        if len(self.debug_logs) > self.max_lines:
            self.debug_logs.pop(0)

    def draw(self, surface: pygame.Surface, fps: float, bullet_count: int) -> None:
        fps_text = self.font.render(f"FPS: {fps:.1f}", True, self.color)
        bullet_text = self.font.render(f"Bullets: {bullet_count}", True, self.color)

        surface.blit(fps_text, (self.x, self.y))
        surface.blit(bullet_text, (self.x, self.y + 20))

        self.draw_debug(surface)

    def draw_debug(self, surface: pygame.Surface) -> None:
        for i, msg in enumerate(self.debug_logs):
            debug_text = self.font.render(msg, True, self.color)
            surface.blit(debug_text, (self.x, self.y + 50 + i * 20))
