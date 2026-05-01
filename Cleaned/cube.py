"""3D cube renderer with perspective projection."""

import pygame
import math
from typing import Tuple, List


class Rotation3D:
    """Manages 3D rotation state and applies combined rotation matrices."""
    def __init__(self, angles=(0.0, 0.0, 0.0), rates=(0.0, 0.0, 0.0)):
        self.ax, self.ay, self.az = angles
        self.vx, self.vy, self.vz = rates
        self._M = None

    def setRates(self, rates):
        self.vx, self.vy, self.vz = rates

    def setAngles(self, angles):
        self.ax, self.ay, self.az = angles
        self._recomputeMatrix()

    def update(self, dt):
        """Update rotation angles."""
        self.ax = (self.ax + self.vx * dt) % (2 * math.pi)
        self.ay = (self.ay + self.vy * dt) % (2 * math.pi)
        self.az = (self.az + self.vz * dt) % (2 * math.pi)
        self._recomputeMatrix()

    def rotatePoint(self, p):
        """Rotate a single point."""
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
        """Rotate multiple points."""
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

    def _recomputeMatrix(self):
        """Compute combined rotation matrix Rz * Ry * Rx."""
        cx, sx = math.cos(self.ax), math.sin(self.ax)
        cy, sy = math.cos(self.ay), math.sin(self.ay)
        cz, sz = math.cos(self.az), math.sin(self.az)

        Rx = ((1, 0, 0), (0, cx, -sx), (0, sx, cx))
        Ry = ((cy, 0, sy), (0, 1, 0), (-sy, 0, cy))
        Rz = ((cz, -sz, 0), (sz, cz, 0), (0, 0, 1))

        def matmul(A, B):
            return tuple(
                tuple(sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3))
                for i in range(3)
            )
        self._M = matmul(Rz, matmul(Ry, Rx))


def projectPerspective(point, center, fov=400.0, zOffset=200.0):
    """Project 3D point to 2D screen space."""
    x, y, z = point
    z += zOffset
    f = fov / max(1e-6, z)
    return int(center[0] + x * f), int(center[1] + y * f)


class CubeRenderer:
    """Renders a rotating 3D cube."""
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
        """Get cube vertices."""
        size = self.baseSize
        return [
            [x, y, z]
            for x in (-size, size)
            for y in (-size, size)
            for z in (-size, size)
        ]

    def update(self, dt: float) -> None:
        """Update rotation."""
        self.rotation.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the cube."""
        vertices = self.getVertices()
        rotated = self.rotation.rotatePoints(vertices)
        projected = [
            projectPerspective(p, self.center, fov=400, zOffset=200)
            for p in rotated
        ]
        for i, j in self.edges:
            pygame.draw.aaline(surface, (100, 255, 200), projected[i], projected[j])
