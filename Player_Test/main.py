# main.py
import pygame
from player import Player

pygame.init()
screen = pygame.display.set_mode((900, 900))
pygame.display.set_caption("Beam & Bullet Game")
clock = pygame.time.Clock()

# Enemy setup
enemy_size = 40
enemy_x = 430
enemy_y = 430
enemy_color = (255, 0, 0)

# Player setup
player = Player(100, 100)

running = True
while running:
    screen.fill((30, 30, 30))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.handle_input(keys)

    enemy_center = (enemy_x + enemy_size // 2, enemy_y + enemy_size // 2)
    player.update(enemy_center)
    player.draw(screen, enemy_center)

    pygame.draw.rect(screen, enemy_color, (enemy_x, enemy_y, enemy_size, enemy_size))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()