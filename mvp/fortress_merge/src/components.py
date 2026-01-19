import pygame
import random
import math
from .config import WIDTH, COLORS

class Camera:
    def __init__(self):
        self.shake_intensity = 0
        self.offset_x = 0
        self.offset_y = 0

    def shake(self, intensity):
        self.shake_intensity = max(self.shake_intensity, intensity)

    def update(self):
        if self.shake_intensity > 0:
            self.offset_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.offset_y = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_intensity *= 0.9
            if self.shake_intensity < 0.5: self.shake_intensity = 0
        else:
            self.offset_x = 0
            self.offset_y = 0
            
    def get_offset(self):
        return (self.offset_x, self.offset_y)

class Particle:
    def __init__(self, x, y, color, size, speed_mult=1.0):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 10) * speed_mult
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 1.0
        self.decay = random.uniform(0.03, 0.06)
        self.color = color
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        self.life -= self.decay
        return self.life > 0

    def draw(self, surface, offset):
        if self.life > 0:
            alpha = int(self.life * 255)
            s = pygame.Surface((int(self.size*4), int(self.size*4)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (int(self.size*2), int(self.size*2)), int(self.size))
            surface.blit(s, (self.x - self.size*2 + offset[0], self.y - self.size*2 + offset[1]), special_flags=pygame.BLEND_ADD)

class FloatingText:
    def __init__(self, x, y, text, color, font):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 1.0
        self.vy = -WIDTH * 0.008
        self.font = font

    def update(self):
        self.y += self.vy
        self.life -= 0.03
        return self.life > 0

    def draw(self, surface, offset):
        if self.life > 0:
            alpha = int(self.life * 255)
            txt_surf = self.font.render(str(self.text), True, self.color)
            txt_surf.set_alpha(alpha)
            surface.blit(txt_surf, (self.x + offset[0], self.y + offset[1]))
