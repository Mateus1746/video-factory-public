import pygame
import math
import random
from ..config import GOLDEN_ANGLE, FIB_SPEED, SPIRAL_RADIUS, FIB_DAMAGE, YELLOW
from ..audio import generate_note_sound
from ..effects import TrailEffect, spawn_particles, create_glow_surface

class FibonacciSpiral:
    def __init__(self, center, rings):
        self.center = center
        self.rings = rings
        self.x = float(center[0])
        self.y = float(center[1])
        self.n = 1
        self.fib_prev = 0
        self.fib_curr = 1
        self.angle = 0.0
        self.projectiles = []
        self.fire_timer = 0.0
        self.set_next_target()

    def get_next_fib(self):
        nxt = self.fib_prev + self.fib_curr
        self.fib_prev = self.fib_curr
        self.fib_curr = nxt
        if self.fib_curr > 1000:
            self.fib_prev = 0
            self.fib_curr = 1
        return self.fib_curr

    def set_next_target(self):
        self.n += 1
        # Spin locally
        self.angle = self.n * GOLDEN_ANGLE
        # Local visual movement (Orbiting center)
        self.vx = math.cos(self.angle) * 20
        self.vy = math.sin(self.angle) * 20

    def update(self, dt):
        # Local Spin Animation
        self.x = self.center[0] + self.vx
        self.y = self.center[1] + self.vy
        
        # Fire Projectiles (Fibonacci Shards)
        self.fire_timer -= dt
        if self.fire_timer <= 0:
            self.fire_timer = 0.1
            self.set_next_target() # Advance pattern
            
            # Fire at random enemy ring
            if self.rings:
                active = [r for r in self.rings if r.alive]
                if active:
                    target = random.choice(active)
                    # Target circumference
                    angle_t = random.uniform(0, 2 * math.pi)
                    tx = target.center[0] + math.cos(angle_t) * target.radius
                    ty = target.center[1] + math.sin(angle_t) * target.radius
                    
                    self.projectiles.append({
                        'pos': [self.x, self.y],
                        'target_pos': [tx, ty],
                        'speed': 700,
                        'damage': FIB_DAMAGE,
                        'color': YELLOW
                    })

        # Update Projectiles
        for p in self.projectiles:
            # Home in on target pos
            dx = p['target_pos'][0] - p['pos'][0]
            dy = p['target_pos'][1] - p['pos'][1]
            dist = math.hypot(dx, dy)
            
            if dist < 20: # Hit logic
                p['speed'] = 0
                spawn_particles(p['pos'][0], p['pos'][1], p['color'], 5)
                # AOE Damage around impact
                for ring in self.rings:
                    if ring.alive:
                         d = math.hypot(p['pos'][0] - ring.center[0], p['pos'][1] - ring.center[1])
                         if abs(d - ring.radius) < 50:
                             ring.take_damage(p['damage'])
                             if random.random() < 0.2 and ring.note_frequency:
                                 generate_note_sound(ring.note_frequency, 0.1).play()
            else:
                move = p['speed'] * dt
                p['pos'][0] += (dx / dist) * move
                p['pos'][1] += (dy / dist) * move
                
        self.projectiles = [p for p in self.projectiles if p['speed'] > 0]

    def draw(self, surface):
        # Draw Base
        pos = (int(self.x), int(self.y))
        glow = create_glow_surface(SPIRAL_RADIUS, YELLOW)
        surface.blit(glow, (pos[0] - glow.get_width()//2, pos[1] - glow.get_height()//2), special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(surface, YELLOW, pos, SPIRAL_RADIUS)
        
        # Draw Projectiles
        for p in self.projectiles:
             pygame.draw.circle(surface, p['color'], (int(p['pos'][0]), int(p['pos'][1])), 6)