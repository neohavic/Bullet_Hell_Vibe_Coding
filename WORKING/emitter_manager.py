from bullet_system import *

# ----------------------------
# Emitter Manager & Setup
# ----------------------------

class EmitterManager:
    def __init__(self):
        self.emitters = {}  # name → Emitter instance
        self.active   = {}  # name → bool

    def add(self, name, emitter, initiallyActive=False):
        self.emitters[name] = emitter
        self.active[name]   = initiallyActive

    def enable(self, name):
        if name in self.active:
            self.active[name] = True

    def disable(self, name):
        if name in self.active:
            self.active[name] = False

    def toggle(self, name):
        if name in self.active:
            self.active[name] = not self.active[name]

    def update(self):
        for name, em in self.emitters.items():
            if self.active.get(name, False):
                em.update()

    def draw(self, surface):
        for name, em in self.emitters.items():
            if self.active.get(name, False):
                em.draw(surface)

def initEmitters(manager: EmitterManager) -> None:
    manager.add("straight", RadialEmitter(), initiallyActive=True)
    manager.add("orbiting", OrbitingEmitter(), initiallyActive=False)
    manager.add("sine", SineEmitter(), initiallyActive=False)
    manager.add("line", RotatingLineEmitter(), initiallyActive=False)
    manager.add("curve", CurveEmitter(count=12, radius=edgeRadius, travelFrames=90), initiallyActive=False)
