"""Manager for controlling multiple bullet emitters."""

from bullet_system import *


class EmitterManager:
    """Manages multiple emitters and their active states."""
    def __init__(self):
        self.emitters = {}
        self.active = {}

    def add(self, name, emitter, initiallyActive=False):
        """Add an emitter to the manager."""
        self.emitters[name] = emitter
        self.active[name] = initiallyActive

    def enable(self, name):
        """Enable an emitter."""
        if name in self.active:
            self.active[name] = True

    def disable(self, name):
        """Disable an emitter."""
        if name in self.active:
            self.active[name] = False

    def toggle(self, name):
        """Toggle an emitter."""
        if name in self.active:
            self.active[name] = not self.active[name]

    def update(self):
        """Update all active emitters."""
        for name, em in self.emitters.items():
            if self.active.get(name, False):
                em.update()

    def draw(self, surface):
        """Draw all active emitters."""
        for name, em in self.emitters.items():
            if self.active.get(name, False):
                em.draw(surface)


def initEmitters(manager: EmitterManager) -> None:
    """Initialize all emitters."""
    manager.add("straight", RadialEmitter(), initiallyActive=True)
    manager.add("orbiting", OrbitingEmitter(), initiallyActive=False)
    manager.add("sine", SineEmitter(), initiallyActive=False)
    manager.add("line", RotatingLineEmitter(), initiallyActive=False)
    manager.add("curve", CurveEmitter(count=12, radius=edgeRadius, travelFrames=90), initiallyActive=False)
