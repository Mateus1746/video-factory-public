import pygame
import math
import random
from ..config import WHITE
from ..audio import generate_note_sound
from ..effects import spawn_particles

class ChaosJumper:
    def __init__(self, center, rings):
        self.center = center
        self.rings = rings
        self.x = center[0]
        self.y = center[1]
        self.jump_timer = 0.0
        self.jump_interval = 0.4
        self.radius = 20
        self.color = (255, 50, 50) 
        self.r = 3.95
        self.lx = 0.5
        self.ly = 0.3
        self.projectiles = []

    def next_chaos(self):
        self.lx = self.r * self.lx * (1 - self.lx)
        self.ly = self.r * self.ly * (1 - self.ly)
        return self.lx, self.ly

    def update(self, dt):
        self.jump_timer -= dt
        
        # Local jumping (Visual Glitch at Base)
        if self.jump_timer <= 0:
            self.jump_timer = self.jump_interval
            cx, cy = self.next_chaos()
            angle = cy * 2 * math.pi
            # Jump around HOME base
            self.x = self.center[0] + math.cos(angle) * 50
            self.y = self.center[1] + math.sin(angle) * 50
            
            # Spawn Projectile targeting local rings
            alive_rings = [r for r in self.rings if r.alive]
            if alive_rings:
                target_ring = random.choice(alive_rings)
                # Target a random point ON the ring
                angle_t = random.uniform(0, 2 * math.pi)
                tx = target_ring.center[0] + math.cos(angle_t) * target_ring.radius
                ty = target_ring.center[1] + math.sin(angle_t) * target_ring.radius

                # Chaos Bomb
                self.projectiles.append({
                    'pos': [self.x, self.y],
                    'target': [tx, ty],
                    'speed': 800,
                    'damage': 18000 + (cx * 18000), # Buffed (was 5250)
                    'color': self.color
                })

        # Update Projectiles
        for p in self.projectiles:
            dx = p['target'][0] - p['pos'][0]
            dy = p['target'][1] - p['pos'][1]
            dist = math.hypot(dx, dy)
            
            if dist < 20:
                # Hit (simplified AOE at target location)
                spawn_particles(p['pos'][0], p['pos'][1], p['color'], 15)
                # Apply damage to rings near impact
                for ring in self.rings:
                    if ring.alive:
                        d_ring = math.hypot(p['pos'][0] - ring.center[0], p['pos'][1] - ring.center[1])
                        if abs(d_ring - ring.radius) < 80:
                             ring.take_damage(p['damage'])
                             if random.random() < 0.3 and ring.note_frequency:
                                 generate_note_sound(ring.note_frequency, 0.2).play()
                p['speed'] = 0 # Mark for removal
            else:
                # Move
                move_dist = p['speed'] * dt
                p['pos'][0] += (dx / dist) * move_dist
                p['pos'][1] += (dy / dist) * move_dist
                
        self.projectiles = [p for p in self.projectiles if p['speed'] > 0]

    def draw(self, surface):
        # Draw Main Jumper
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        inner_r = int(self.radius * self.lx)
        if inner_r > 0:
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), inner_r, 1)
            
        # Draw Projectiles
        for p in self.projectiles:
            pygame.draw.circle(surface, p['color'], (int(p['pos'][0]), int(p['pos'][1])), 8)