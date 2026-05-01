"""Player character with movement and shooting mechanics."""

import settings
import pygame
import math

center = (settings.WIDTH // 2, settings.HEIGHT // 2)


class Player:
    """Player character with beam and sword attacks."""
    def __init__(self, x, y, radius=20, speed=5):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.color = (0, 255, 0)
        self.bulletColor = (255, 255, 0)
        self.bullets = []
        self.bulletCooldown = 10
        self.cooldownTimer = 0
        self.swordAngle = 0
        self.swinging = False

    def handleInput(self, keys):
        """Handle keyboard input for movement."""
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
        """Update player state (shooting, sword swing)."""
        if self.cooldownTimer > 0:
            self.cooldownTimer -= 1
        if keys[pygame.K_SPACE] and self.cooldownTimer == 0:
            self.shoot(center)
            self.cooldownTimer = self.bulletCooldown
        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            if not self.swinging:
                self.swinging = True
                self.swordAngle = 0

        if self.swinging:
            self.swordAngle += 6
        if self.swordAngle >= 360:
            self.swordAngle = 0
            self.swinging = False
        
        # Update bullets
        for bullet in self.bullets:
            bullet['x'] += bullet['dx'] * bullet['speed']
            bullet['y'] += bullet['dy'] * bullet['speed']
        self.bullets = [b for b in self.bullets if 0 <= b['x'] <= settings.WIDTH and 0 <= b['y'] <= settings.HEIGHT]

    def shoot(self, targetPos):
        """Shoot a bullet towards target."""
        dx = targetPos[0] - self.x
        dy = targetPos[1] - self.y
        length = math.hypot(dx, dy)
        if length < 1e-5:
            return
        dx /= length
        dy /= length
        spawnX = self.x + dx * (self.radius + 1)
        spawnY = self.y + dy * (self.radius + 1)
        bullet = {
            'x': spawnX,
            'y': spawnY,
            'dx': dx,
            'dy': dy,
            'speed': 10,
            'radius': 5
        }
        self.bullets.append(bullet)

    def draw(self, screen):
        """Draw player with rings and sword."""
        time = pygame.time.get_ticks() * 0.002
        cx, cy = self.x, self.y
        ringRadius = 40
        ringThickness = 2
        segments = 32

        # Draw three rotating rings
        for ring_type in range(3):
            for i in range(segments):
                angle = time + i * (2 * math.pi / segments)
                if ring_type == 0:  # Z-axis ring
                    x = cx + math.cos(angle) * ringRadius
                    y = cy + math.sin(angle) * ringRadius
                elif ring_type == 1:  # X-axis ring
                    x = cx + math.cos(angle) * ringRadius
                    y = cy + math.sin(angle) * ringRadius * math.cos(time)
                else:  # Y-axis ring
                    x = cx + math.cos(angle) * ringRadius * math.cos(time)
                    y = cy + math.sin(angle) * ringRadius
                pygame.draw.circle(screen, self.color, (int(x), int(y)), ringThickness)

        # Draw beam to center
        pygame.draw.line(screen, (105, 7, 7), (cx, cy), center, 2)

        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.circle(screen, self.bulletColor, (int(bullet['x']), int(bullet['y'])), bullet['radius'])

        # Draw sword if swinging
        if self.swinging:
            angleRad = math.radians(self.swordAngle)
            length = 90
            offset = math.radians(20)

            a1 = angleRad + offset
            a2 = angleRad - offset
            p1 = (cx + math.cos(a1) * length, cy + math.sin(a1) * length)
            p2 = (cx + math.cos(a2) * length, cy + math.sin(a2) * length)

            tipLength = length * 2
            tip = (cx + math.cos(angleRad) * tipLength, cy + math.sin(angleRad) * tipLength)

            pygame.draw.line(screen, (255, 0, 0), (cx, cy), p1, 2)
            pygame.draw.line(screen, (255, 0, 0), (cx, cy), p2, 2)
            pygame.draw.line(screen, (255, 0, 0), p1, tip, 2)
            pygame.draw.line(screen, (255, 0, 0), p2, tip, 2)
