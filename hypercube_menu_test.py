import pygame
import numpy as np
import math

# Initialize PyGame
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Trail surface for glow and motion blur
trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# Generate base hypercube vertices
def generate_hypercube_vertices(scale=1.08):  # 50% larger
    return [np.array([x, y, z, w]) * scale
            for x in (-1, 1)
            for y in (-1, 1)
            for z in (-1, 1)
            for w in (-1, 1)]

# Connect vertices that differ by one coordinate
def generate_edges(vertices):
    edges = []
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            if np.sum(vertices[i] != vertices[j]) == 1:
                edges.append((i, j))
    return edges

# Rotation in 4D space
def rotate_4d(point, angle, axis1, axis2):
    rotation_matrix = np.identity(4)
    c, s = math.cos(angle), math.sin(angle)
    rotation_matrix[axis1, axis1] = c
    rotation_matrix[axis1, axis2] = -s
    rotation_matrix[axis2, axis1] = s
    rotation_matrix[axis2, axis2] = c
    return rotation_matrix @ point

# Project 4D → 3D → 2D
def project(point):
    w = 2 / (2 - point[3])
    point3d = point[:3] * w
    z = 2 / (4 - point3d[2])
    x = point3d[0] * z * 100 + WIDTH // 2
    y = point3d[1] * z * 100 + HEIGHT // 2
    return int(x), int(y)

# Base vertices and edges
base_vertices = generate_hypercube_vertices()
edges = generate_edges(base_vertices)
t = 0

running = True
while running:
    screen.fill(BLACK)
    t += 0.01

    # Morphing scales using sine wave
    phase = t % (2 * math.pi)
    outer_scale = max(0.1, math.cos(phase * 2))  # Shrinks to point
    inner_scale = max(0.1, math.sin(phase))      # Grows to full

    # Outer cube morph
    outer_vertices = [v * outer_scale for v in base_vertices]
    # Inner cube morph
    inner_vertices = [v * inner_scale for v in base_vertices]

    # Apply rotation
    def transform(vertices):
        rotated = []
        for v in vertices:
            v = rotate_4d(v, t * 0.5, 0, 1)
            v = rotate_4d(v, t * 0.3, 0, 2)
            v = rotate_4d(v, t * 0.2, 1, 2)
            rotated.append(v)
        return rotated

    outer_rotated = transform(outer_vertices)
    inner_rotated = transform(inner_vertices)

    # Project to 2D
    outer_projected = [project(v) for v in outer_rotated]
    inner_projected = [project(v) for v in inner_rotated]

    # Fade previous trails slightly (motion blur)
    trail_surface.fill((0, 0, 0, 10))  # Lower alpha = longer blur

    # Draw glowing red inner cube edges with trails
    for i, j in edges:
        start = inner_projected[i]
        end = inner_projected[j]
        for glow_pass in range(3):
            glow_color = (255, 60 * glow_pass, 60 * glow_pass)  # Red glow gradient
            thickness = 3 - glow_pass
            pygame.draw.line(trail_surface, glow_color, start, end, thickness)

    # Draw outer cube edges with faint white lines for motion blur
    for i, j in edges:
        start = outer_projected[i]
        end = outer_projected[j]
        pygame.draw.line(trail_surface, (255, 255, 255, 80), start, end, 1)

    # Blit trail surface onto main screen
    screen.blit(trail_surface, (0, 0))

    pygame.display.flip()
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

pygame.quit()