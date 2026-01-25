import pygame
import math
import random
from .base import Entity
from ..config import WHITE
from ..audio import generate_note_sound
from ..effects import spawn_particles

class RadarSweep(Entity):
    NAME = "RADAR SWEEP"
    COLOR = (255, 50, 50)

    def __init__(self, center, rings, projectile_manager=None):
        super().__init__(center, rings, projectile_manager)
        self.angle = 0.0
        self.speed = 5.0 
        self.color = self.COLOR 
        self.max_radius = 150 # Local scan
        self.projectiles = []
        self.scan_cooldown = 0.0
        
    def update(self, dt):
        self.angle += self.speed * dt
        self.angle %= 6.28
        self.scan_cooldown -= dt
        
        # Scan local area (Visual)
        # If angle aligns with an enemy ring (which is always true directionally, but let's simulate a lock)
        # We fire a "Tracer" towards a random point on an enemy ring
        if self.scan_cooldown <= 0 and self.rings:
            active_rings = [r for r in self.rings if r.alive]
            if active_rings:
                self.scan_cooldown = 0.1
                target_ring = random.choice(active_rings)
                # Random point on ring
                t_angle = random.uniform(0, 6.28)
                tx = target_ring.center[0] + math.cos(t_angle) * target_ring.radius
                ty = target_ring.center[1] + math.sin(t_angle) * target_ring.radius
                
                self.projectiles.append({
                    'pos': [self.center[0], self.center[1]],
                    'target': [tx, ty],
                    'speed': 1200,
                    'damage': 6500 # Buffed (was 3500)
                })
                
        # Update Projectiles
        for p in self.projectiles:
            dx = p['target'][0] - p['pos'][0]
            dy = p['target'][1] - p['pos'][1]
            dist = math.hypot(dx, dy)
            
            if dist < 30:
                # Hit
                spawn_particles(p['pos'][0], p['pos'][1], self.color, 5)
                # Apply damage
                for ring in self.rings:
                    if ring.alive:
                        d_ring = math.hypot(p['pos'][0] - ring.center[0], p['pos'][1] - ring.center[1])
                        if abs(d_ring - ring.radius) < 30:
                             ring.take_damage(p['damage'])
                             if random.random() < 0.1 and ring.note_frequency:
                                 generate_note_sound(ring.note_frequency, 0.05).play()
                p['speed'] = 0
            else:
                move = p['speed'] * dt
                p['pos'][0] += (dx / dist) * move
                p['pos'][1] += (dy / dist) * move
                
        self.projectiles = [p for p in self.projectiles if p['speed'] > 0]

    def draw(self, surface):
        # Draw Radar Dish/Scan at Home
        end_x = self.center[0] + math.cos(self.angle) * self.max_radius
        end_y = self.center[1] + math.sin(self.angle) * self.max_radius
        pygame.draw.line(surface, self.color, self.center, (end_x, end_y), 3)
        pygame.draw.circle(surface, self.color, self.center, 5)
        
        # Draw Projectiles
        for p in self.projectiles:
            pygame.draw.line(surface, self.color, (p['pos'][0], p['pos'][1]), 
                             (p['pos'][0] - 10, p['pos'][1] - 10), 2) # Simple trace
