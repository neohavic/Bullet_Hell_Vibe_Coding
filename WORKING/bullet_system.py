import math
import pygame
import settings

# ----------------------------
# Constants
# ----------------------------

center           = (settings.WIDTH // 2, settings.HEIGHT // 2)
bulletRadius    = 4
bulletColor     = (255, 100, 255)
straightSpeed   = 5
baseRotSpeed   = 0.03
orbitExpandSpeed = 2
orbitCycleLimit  = 3
sineAmplitude   = 10
sineFrequency   = 0.2
edgeRadius      = max(settings.WIDTH, settings.HEIGHT) // 2
emissionInterval = 30  # frames between spawns

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
        pygame.draw.circle(surface, bulletColor, (int(self.x), int(self.y)), bulletRadius)

class OrbitingBullet(Bullet):
    """Expands out on orb, then spins. fly_out() sends it straight."""
    def __init__(self, angle, targetRadius):
        super().__init__(*center, 0, 0)
        self.angle = angle
        self.radius = 0
        self.targetRadius = targetRadius
        self.flyingOut = False

    def update(self):
        if not self.flyingOut:
            if self.radius < self.targetRadius:
                self.radius += orbitExpandSpeed
            else:
                self.angle += baseRotSpeed
            self.x = center[0] + self.radius * math.cos(self.angle)
            self.y = center[1] + self.radius * math.sin(self.angle)
        else:
            super().update()

    def flyOut(self):
        if not self.flyingOut:
            self.flyingOut = True
            self.vx = straightSpeed * math.cos(self.angle)
            self.vy = straightSpeed * math.sin(self.angle)

class SinusoidalBullet(Bullet):
    """Straight motion plus sine‐wave lateral wiggle."""
    def __init__(self, angle, speed, amplitude, frequency):
        vx = speed * math.cos(angle)
        vy = speed * math.sin(angle)
        super().__init__(*center, vx, vy)
        # perpendicular unit vector for lateral offset
        self.perpX = -math.sin(angle)
        self.perpY = math.cos(angle)
        self.amplitude = amplitude
        self.frequency = frequency
        self.frame = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.frame += 1
        offset = self.amplitude * math.sin(self.frame * self.frequency)
        self.x += self.perpX * offset
        self.y += self.perpY * offset

class RotatingLineBullet:
    def __init__(self, radius, angle, speed):
        self.radius = radius
        self.angle = angle
        self.speed = speed
        self._recalc()

    def _recalc(self):
        self.x = center[0] + self.radius * math.cos(self.angle)
        self.y = center[1] + self.radius * math.sin(self.angle)

    def update(self):
        self.angle += self.speed
        self._recalc()

    def draw(self, surface):
        pygame.draw.circle(surface, bulletColor, (int(self.x), int(self.y)), bulletRadius)

class CurvedBullet:
    """Quadratic Bézier arc from p0 → p1 → p2, disappears at t=1."""
    def __init__(self, p0, p1, p2, travelFrames):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.travelFrames = travelFrames
        self.frame = 0
        self.x, self.y = p0
        self.vx = 0
        self.vy = 0
        self.flyingOut = False

    def update(self):
        self.frame += 1
        t = min(self.frame / self.travelFrames, 1.0)
        if t < 1.0:
            inv = 1 - t
            self.x = inv*inv * self.p0[0] + 2*inv*t * self.p1[0] + t*t * self.p2[0]
            self.y = inv*inv * self.p0[1] + 2*inv*t * self.p1[1] + t*t * self.p2[1]
        else:
            if not self.flyingOut:
                dx = self.p2[0] - self.p1[0]
                dy = self.p2[1] - self.p1[1]
                ang = math.atan2(dy, dx)
                self.vx = straightSpeed * math.cos(ang)
                self.vy = straightSpeed * math.sin(ang)
                self.flyingOut = True
            self.x += self.vx
            self.y += self.vy

    def draw(self, surface):
        pygame.draw.circle(surface, bulletColor, (int(self.x), int(self.y)), bulletRadius)

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
        if self._timer >= emissionInterval:
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
            vx = straightSpeed * math.cos(angle)
            vy = straightSpeed * math.sin(angle)
            self.bullets.append(Bullet(*center, vx, vy))

class OrbitingEmitter(Emitter):
    """
    Emits orbiting bullets in `count` spokes.
    After `cycleLimit` emissions, all orbiters fly out.
    """
    def __init__(self, count=36, targetRadius=100, cycleLimit=orbitCycleLimit):
        super().__init__()
        self.count = count
        self.targetRadius = targetRadius
        self.cycleLimit = cycleLimit
        self._emissions = 0

    def spawn(self):
        for i in range(self.count):
            angle = 2 * math.pi * i / self.count
            self.bullets.append(OrbitingBullet(angle, self.targetRadius))
        self._emissions += 1
        if self._emissions >= self.cycleLimit:
            for b in self.bullets:
                if isinstance(b, OrbitingBullet) and not b.flyingOut:
                    b.flyOut()
            self._emissions = 0


class SineEmitter(Emitter):
    """Spawns bullets that wiggle sinusoidally."""
    def __init__(self, count=36, amplitude=sineAmplitude, frequency=sineFrequency):
        super().__init__()
        self.count = count
        self.amplitude = amplitude
        self.frequency = frequency

    def spawn(self):
        for i in range(self.count):
            angle = 2 * math.pi * i / self.count
            self.bullets.append(SinusoidalBullet(angle, straightSpeed, self.amplitude, self.frequency))

class RotatingLineEmitter(Emitter):
    def __init__(self, count=36, radius=edgeRadius, speedMul=3):
        super().__init__()
        self.count = count * 2
        self.radius = radius
        self.speed = baseRotSpeed * speedMul
        self.lineAngle = 0

    def update(self):
        self.lineAngle += self.speed
        super().update()

    def spawn(self):
        self.bullets.clear()
        for i in range(self.count):
            # t from -1→1; absolute determines distance along line
            t = -1 + (2 * i) / (self.count - 1)
            r = abs(t) * self.radius
            angle = self.lineAngle + (0 if t >= 0 else math.pi)
            self.bullets.append(RotatingLineBullet(r, angle, self.speed))

class CurveEmitter(Emitter):
    """
    Emits bullets along quadratic Bézier curves fanning out.
    Control point bent by ctrlAngleOffset.
    """
    def __init__(self, count=24, radius=edgeRadius, travelFrames=60, ctrlAngleOffset=math.pi / 4):
        super().__init__()
        self.count = count
        self.radius = radius
        self.travelFrames = travelFrames
        self.ctrlOffset = ctrlAngleOffset

    def spawn(self):
        for i in range(self.count):
            angle = 2 * math.pi * i / self.count
            p0 = center
            p2 = (center[0] + self.radius * math.cos(angle), center[1] + self.radius * math.sin(angle))
            midRadius = self.radius * 0.5
            ctrl = angle + self.ctrlOffset
            p1 = (center[0] + midRadius * math.cos(ctrl), center[1] + midRadius * math.sin(ctrl))
            self.bullets.append(CurvedBullet(p0, p1, p2, self.travelFrames))
