import pygame
import random
import math
from .config import *

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.05)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay

    def draw(self, surface):
        if self.life > 0:
            size = int(self.life * 4)
            c = (int(self.color[0]*self.life), int(self.color[1]*self.life), int(self.color[2]*self.life))
            pygame.draw.circle(surface, c, (int(self.x), int(self.y)), size)

class TrailEffect:
    def __init__(self, max_len=10):
        self.points = []
        self.max_len = max_len

    def add(self, pos):
        self.points.append(pos)
        if len(self.points) > self.max_len:
            self.points.pop(0)

    def draw(self, surface, color, radius=5):
        for i, pos in enumerate(self.points):
            factor = i / self.max_len
            c = (int(color[0]*factor), int(color[1]*factor), int(color[2]*factor))
            size = int(factor * radius)
            pygame.draw.circle(surface, c, pos, size // 2 + 1)

GLOBAL_PARTICLES = []

def spawn_particles(x, y, color, count=10):
    for _ in range(count):
        GLOBAL_PARTICLES.append(Particle(x, y, color))

def update_particles():
    global GLOBAL_PARTICLES
    for p in GLOBAL_PARTICLES:
        p.update()
    GLOBAL_PARTICLES = [p for p in GLOBAL_PARTICLES if p.life > 0]

def draw_particles(surface):
    for p in GLOBAL_PARTICLES:
        p.draw(surface)

GLOW_CACHE = {}

def create_glow_surface(radius, color):
    key = (radius, tuple(color))
    if key in GLOW_CACHE:
        return GLOW_CACHE[key]
        
    size = radius * 4
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    for r in range(radius * 2, 0, -1):
        alpha = int(100 * (1 - r / (radius * 2))**2)
        pygame.draw.circle(surf, (*color, alpha), (size // 2, size // 2), r)
    
    GLOW_CACHE[key] = surf
    return surf

class Starfield:
    def __init__(self, count=100):
        self.stars = []
        for _ in range(count):
            self.stars.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'size': random.uniform(0.5, 2.0),
                'speed': random.uniform(0.1, 0.5)
            })

    def update(self):
        for s in self.stars:
            s['y'] += s['speed']
            if s['y'] > SCREEN_HEIGHT:
                s['y'] = 0
                s['x'] = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface):
        for s in self.stars:
            pygame.draw.circle(surface, (100, 100, 120), (int(s['x']), int(s['y'])), int(s['size']))

FONT_SMALL = None
FONT_LARGE = None

def get_fonts():
    global FONT_SMALL, FONT_LARGE
    if FONT_SMALL is None:
        FONT_SMALL = pygame.font.SysFont("Arial", 16, bold=True)
    if FONT_LARGE is None:
        FONT_LARGE = pygame.font.SysFont("Arial", 40, bold=True)
    return FONT_SMALL, FONT_LARGE
