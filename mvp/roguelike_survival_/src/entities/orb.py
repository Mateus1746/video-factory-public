import pygame
import math
import random
from src.config import COLOR_XP, COLOR_TEXT
from src.utils import draw_glow

class XPOrb:
    def __init__(self, x, y, value=10):
        self.x = x
        self.y = y
        self.radius = 8
        self.value = value
        self.bob_timer = random.uniform(0, math.tau)
        self.collected = False
        
        # Magnet logic
        self.speed = 0
        self.max_speed = 600

    def update(self, dt, player):
        self.bob_timer += 5 * dt
        
        # Magnet logic
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        # Detection range for "eating" the orb
        if dist < player.radius + self.radius:
            self.collected = True
            return True
            
        # Magnet effect range
        if dist < 250:
            self.speed = min(self.max_speed, self.speed + 1500 * dt)
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt
            
        return False

    def draw(self, screen, offset):
        ox, oy = offset
        bob = math.sin(self.bob_timer) * 4
        
        draw_glow(screen, COLOR_XP, (int(self.x + ox), int(self.y + oy + bob)), self.radius)
        pygame.draw.circle(screen, COLOR_XP, (int(self.x + ox), int(self.y + oy + bob)), self.radius)
        pygame.draw.circle(screen, COLOR_TEXT, (int(self.x + ox), int(self.y + oy + bob)), self.radius - 4)
