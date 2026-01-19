import pygame
import math
from ..config import WHITE
from ..audio import generate_note_sound
from ..effects import spawn_particles

class OrbitStriker:
    def __init__(self, center, rings):
        self.center = center
        self.rings = rings
        self.angle = 0.0
        self.radius = 360 # Slightly larger than largest ring (340)
        self.speed = 2.0 # Radians per second
        self.projectiles = []
        self.fire_timer = 0.0
        self.fire_rate = 0.035 # Buffed fire rate (Machine Gun)
        self.color = (0, 255, 128) # Spring Green
        
    def update(self, dt):
        self.angle += self.speed * dt
        self.fire_timer -= dt
        
        orbiter_x = self.center[0] + math.cos(self.angle) * self.radius
        orbiter_y = self.center[1] + math.sin(self.angle) * self.radius
        
        # Fire
        if self.fire_timer <= 0:
            self.fire_timer = self.fire_rate
            # Shoot towards center
            dx = self.center[0] - orbiter_x
            dy = self.center[1] - orbiter_y
            dist = math.hypot(dx, dy)
            vx = (dx / dist) * 1200 # Faster projectiles (1200)
            vy = (dy / dist) * 1200
            self.projectiles.append({
                'pos': [orbiter_x, orbiter_y],
                'vel': [vx, vy],
                'active': True
            })
            
        # Update projectiles
        for p in self.projectiles:
            if not p['active']: continue
            
            p['pos'][0] += p['vel'][0] * dt
            p['pos'][1] += p['vel'][1] * dt
            
            px, py = p['pos'][0], p['pos'][1]
            dist_to_center = math.hypot(px - self.center[0], py - self.center[1])
            
            # Check collisions
            hit = False
            for ring in self.rings:
                if ring.alive:
                     # Simple distance check for ring width
                    if abs(dist_to_center - ring.radius) < 20:
                        ring.take_damage(2800) # Buffed (was 1540)
                        if ring.note_frequency:
                            generate_note_sound(ring.note_frequency, 0.05).play()
                        spawn_particles(px, py, self.color, 5)
                        hit = True
                        break
            
            if hit or dist_to_center < 10 or dist_to_center > 500:
                p['active'] = False
                
        self.projectiles = [p for p in self.projectiles if p['active']]

    def draw(self, surface):
        # Draw Orbiter
        orbiter_x = self.center[0] + math.cos(self.angle) * self.radius
        orbiter_y = self.center[1] + math.sin(self.angle) * self.radius
        
        pygame.draw.circle(surface, self.color, (int(orbiter_x), int(orbiter_y)), 15)
        
        # Draw Projectiles
        for p in self.projectiles:
            pygame.draw.circle(surface, WHITE, (int(p['pos'][0]), int(p['pos'][1])), 4)
