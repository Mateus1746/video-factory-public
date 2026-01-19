import pygame
import math
import random
from ..audio import generate_note_sound
from ..effects import spawn_particles

class BinaryGlitch:
    """
    Binary Glitch uses bitwise logic (XOR patterns) to determine 
    the location and intensity of its attacks.
    """
    def __init__(self, center, rings):
        self.center = center
        self.rings = rings
        self.glitches = [] # (rect, timer, bits)
        self.timer = 0.0
        self.interval = 0.08
        self.color = (0, 255, 0) # Matrix Green
        self.step = 0
        
    def update(self, dt):
        self.timer -= dt
        self.step += 1
        
        if self.timer <= 0:
            self.timer = self.interval
            
            active_rings = [r for r in self.rings if r.alive]
            if active_rings:
                for _ in range(8):
                    target_ring = random.choice(active_rings)
                    # Pick a point near the ring
                    angle = random.uniform(0, 2 * math.pi)
                    # Bitwise-influenced offset
                    bits = (self.step + _) % 256
                    offset = ((bits ^ 0xAA) % 40) - 20
                    dist = target_ring.radius + offset
                    
                    x = self.center[0] + math.cos(angle) * dist
                    y = self.center[1] + math.sin(angle) * dist
                    
                    w, h = 16, 16
                    self.glitches.append([pygame.Rect(x - 8, y - 8, w, h), 0.2, bits])
            
        # Update glitches
        for g in self.glitches:
            g[1] -= dt
            rect = g[0]
            if g[1] > 0:
                dist = math.hypot(rect.centerx - self.center[0], rect.centery - self.center[1])
                for ring in self.rings:
                    if ring.alive and abs(dist - ring.radius) < 30: # Increased window
                        # Damage scales with the bitwise result
                        damage = 15 + (g[2] * 2.5) # Balanced (was 25 + bits*5)
                        ring.take_damage(damage * dt * 10)
                        if random.random() < 0.05:
                            spawn_particles(rect.centerx, rect.centery, self.color, 1)
                    
        self.glitches = [g for g in self.glitches if g[1] > 0]

    def draw(self, surface):
        for g in self.glitches:
            rect, life, bits = g
            # Color intensity based on bits
            c = (0, min(255, 100 + bits * 10), 0)
            pygame.draw.rect(surface, c, rect)
            pygame.draw.rect(surface, (200, 255, 200), rect, 1)
            
            # Visual binary digit representation
            if life > 0.1:
                font = pygame.font.SysFont("monospace", 10)
                txt = font.render("1" if bits % 2 == 0 else "0", True, (0, 255, 0))
                surface.blit(txt, rect.topleft)