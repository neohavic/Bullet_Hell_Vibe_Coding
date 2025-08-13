import pygame
import math
from cube_no_pulse import *
from hud import *
from beat_pulse import BeatPulseController


# === CONFIG ===
WIDTH = 900
HEIGHT = 900
#AUDIO_FILE = "assets/audio/test1_125bpm.wav"
FPS = 60


CENTER = (WIDTH // 2, WIDTH // 2)

# === INIT ===
pygame.init()
FONT = pygame.font.SysFont("Arial", 18)
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()

cube = CubeRenderer(center=CENTER)
hud = HUDRenderer(font=FONT)
pulse = BeatPulseController("test1_125bpm.wav")

running = True
while running:
    SCREEN.fill((10, 10, 10))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # --- Cube updates
    dt = CLOCK.get_time() / 1000.0
    cube.update(dt)
    cube.draw(SCREEN)
    
    amp = pulse.update(dt)
    cube.base_size = 27.0 * amp
    
    hud.draw(SCREEN, CLOCK.get_fps(), 0)

    pygame.display.flip()
    CLOCK.tick(FPS)

pygame.quit()