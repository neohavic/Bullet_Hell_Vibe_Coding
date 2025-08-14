from bullet_system import *

# ----------------------------
# Emitter Manager & Setup
# ----------------------------

class EmitterManager:
    def __init__(self):
        self.emitters = {}  # name → Emitter instance
        self.active   = {}  # name → bool

    def add(self, name, emitter, initially_active=False):
        self.emitters[name] = emitter
        self.active[name]   = initially_active

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

def init_emitters(manager: EmitterManager) -> None:
    manager.add("straight", RadialEmitter(), initially_active=True)
    manager.add("orbiting", OrbitingEmitter(), initially_active=False)
    manager.add("sine", SineEmitter(), initially_active=False)
    manager.add("line", RotatingLineEmitter(), initially_active=False)
    manager.add("curve", CurveEmitter(count=12, radius=EDGE_RADIUS, travel_frames=90), initially_active=False)