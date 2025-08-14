import math
import pygame
import settings

# ----------------------------
# Constants
# ----------------------------

CENTER           = (settings.WIDTH // 2, settings.HEIGHT // 2)
BULLET_RADIUS    = 4
BULLET_COLOR     = (255, 100, 255)
STRAIGHT_SPEED   = 5
BASE_ROT_SPEED   = 0.03
ORBIT_EXPAND_SPEED = 2
ORBIT_CYCLE_LIMIT  = 3
SINE_AMPLITUDE   = 10
SINE_FREQUENCY   = 0.2
EDGE_RADIUS      = max(settings.WIDTH, settings.HEIGHT) // 2
EMISSION_INTERVAL = 30  # frames between spawns

# ----------------------------
# Bullet Classes
# ----------------------------

class Bullet:
    """Basic straight‐moving bullet."""
    def __init__(self, x, y, vx, vy):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        pygame.draw.circle(surface, BULLET_COLOR, (int(self.x), int(self.y)), BULLET_RADIUS)

class OrbitingBullet(Bullet):
    """Expands out on orb, then spins. fly_out() sends it straight."""
    def __init__(self, angle, target_radius):
        super().__init__(*CENTER, 0, 0)
        self.angle = angle
        self.radius = 0
        self.target_radius = target_radius
        self.flying_out = False

    def update(self):
        if not self.flying_out:
            if self.radius < self.target_radius:
                self.radius += ORBIT_EXPAND_SPEED
            else:
                self.angle += BASE_ROT_SPEED
            self.x = CENTER[0] + self.radius * math.cos(self.angle)
            self.y = CENTER[1] + self.radius * math.sin(self.angle)
        else:
            super().update()

    def fly_out(self):
        if not self.flying_out:
            self.flying_out = True
            self.vx = STRAIGHT_SPEED * math.cos(self.angle)
            self.vy = STRAIGHT_SPEED * math.sin(self.angle)

class SinusoidalBullet(Bullet):
    """Straight motion plus sine‐wave lateral wiggle."""
    def __init__(self, angle, speed, amplitude, frequency):
        vx = speed * math.cos(angle)
        vy = speed * math.sin(angle)
        super().__init__(*CENTER, vx, vy)
        # perpendicular unit vector for lateral offset
        self.perp_x = -math.sin(angle)
        self.perp_y = math.cos(angle)
        self.amplitude = amplitude
        self.frequency = frequency
        self.frame = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.frame += 1
        offset = self.amplitude * math.sin(self.frame * self.frequency)
        self.x += self.perp_x * offset
        self.y += self.perp_y * offset

class RotatingLineBullet:
    def __init__(self, radius, angle, speed):
        self.radius = radius
        self.angle = angle
        self.speed = speed
        self._recalc()

    def _recalc(self):
        self.x = CENTER[0] + self.radius * math.cos(self.angle)
        self.y = CENTER[1] + self.radius * math.sin(self.angle)

    def update(self):
        self.angle += self.speed
        self._recalc()

    def draw(self, surface):
        pygame.draw.circle(surface, BULLET_COLOR, (int(self.x), int(self.y)), BULLET_RADIUS)

class CurvedBullet:
    """Quadratic Bézier arc from p0 → p1 → p2, disappears at t=1."""
    def __init__(self, p0, p1, p2, travel_frames):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.travel_frames = travel_frames
        self.frame = 0
        self.x, self.y = p0
        self.vx = 0
        self.vy = 0
        self.flying_out = False

    def update(self):
        self.frame += 1
        t = min(self.frame / self.travel_frames, 1.0)
        if t < 1.0:
            inv = 1 - t
            self.x = inv*inv * self.p0[0] + 2*inv*t * self.p1[0] + t*t * self.p2[0]
            self.y = inv*inv * self.p0[1] + 2*inv*t * self.p1[1] + t*t * self.p2[1]
        else:
            if not self.flying_out:
                dx = self.p2[0] - self.p1[0]
                dy = self.p2[1] - self.p1[1]
                ang = math.atan2(dy, dx)
                self.vx = STRAIGHT_SPEED * math.cos(ang)
                self.vy = STRAIGHT_SPEED * math.sin(ang)
                self.flying_out = True
            self.x += self.vx
            self.y += self.vy

    def draw(self, surface):
        pygame.draw.circle(surface, BULLET_COLOR, (int(self.x), int(self.y)), BULLET_RADIUS)

# ----------------------------
# Emitter Base & Subclasses
# ----------------------------
class Emitter:
    """
    Base emitter handles interval spawning, bullet updates, and bounds culling.
    Subclasses implement spawn().
    """
    def __init__(self):
        self.bullets = []
        self._timer = 0

    def update(self):
        self._timer += 1
        if self._timer >= EMISSION_INTERVAL:
            self.spawn()
            self._timer = 0
        alive = []
        for b in self.bullets:
             b.update()
             if 0 <= b.x <= settings.WIDTH and 0 <= b.y <= settings.HEIGHT:
                 alive.append(b)
        self.bullets = alive

    def draw(self, surface):
        for b in self.bullets:
            b.draw(surface)

    def spawn(self):
        raise NotImplementedError("Emitters must implement spawn()")

class RadialEmitter(Emitter):
    """Spawns `count` bullets in a uniform circle."""
    def __init__(self, count=36):
        super().__init__()
        self.count = count

    def spawn(self):
        for i in range(self.count):
            angle = 2 * math.pi * i / self.count
            vx = STRAIGHT_SPEED * math.cos(angle)
            vy = STRAIGHT_SPEED * math.sin(angle)
            self.bullets.append(Bullet(*CENTER, vx, vy))

class OrbitingEmitter(Emitter):
    """
    Emits orbiting bullets in `count` spokes.
    After `cycle_limit` emissions, all orbiters fly out.
    """
    def __init__(self, count=36, target_radius=100, cycle_limit=ORBIT_CYCLE_LIMIT):
        super().__init__()
        self.count = count
        self.target_radius = target_radius
        self.cycle_limit = cycle_limit
        self._emissions = 0

    def spawn(self):
        for i in range(self.count):
            angle = 2 * math.pi * i / self.count
            self.bullets.append(OrbitingBullet(angle, self.target_radius))
        self._emissions += 1
        if self._emissions >= self.cycle_limit:
            for b in self.bullets:
                if isinstance(b, OrbitingBullet) and not b.flying_out:
                    b.fly_out()
            self._emissions = 0


class SineEmitter(Emitter):
    """Spawns bullets that wiggle sinusoidally."""
    def __init__(self, count=36, amplitude=SINE_AMPLITUDE, frequency=SINE_FREQUENCY):
        super().__init__()
        self.count = count
        self.amplitude = amplitude
        self.frequency = frequency

    def spawn(self):
        for i in range(self.count):
            angle = 2 * math.pi * i / self.count
            self.bullets.append(SinusoidalBullet(angle, STRAIGHT_SPEED, self.amplitude, self.frequency))

class RotatingLineEmitter(Emitter):
    def __init__(self, count=36, radius=EDGE_RADIUS, speed_mul=3):
        super().__init__()
        self.count = count * 2
        self.radius = radius
        self.speed = BASE_ROT_SPEED * speed_mul
        self.line_angle = 0

    def update(self):
        self.line_angle += self.speed
        super().update()

    def spawn(self):
        self.bullets.clear()
        for i in range(self.count):
            # t from -1→1; absolute determines distance along line
            t = -1 + (2 * i) / (self.count - 1)
            r = abs(t) * self.radius
            angle = self.line_angle + (0 if t >= 0 else math.pi)
            self.bullets.append(RotatingLineBullet(r, angle, self.speed))

class CurveEmitter(Emitter):
    """
    Emits bullets along quadratic Bézier curves fanning out.
    Control point bent by ctrl_angle_offset.
    """
    def __init__(self, count=24, radius=EDGE_RADIUS, travel_frames=60, ctrl_angle_offset=math.pi / 4):
        super().__init__()
        self.count = count
        self.radius = radius
        self.travel_frames = travel_frames
        self.ctrl_offset = ctrl_angle_offset

    def spawn(self):
        for i in range(self.count):
            angle = 2 * math.pi * i / self.count
            p0 = CENTER
            p2 = (CENTER[0] + self.radius * math.cos(angle), CENTER[1] + self.radius * math.sin(angle))
            mid_radius = self.radius * 0.5
            ctrl = angle + self.ctrl_offset
            p1 = (CENTER[0] + mid_radius * math.cos(ctrl), CENTER[1] + mid_radius * math.sin(ctrl))
            self.bullets.append(CurvedBullet(p0, p1, p2, self.travel_frames))