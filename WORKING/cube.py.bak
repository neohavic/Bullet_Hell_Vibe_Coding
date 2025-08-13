import pygame
import math
from typing import Tuple, List
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

class CubeRenderer:
    def __init__(self, center: Tuple[int, int], base_size: float = 27.0, amplitude: float = 2.0, pulse_speed: float = 15.0):
        self.center = center
        self.base_size = base_size
        self.amplitude = amplitude
        self.pulse_speed = pulse_speed
        self.edges = [
            (0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3),
            (2, 6), (3, 7), (4, 5), (4, 6), (5, 7), (6, 7)
        ]
        self.rotation = Rotation3D(
            angles=(0.0, 0.0, 0.0),
            rates=(1.2, 0.9, 0.6)
        )

    def get_vertices(self) -> List[List[float]]:
        t = pygame.time.get_ticks() / 1000.0
        size = self.base_size + self.amplitude * math.sin(t * self.pulse_speed)
        return [
            [x, y, z]
            for x in (-size, size)
            for y in (-size, size)
            for z in (-size, size)
        ]

    def update(self, dt: float) -> None:
        self.rotation.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        vertices = self.get_vertices()
        rotated = self.rotation.rotate_points(vertices)
        projected = [
            project_perspective(p, self.center, fov=400, z_offset=200)
            for p in rotated
        ]
        for i, j in self.edges:
            pygame.draw.aaline(surface, (100, 255, 200), projected[i], projected[j])