import pygame
import math

# Initialize PyGame
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Load ship image
ship_img = pygame.image.load("assets/images/player_ship.png").convert_alpha()
ship_rect = ship_img.get_rect(center=(400, 300))

# Tilt angles for each frame
tilt_angles = [0, -5, -10, -15]  # Negative for left tilt

frame = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear screen
    screen.fill((0, 0, 0))

    # Rotate ship
    angle = tilt_angles[frame % len(tilt_angles)]
    rotated_img = pygame.transform.rotate(ship_img, angle)
    rotated_rect = rotated_img.get_rect(center=ship_rect.center)

    # Draw ship
    screen.blit(rotated_img, rotated_rect)

    # Update frame
    frame += 1
    pygame.display.flip()
    clock.tick(2)  # Slow frame rate to see tilt

pygame.quit()

