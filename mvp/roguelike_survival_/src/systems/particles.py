
import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color, velocity, size, life):
        self.x = x
        self.y = y
        self.color = color
        self.vx = velocity[0]
        self.vy = velocity[1]
        self.size = size
        self.max_life = life
        self.life = life

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        self.size = max(0, self.size - dt * 2)

    def draw(self, surface, offset=(0,0)):
        if self.life <= 0: return
        alpha = int(255 * (self.life / self.max_life))
        pos = (int(self.x + offset[0]), int(self.y + offset[1]))
        
        surf = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
        surface.blit(surf, (pos[0]-self.size, pos[1]-self.size), special_flags=pygame.BLEND_ADD)

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, count=10, speed=100):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            sp = random.uniform(speed * 0.5, speed * 1.5)
            vx = math.cos(angle) * sp
            vy = math.sin(angle) * sp
            size = random.uniform(2, 6)
            life = random.uniform(0.3, 0.9)
            self.particles.append(Particle(x, y, color, (vx, vy), size, life))

    def update(self, dt):
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update(dt)

    def draw(self, surface, offset=(0,0)):
        for p in self.particles:
            p.draw(surface, offset)
