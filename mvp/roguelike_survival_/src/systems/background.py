import pygame
import random
import math
from src.config import *

class BackgroundSystem:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Simple stars/dust particles
        self.particles = []
        for _ in range(100):
            self.particles.append({
                'pos': pygame.Vector2(random.uniform(0, WORLD_W), random.uniform(0, WORLD_H)),
                'size': random.uniform(1, 3),
                'speed_mult': random.uniform(0.2, 0.5), # Parallax effect
                'color': random.choice([(40, 40, 80), (60, 60, 100), (30, 30, 60)])
            })

    def draw(self, surface, camera):
        ox, oy = camera.offset
        scale = camera.zoom
        
        for p in self.particles:
            # Apply parallax by using speed_mult
            # This makes background move slower than the foreground
            px = (p['pos'].x * scale + ox * p['speed_mult']) % self.width
            py = (p['pos'].y * scale + oy * p['speed_mult']) % self.height
            
            s = int(p['size'] * scale)
            if s > 0:
                pygame.draw.circle(surface, p['color'], (int(px), int(py)), s)
