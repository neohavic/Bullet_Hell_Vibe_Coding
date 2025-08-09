import pygame
import math

# ----------------------------
# Constants & Initialization
# ----------------------------
pygame.init()
WIDTH, HEIGHT = 1024, 768
SCREEN       = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK        = pygame.time.Clock()
FPS_TARGET   = 60

# Font for counters
FONT         = pygame.font.SysFont("Arial", 18)

CENTER       = (WIDTH // 2, HEIGHT // 2)

# Bullet settings
BULLET_RADIUS      = 4
BULLET_COLOR       = (255, 100, 255)
STRAIGHT_SPEED     = 4
ORBIT_EXPAND_SPEED = 2
BASE_ROT_SPEED     = math.radians(10) / FPS_TARGET  # 10° per second

# Sinusoidal movement settings
SINE_AMPLITUDE     = 6
SINE_FREQUENCY     = 0.15

# Screen-edge radius for full diagonal line
EDGE_RADIUS        = math.hypot(WIDTH, HEIGHT) / 2

# Emission settings
EMISSION_INTERVAL = 30  # frames between spawns
ORBIT_CYCLE_LIMIT = 5   # orbiting emissions before fly-out

# Precompute screen-corner radius for line emitter
EDGE_RADIUS = math.hypot(WIDTH/2, HEIGHT/2)

# ----------------------------
# Bullet Classes
# ----------------------------
class Bullet:
    def __init__(self, x, y, vx, vy):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        pygame.draw.circle(surface, BULLET_COLOR,
                           (int(self.x), int(self.y)), BULLET_RADIUS)


class OrbitingBullet(Bullet):
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
    def __init__(self, angle, speed, amplitude, frequency):
        vx = speed * math.cos(angle)
        vy = speed * math.sin(angle)
        super().__init__(*CENTER, vx, vy)
        self.perp_x = -math.sin(angle)
        self.perp_y = math.cos(angle)
        self.amplitude = amplitude
        self.frequency = frequency
        self.frame = 0

    def update(self):
        # radial movement
        self.x += self.vx
        self.y += self.vy
        # sine‐wave offset
        self.frame += 1
        offset = self.amplitude * math.sin(self.frame * self.frequency)
        self.x += self.perp_x * offset
        self.y += self.perp_y * offset


class RotatingLineBullet:
    def __init__(self, radius, angle, speed):
        self.radius = radius
        self.angle = angle
        self.speed = speed
        self.x = CENTER[0] + radius * math.cos(angle)
        self.y = CENTER[1] + radius * math.sin(angle)

    def update(self):
        self.angle += self.speed
        self.x = CENTER[0] + self.radius * math.cos(self.angle)
        self.y = CENTER[1] + self.radius * math.sin(self.angle)

    def draw(self, surface):
        pygame.draw.circle(surface, BULLET_COLOR,
                           (int(self.x), int(self.y)), BULLET_RADIUS)
        
class CurvedBullet:
    """
    Moves along a quadratic Bézier curve defined by p0→p1→p2.
    Disappears when t >= 1.
    """
    def __init__(self, p0, p1, p2, travel_frames):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.travel_frames = travel_frames
        self.frame = 0
        self.x, self.y = p0

    def update(self):
        # Advance t from 0 to 1 over travel_frames
        self.frame += 1
        t = min(self.frame / self.travel_frames, 1.0)
        inv = 1 - t

        # Quadratic Bézier formula
        self.x = inv*inv*self.p0[0] + 2*inv*t*self.p1[0] + t*t*self.p2[0]
        self.y = inv*inv*self.p0[1] + 2*inv*t*self.p1[1] + t*t*self.p2[1]

    def draw(self, surf):
        pygame.draw.circle(surf, BULLET_COLOR, (int(self.x), int(self.y)), BULLET_RADIUS)


# ----------------------------
# Emitter Base & Subclasses
# ----------------------------
class Emitter:
    def __init__(self):
        self.bullets = []
        self.spawn_timer = 0

    def update(self):
        # spawn on interval
        self.spawn_timer += 1
        if self.spawn_timer >= EMISSION_INTERVAL:
            self.spawn()
            self.spawn_timer = 0

        # update and cull
        new_bullets = []
        for b in self.bullets:
            b.update()
            if 0 <= b.x <= WIDTH and 0 <= b.y <= HEIGHT:
                new_bullets.append(b)
        self.bullets = new_bullets

    def draw(self, surface):
        for b in self.bullets:
            b.draw(surface)

    def spawn(self):
        raise NotImplementedError


class RadialEmitter(Emitter):
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
    def __init__(self, count=36, target_radius=100, cycle_limit=ORBIT_CYCLE_LIMIT):
        super().__init__()
        self.count = count
        self.target_radius = target_radius
        self.cycle_limit = cycle_limit
        self.emission_count = 0

    def spawn(self):
        for i in range(self.count):
            angle = 2 * math.pi * i / self.count
            self.bullets.append(OrbitingBullet(angle, self.target_radius))
        self.emission_count += 1
        if self.emission_count >= self.cycle_limit:
            for b in self.bullets:
                if isinstance(b, OrbitingBullet) and not b.flying_out:
                    b.fly_out()
            self.emission_count = 0


class SineEmitter(Emitter):
    def __init__(self, count=36, amplitude=SINE_AMPLITUDE, frequency=SINE_FREQUENCY):
        super().__init__()
        self.count = count
        self.amplitude = amplitude
        self.frequency = frequency

    def spawn(self):
        for i in range(self.count):
            angle = 2 * math.pi * i / self.count
            self.bullets.append(SinusoidalBullet(angle,
                                                 STRAIGHT_SPEED,
                                                 self.amplitude,
                                                 self.frequency))


class RotatingLineEmitter(Emitter):
    """
    Emits 2×count bullets along a diameter that rotates through
    the screen’s diagonal. Clears old bullets each spawn so
    the count stays constant.
    """
    def __init__(self, count=36, radius=EDGE_RADIUS, speed_mul=3):
        super().__init__()
        self.count      = count * 2
        self.radius     = radius
        self.speed      = BASE_ROT_SPEED * speed_mul
        self.line_angle = 0

    def update(self):
        # spin the line each frame
        self.line_angle += self.speed
        super().update()

    def spawn(self):
        # remove last frame's bullets before emitting new ones
        self.bullets.clear()
        for i in range(self.count):
            t = -1 + (2 * i) / (self.count - 1)
            r = abs(t) * self.radius
            angle = self.line_angle + (0 if t >= 0 else math.pi)
            self.bullets.append(RotatingLineBullet(r, angle, self.speed))
            
class CurveEmitter(Emitter):
    """
    Emits `count` bullets along Bézier curves fanning out from CENTER.
    Each bullet arcs via a control point offset by ctrl_angle_offset.
    """
    def __init__(self, count=24, radius=300, travel_frames=60, ctrl_angle_offset=math.pi/4):
        super().__init__()
        self.count = count
        self.radius = radius
        self.travel_frames = travel_frames
        self.ctrl_offset = ctrl_angle_offset

    def spawn(self):
        for i in range(self.count):
            # evenly spaced final-angle
            angle = 2 * math.pi * i / self.count

            # p0 = center
            p0 = CENTER

            # p2 = point on circle at `angle`
            p2 = (CENTER[0] + self.radius * math.cos(angle),
                  CENTER[1] + self.radius * math.sin(angle))

            # p1 = midpoint bent by ctrl_offset
            mid_radius = self.radius * 0.5
            ctrl_angle = angle + self.ctrl_offset
            p1 = (CENTER[0] + mid_radius * math.cos(ctrl_angle),
                  CENTER[1] + mid_radius * math.sin(ctrl_angle))

            self.bullets.append(CurvedBullet(p0, p1, p2, self.travel_frames))


# ----------------------------
# Emitter Manager
# ----------------------------
class EmitterManager:
    def __init__(self):
        self.emitters = {}
        self.active = {}

    def add(self, name, emitter, initially_active=False):
        self.emitters[name] = emitter
        self.active[name] = initially_active

    def set_active(self, name):
        for n in self.active:
            self.active[n] = (n == name)

    def update(self):
        for name, e in self.emitters.items():
            if self.active[name]:
                e.update()

    def draw(self, surface):
        for name, e in self.emitters.items():
            if self.active[name]:
                e.draw(surface)
                
    def toggle(self, name):
        if name in self.active:
            self.active[name] = not self.active[name]

# ----------------------------
# Rotation Class
# ----------------------------

class Rotation3D:
    """
    Manages 3D rotation state (angles + angular velocity) and applies
    a combined rotation matrix Rz * Ry * Rx to points.
    Angles and rates are in radians and radians/second, respectively.
    """
    def __init__(self, angles=(0.0, 0.0, 0.0), rates=(0.0, 0.0, 0.0)):
        self.ax, self.ay, self.az = angles
        self.vx, self.vy, self.vz = rates
        self._M = None  # combined rotation matrix cache

    # ----- Configuration -----
    def set_rates(self, rates):
        self.vx, self.vy, self.vz = rates

    def set_angles(self, angles):
        self.ax, self.ay, self.az = angles
        self._recompute_matrix()

    # ----- Update per frame -----
    def update(self, dt):
        # Update angles with wrap to keep values bounded
        self.ax = (self.ax + self.vx * dt) % (2 * math.pi)
        self.ay = (self.ay + self.vy * dt) % (2 * math.pi)
        self.az = (self.az + self.vz * dt) % (2 * math.pi)
        self._recompute_matrix()

    # ----- Apply rotation -----
    def rotate_point(self, p):
        """Rotate a single (x, y, z) tuple using the cached matrix."""
        if self._M is None:
            self._recompute_matrix()
        x, y, z = p
        m = self._M
        return (
            m[0][0]*x + m[0][1]*y + m[0][2]*z,
            m[1][0]*x + m[1][1]*y + m[1][2]*z,
            m[2][0]*x + m[2][1]*y + m[2][2]*z
        )

    def rotate_points(self, points):
        """Rotate an iterable of (x, y, z) points."""
        if self._M is None:
            self._recompute_matrix()
        m = self._M
        out = []
        for x, y, z in points:
            out.append((
                m[0][0]*x + m[0][1]*y + m[0][2]*z,
                m[1][0]*x + m[1][1]*y + m[1][2]*z,
                m[2][0]*x + m[2][1]*y + m[2][2]*z
            ))
        return out

    # ----- Internals -----
    def _recompute_matrix(self):
        cx, sx = math.cos(self.ax), math.sin(self.ax)
        cy, sy = math.cos(self.ay), math.sin(self.ay)
        cz, sz = math.cos(self.az), math.sin(self.az)

        # Rx
        Rx = (
            (1, 0,   0),
            (0, cx, -sx),
            (0, sx,  cx),
        )
        # Ry
        Ry = (
            (cy, 0, sy),
            (0,  1, 0),
            (-sy,0, cy),
        )
        # Rz
        Rz = (
            (cz, -sz, 0),
            (sz,  cz, 0),
            (0,    0, 1),
        )

        # M = Rz * Ry * Rx
        def matmul(A, B):
            return tuple(
                tuple(sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3))
                for i in range(3)
            )
        self._M = matmul(Rz, matmul(Ry, Rx))
        
