import pygame
import math
import random
from .base import Entity
from ..config import WHITE
from ..audio import generate_note_sound
from ..effects import spawn_particles

class SonicWave(Entity):
    NAME = "SONIC WAVE"
    COLOR = (200, 200, 200)

    def __init__(self, center, rings, projectile_manager=None):
        super().__init__(center, rings, projectile_manager)
        self.sources = []
        self.timer = 0.0
        self.interval = 0.5
        self.color = self.COLOR
        self.wave_speed = 500.0 # Faster travel

    def update(self, dt):
        if not self.rings: return
        target_center = self.center

        self.timer -= dt
        if self.timer <= 0:
            self.timer = self.interval
            # Spawn wave at HOME
            angle = random.uniform(0, 2 * math.pi)
            self.sources.append({
                'pos': [self.center[0], self.center[1]],
                'dir': [0, 0], # Stationary source expanding locally
                'age': 0.0,
                'max_age': 4.0
            })
            
        # Update sources (Travel/Expand)
        for s in self.sources:
            s['age'] += dt
            
            # Wave expands as it travels (local expansion)
            radius = s['age'] * 150 
            
            # Check interaction with rings
            for ring in self.rings:
                if ring.alive:
                    # Check overlap of Wave Circle vs Ring Circle
                    d_centers = math.hypot(s['pos'][0] - ring.center[0], s['pos'][1] - ring.center[1])
                    
                    # If wave edge touches ring edge (approx)
                    if abs(d_centers - ring.radius) < radius + 10 and abs(d_centers - ring.radius) > radius - 20:
                        ring.take_damage(5500 * dt * 20) # Buffed (was 3500)
                        if random.random() < 0.1:
                            spawn_particles(s['pos'][0], s['pos'][1], self.color, 1)

        self.sources = [s for s in self.sources if s['age'] < s['max_age']]

    def draw(self, surface):
        for s in self.sources:
            radius = int(s['age'] * 150)
            if radius > 0:
                pygame.draw.circle(surface, self.color, (int(s['pos'][0]), int(s['pos'][1])), radius, 1)