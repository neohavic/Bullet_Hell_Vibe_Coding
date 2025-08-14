import settings
import pygame
import math

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
        self.sword_angle = 0
        self.swinging = False


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
            self.shoot((CENTER))
            self.cooldown_timer = self.bullet_cooldown
        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            if not self.swinging:
                self.swinging = True
                self.sword_angle = 0

        if self.swinging:
            self.sword_angle += 6  # degrees per frame
        if self.sword_angle >= 360:
            self.sword_angle = 0
            self.swinging = False
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
        time = pygame.time.get_ticks() * 0.002
        cx, cy = self.x, self.y
        ring_radius = 40
        ring_thickness = 2
        segments = 32  # More segments = smoother ring

        # Z-axis ring (flat circle)
        for i in range(segments):
            angle = time + i * (2 * math.pi / segments)
            x = cx + math.cos(angle) * ring_radius
            y = cy + math.sin(angle) * ring_radius
            pygame.draw.circle(screen, self.color, (int(x), int(y)), ring_thickness)

        # X-axis ring (vertical ellipse)
        for i in range(segments):
            angle = time + i * (2 * math.pi / segments)
            x = cx + math.cos(angle) * ring_radius
            y = cy + math.sin(angle) * ring_radius * math.cos(time)
            pygame.draw.circle(screen, self.color, (int(x), int(y)), ring_thickness)

        # Y-axis ring (horizontal ellipse)
        for i in range(segments):
            angle = time + i * (2 * math.pi / segments)
            x = cx + math.cos(angle) * ring_radius * math.cos(time)
            y = cy + math.sin(angle) * ring_radius
            pygame.draw.circle(screen, self.color, (int(x), int(y)), ring_thickness)

        # Beam to CENTER
        pygame.draw.line(screen, (105, 7, 7), (cx, cy), CENTER, 2)

        # Bullets
        for bullet in self.bullets:
            pygame.draw.circle(screen, self.bullet_color, (int(bullet['x']), int(bullet['y'])), bullet['radius'])

        if self.swinging:
            angle_rad = math.radians(self.sword_angle)
            cx, cy = self.x, self.y
            length = 90
            offset = math.radians(20)

            # Two angled points from center
            a1 = angle_rad + offset
            a2 = angle_rad - offset
            p1 = (cx + math.cos(a1) * length, cy + math.sin(a1) * length)
            p2 = (cx + math.cos(a2) * length, cy + math.sin(a2) * length)

            # Tip of the sword (forward direction)
            tip_length = length * 2
            tip = (cx + math.cos(angle_rad) * tip_length, cy + math.sin(angle_rad) * tip_length)

            # Draw four lines
            pygame.draw.line(screen, (255, 0, 0), (cx, cy), p1, 2)
            pygame.draw.line(screen, (255, 0, 0), (cx, cy), p2, 2)
            pygame.draw.line(screen, (255, 0, 0), p1, tip, 2)
            pygame.draw.line(screen, (255, 0, 0), p2, tip, 2)
