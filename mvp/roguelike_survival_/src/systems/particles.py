import pygame
import random
import math

class Particle:
    __slots__ = ['x', 'y', 'color', 'vx', 'vy', 'size', 'max_life', 'life']
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

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self._surface_cache = {}

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
        alive = []
        for p in self.particles:
            p.update(dt)
            if p.life > 0:
                alive.append(p)
        self.particles = alive

    def _get_particle_surf(self, color, size, alpha):
        q_size = int(size)
        q_alpha = (int(alpha) // 10) * 10
        key = (color, q_size, q_alpha)
        
        if key not in self._surface_cache:
            if q_size <= 0: return None
            s = pygame.Surface((q_size * 2, q_size * 2), pygame.SRCALPHA).convert_alpha()
            pygame.draw.circle(s, (*color, q_alpha), (q_size, q_size), q_size)
            self._surface_cache[key] = s
        return self._surface_cache[key]

    def draw(self, surface, camera):
        for p in self.particles:
            alpha = int(255 * (p.life / p.max_life))
            size = max(1, p.size * (p.life / p.max_life))
            scaled_size = camera.apply_scale(size)
            
            p_surf = self._get_particle_surf(p.color, scaled_size, alpha)
            if p_surf:
                pos = camera.apply(p.x, p.y)
                surface.blit(p_surf, (pos[0] - scaled_size, pos[1] - scaled_size), special_flags=pygame.BLEND_ADD)
