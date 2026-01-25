import pygame
import random
import math
from .config import WIDTH, HEIGHT, COLORS

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
    _cache = {} # (size, color, alpha_step) -> Surface
    
    def __init__(self, x, y, color, size, speed_mult=1.0):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 8) * speed_mult
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 1.0
        self.decay = random.uniform(0.04, 0.08)
        self.color = color
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.9 # Friction (slower over time)
        self.vy *= 0.9
        self.life -= self.decay
        return self.life > 0

    def draw(self, surface, offset):
        if self.life > 0:
            # Discretize alpha to 10 steps to limit cache size
            alpha_step = int(self.life * 10) 
            alpha = int(self.life * 255)
            
            key = (self.size, self.color, alpha_step)
            
            if key not in Particle._cache:
                s = pygame.Surface((int(self.size*4), int(self.size*4)), pygame.SRCALPHA)
                pygame.draw.circle(s, (*self.color, alpha), (int(self.size*2), int(self.size*2)), int(self.size))
                Particle._cache[key] = s
            
            surface.blit(Particle._cache[key], (self.x - self.size*2 + offset[0], self.y - self.size*2 + offset[1]), special_flags=pygame.BLEND_ADD)

class Shockwave:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 10
        self.max_radius = 150
        self.width = 10
        self.life = 1.0
        
    def update(self):
        self.radius += (self.max_radius - self.radius) * 0.1
        self.width = max(1, self.width * 0.9)
        self.life -= 0.05
        return self.life > 0
        
    def draw(self, surface, offset):
        if self.life > 0:
            alpha = int(self.life * 255)
            # Draw arc or circle? Circle is easier
            # Pygame draw circle with width doesn't support alpha directly on surface well without surface creation
            # Optimization: Just draw a few expanding circles
            
            target_rect = pygame.Rect(
                self.x - self.radius + offset[0], 
                self.y - self.radius + offset[1], 
                self.radius*2, self.radius*2
            )
            
            # Simple ring optimization: 
            # If we want alpha, we must use a temp surface or gfxdraw.
            # For speed, let's use a non-alpha circle if alpha > 100, or skip.
            # Or better: just draw 4 dots rotating? No, shockwave needs to be a ring.
            # Let's use the efficient Surface method (created once? No, size changes).
            # Actually, standard draw.circle supports alpha color in pygame 2.0+!
            # Let's assume Pygame 2+ (project requirement).
            pygame.draw.circle(surface, (*self.color, alpha), (self.x + offset[0], self.y + offset[1]), int(self.radius), int(self.width))

class FloatingText:
    def __init__(self, x, y, text, color, font):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 1.0
        # Physics pop effect
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-6, -3) # Pop up
        self.gravity = 0.3
        self.font = font
        self.scale = 1.2 # Start big

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity # Gravity falls down
        self.life -= 0.02
        if self.scale > 1.0:
            self.scale -= 0.05
        return self.life > 0

    def draw(self, surface, offset):
        if self.life > 0:
            alpha = int(min(1, self.life * 2) * 255) # Fade out faster at end
            txt_surf = self.font.render(str(self.text), True, self.color)
            txt_surf.set_alpha(alpha)
            surface.blit(txt_surf, (self.x + offset[0], self.y + offset[1]))

class VirtualCursor:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.target_x = self.x
        self.target_y = self.y
        self.click_timer = 0
        # Cria o sprite do cursor (seta simples)
        self.surf = pygame.Surface((30, 40), pygame.SRCALPHA)
        # Desenha uma seta branca com borda preta
        points = [(0, 0), (0, 30), (8, 22), (16, 38), (22, 35), (14, 20), (24, 20)]
        pygame.draw.polygon(self.surf, (0, 0, 0), [(p[0]+2, p[1]+2) for p in points]) # Sombra
        pygame.draw.polygon(self.surf, (255, 255, 255), points)
        pygame.draw.polygon(self.surf, (0, 0, 0), points, 2)

    def move_to(self, x, y):
        self.target_x = x
        self.target_y = y
        self.click_timer = 5 # Frames de animação de clique

    def update(self):
        # Movimento Suave (Lerp)
        self.x += (self.target_x - self.x) * 0.3
        self.y += (self.target_y - self.y) * 0.3
        
        if self.click_timer > 0:
            self.click_timer -= 1

    def draw(self, surface):
        # Escala no clique
        scale = 0.8 if self.click_timer > 0 else 1.0
        if scale != 1.0:
            s = pygame.transform.scale(self.surf, (int(30*scale), int(40*scale)))
            surface.blit(s, (self.x, self.y))
        else:
            surface.blit(self.surf, (self.x, self.y))
