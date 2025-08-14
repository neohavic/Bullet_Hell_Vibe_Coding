import settings
import pygame
import math
from hud import *

CENTER = (settings.WIDTH // 2, settings.HEIGHT // 2)

class Player:
    def __init__(self, x, y, radius=20, speed=5):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.color = (0, 255, 0)
        self.bullet_color = (255, 255, 0)
        self.bullets = []
        self.bullet_cooldown = 10
        self.cooldown_timer = 0

    def handle_input(self, keys):
        dx = dy = 0
        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1

        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length
            self.x += dx * self.speed
            self.y += dy * self.speed

    def update(self, keys):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
        if keys[pygame.K_SPACE] and self.cooldown_timer == 0:
            center_x = int(settings.WIDTH / 2)
            center_y = int(settings.HEIGHT / 2)
            self.shoot((center_x, center_y))
            self.cooldown_timer = self.bullet_cooldown
        for bullet in self.bullets:
            bullet['x'] += bullet['dx'] * bullet['speed']
            bullet['y'] += bullet['dy'] * bullet['speed']
        self.bullets = [b for b in self.bullets if 0 <= b['x'] <= settings.WIDTH and 0 <= b['y'] <= settings.HEIGHT]

    def shoot(self, target_pos):
        dx = target_pos[0] - self.x
        dy = target_pos[1] - self.y
        length = math.hypot(dx, dy)
        if length < 1e-5:
            return  # Avoid near-zero vectors
        dx /= length
        dy /= length
        spawn_x = self.x + dx * (self.radius + 1)
        spawn_y = self.y + dy * (self.radius + 1)
        bullet = {
            'x': spawn_x,
            'y': spawn_y,
            'dx': dx,
            'dy': dy,
            'speed': 10,
            'radius': 5
         }
        self.bullets.append(bullet)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # Very dark grey beam to CENTER
        center_x = int(settings.WIDTH / 2)
        center_y = int(settings.HEIGHT / 2)
        pygame.draw.line(screen, (105, 7, 7), (self.x, self.y), (center_x, center_y), 2)
        for bullet in self.bullets:
            pygame.draw.circle(screen, self.bullet_color, (int(bullet['x']), int(bullet['y'])), bullet['radius'])