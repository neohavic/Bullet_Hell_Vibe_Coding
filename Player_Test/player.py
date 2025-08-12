# player.py
import pygame
import math

class Player:
    def __init__(self, x, y, radius=20, speed=5):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.color = (0, 255, 0)
        self.bullet_color = (255, 255, 0)
        self.bullets = []
        self.tick_counter = 0
        self.bullet_rate = 10  # fire every 10 ticks

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

    def update(self, enemy_pos):
        self.tick_counter += 1
        if self.tick_counter % self.bullet_rate == 0:
            self.shoot(enemy_pos)

        # Update bullets
        for bullet in self.bullets:
            bullet['x'] += bullet['dx'] * bullet['speed']
            bullet['y'] += bullet['dy'] * bullet['speed']

        # Remove off-screen bullets
        self.bullets = [b for b in self.bullets if 0 <= b['x'] <= 900 and 0 <= b['y'] <= 900]

    def shoot(self, target_pos):
        dx = target_pos[0] - self.x
        dy = target_pos[1] - self.y
        length = math.hypot(dx, dy)
        dx /= length
        dy /= length
        bullet = {
            'x': self.x,
            'y': self.y,
            'dx': dx,
            'dy': dy,
            'speed': 10,
            'radius': 5
        }
        self.bullets.append(bullet)

    def draw(self, screen, enemy_pos):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

        # Draw beam
        pygame.draw.line(screen, (0, 255, 255), (self.x, self.y), enemy_pos, 2)

        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.circle(screen, self.bullet_color, (int(bullet['x']), int(bullet['y'])), bullet['radius'])