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
    def setRates(self, rates):
        self.vx, self.vy, self.vz = rates

    def setAngles(self, angles):
        self.ax, self.ay, self.az = angles
        self._recomputeMatrix()

    # ----- Update per frame -----
    def update(self, dt):
        # Update angles with wrap to keep values bounded
        self.ax = (self.ax + self.vx * dt) % (2 * math.pi)
        self.ay = (self.ay + self.vy * dt) % (2 * math.pi)
        self.az = (self.az + self.vz * dt) % (2 * math.pi)
        self._recomputeMatrix()

    # ----- Apply rotation -----
    def rotatePoint(self, p):
        """Rotate a single (x, y, z) tuple using the cached matrix."""
        if self._M is None:
            self._recomputeMatrix()
        x, y, z = p
        m = self._M
        return (
            m[0][0]*x + m[0][1]*y + m[0][2]*z,
            m[1][0]*x + m[1][1]*y + m[1][2]*z,
            m[2][0]*x + m[2][1]*y + m[2][2]*z
        )

    def rotatePoints(self, points):
        """Rotate an iterable of (x, y, z) points."""
        if self._M is None:
            self._recomputeMatrix()
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
    def _recomputeMatrix(self):
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
        
def projectPerspective(point, center, fov=400.0, zOffset=200.0):
    x, y, z = point
    z += zOffset
    f = fov / max(1e-6, z)
    return int(center[0] + x * f), int(center[1] + y * f)

class CubeRenderer:
    def __init__(self, center: Tuple[int, int], baseSize: float = 27.0, amplitude: float = 2.0, pulseSpeed: float = 15.0):
        self.center = center
        self.baseSize = baseSize
        self.amplitude = amplitude
        self.pulseSpeed = pulseSpeed
        self.edges = [
            (0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3),
            (2, 6), (3, 7), (4, 5), (4, 6), (5, 7), (6, 7)
        ]
        self.rotation = Rotation3D(
            angles=(0.0, 0.0, 0.0),
            rates=(1.2, 0.9, 0.6)
        )

    def getVertices(self) -> List[List[float]]:
        size = self.baseSize  # Fixed size, no pulsing
        return [
            [x, y, z]
            for x in (-size, size)
            for y in (-size, size)
            for z in (-size, size)
        ]

    def update(self, dt: float) -> None:
        self.rotation.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        vertices = self.getVertices()
        rotated = self.rotation.rotatePoints(vertices)
        projected = [
            projectPerspective(p, self.center, fov=400, zOffset=200)
            for p in rotated
        ]
        for i, j in self.edges:
            pygame.draw.aaline(surface, (100, 255, 200), projected[i], projected[j])