def project_perspective(point, center, fov=400.0, z_offset=200.0):
    x, y, z = point
    z += z_offset
    f = fov / max(1e-6, z)
    return int(center[0] + x * f), int(center[1] + y * f)

# ----------------------------
# Main Game Loop
# ----------------------------
def main():
    manager = EmitterManager()
    manager.add("straight", RadialEmitter(),   initially_active=True)
    manager.add("orbiting", OrbitingEmitter(), initially_active=False)
    manager.add("sine",     SineEmitter(),     initially_active=False)
    manager.add("line",     RotatingLineEmitter(), initially_active=False)
    manager.add("curve", CurveEmitter(count=12, radius=800, travel_frames=90), initially_active=False)
    
    # Half-size 50 -> 100px wide cube
    CUBE_SIZE = 17
    cube_vertices = [
        [x, y, z]
        for x in (-CUBE_SIZE, CUBE_SIZE)
        for y in (-CUBE_SIZE, CUBE_SIZE)
        for z in (-CUBE_SIZE, CUBE_SIZE)
    ]
    cube_edges = [
        (0,1), (0,2), (0,4), (1,3), (1,5), (2,3),
        (2,6), (3,7), (4,5), (4,6), (5,7), (6,7)
    ]

    rot = Rotation3D(
        angles=(0.0, 0.0, 0.0),
        rates=(1.2, 0.9, 0.6)  # rad/s
    )

    running = True
    while running:
        CLOCK.tick(FPS_TARGET)
        SCREEN.fill((0, 0, 0))
        
        
        # Inside your loop, before computing cube vertices
        pulse_base = 27.0     # Half of 34 pixels
        pulse_amplitude = 2.0 # Grows ±2 pixels
        pulse_speed = 15.0     # Radians per second

        # Compute pulsing cube size
        t = pygame.time.get_ticks() / 1000.0  # seconds
        dynamic_size = pulse_base + pulse_amplitude * math.sin(t * pulse_speed)

        # Recompute cube vertices on each frame
        cube_vertices = [
            [x, y, z]
            for x in (-dynamic_size, dynamic_size)
            for y in (-dynamic_size, dynamic_size)
            for z in (-dynamic_size, dynamic_size)
        ]
        
        
        dt = CLOCK.get_time() / 1000.0  # seconds since last frame
        rot.update(dt)

        rotated = rot.rotate_points(cube_vertices)
        projected = [project_perspective(p, CENTER, fov=400, z_offset=200) for p in rotated]

        for i, j in cube_edges:
            pygame.draw.aaline(SCREEN, (100, 255, 200), projected[i], projected[j])
        
        # --- Draw grid overlay (100px spacing)
        grid_color = (40, 40, 40)
        spacing = 100
        for x in range(0, WIDTH, spacing):
            pygame.draw.line(SCREEN, grid_color, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, spacing):
            pygame.draw.line(SCREEN, grid_color, (0, y), (WIDTH, y))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                 running = False
            elif event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_1:
                     manager.toggle("straight")
                 elif event.key == pygame.K_2:
                     manager.toggle("orbiting")
                 elif event.key == pygame.K_3:
                     manager.toggle("sine")
                 elif event.key == pygame.K_4:
                     manager.toggle("line")
                 elif event.key == pygame.K_5:
                     manager.toggle("curve")

        # Update & draw
        manager.update()
        manager.draw(SCREEN)

        # Render FPS
        fps_text = FONT.render(f"FPS: {CLOCK.get_fps():.1f}", True, (255, 255, 255))
        SCREEN.blit(fps_text, (10, 10))

        # Render accurate bullet count
        bullet_count = sum(
            len(manager.emitters[name].bullets)
            for name, active in manager.active.items()
            if active
        )
        bullet_text = FONT.render(f"Bullets: {bullet_count}", True, (255, 255, 255))
        SCREEN.blit(bullet_text, (10, 30))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()