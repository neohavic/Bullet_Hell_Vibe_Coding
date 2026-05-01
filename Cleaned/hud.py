"""Head-Up Display (HUD) for showing FPS and game information."""

import pygame
from typing import Tuple, List


class HUDRenderer:
    """Renders FPS and debug information on screen."""
    def __init__(self, font: pygame.font.Font, position: Tuple[int, int] = (10, 10), color: Tuple[int, int, int] = (255, 255, 255)):
        self.font = font
        self.x, self.y = position
        self.color = color
        self.debugLogs: List[str] = []
        self.maxLines = 5

    def log(self, message: str) -> None:
        """Add a debug message."""
        self.debugLogs.append(message)
        if len(self.debugLogs) > self.maxLines:
            self.debugLogs.pop(0)

    def draw(self, surface: pygame.Surface, fps: float, bulletCount: int) -> None:
        """Draw FPS and bullet count."""
        fpsText = self.font.render(f"FPS: {fps:.1f}", True, self.color)
        bulletText = self.font.render(f"Bullets: {bulletCount}", True, self.color)

        surface.blit(fpsText, (self.x, self.y))
        surface.blit(bulletText, (self.x, self.y + 20))

        self.drawDebug(surface)

    def drawDebug(self, surface: pygame.Surface) -> None:
        """Draw debug messages."""
        for i, msg in enumerate(self.debugLogs):
            debugText = self.font.render(msg, True, self.color)
            surface.blit(debugText, (self.x, self.y + 50 + i * 20))
