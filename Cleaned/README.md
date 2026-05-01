# Bullet Hell Vibe Coding - Cleaned Edition

## Overview
A high-performance Bullet Hell/Danmaku game prototype built with PyGame and audio-reactive visual effects.

## Features
- **Multiple Bullet Patterns**: Radial, orbiting, sinusoidal, rotating lines, and Bézier curves
- **Audio-Reactive Visuals**: Real-time beat detection on kick drums with adaptive cube pulsing
- **3D Rotating Cube**: Perspective-projected 3D rendering
- **Player Character**: WASD movement, spacebar shooting, CTRL sword attacks
- **Performance**: Optimized bullet culling and efficient sprite management

## Project Structure
```
Cleaned/
├── main.py                 # Main game loop
├── settings.py            # Global configuration
├── player.py              # Player character class
├── bullet_system.py       # Bullet and emitter classes
├── emitter_manager.py     # Emitter management
├── cube.py                # 3D cube rendering
├── beat_pulse.py          # Audio analysis
└── hud.py                 # UI display
```

## Requirements
- Python 3.8+
- pygame
- numpy

## Controls
- **WASD** - Move player
- **Space** - Shoot bullets
- **CTRL** - Swing sword
- **1-5** - Toggle bullet patterns
- **ESC** - Exit game

## Patterns
1. **Straight** - Radial bullets moving outward
2. **Orbiting** - Bullets that orbit then fly out
3. **Sine** - Bullets with sinusoidal wiggle
4. **Line** - Bullets along a rotating line
5. **Curve** - Bullets following Bézier curves

## Audio
Place your 44100 Hz WAV file at `assets/audio/test1_125bpm.wav` for beat-synchronized effects.
