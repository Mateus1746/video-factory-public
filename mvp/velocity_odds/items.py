import pygame
import math
import random
from config import *

class PowerUp:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type # 'INVERT', 'MOON', 'TURBO', 'GLITCH'
        self.radius = 12
        self.active = True
        
        # Animation float
        self.anim_offset = random.uniform(0, 6.28)
        
        # Set visuals
        if self.type == 'INVERT':
            self.color = COLOR_EVENT_INVERT
            self.symbol = "I"
        elif self.type == 'MOON':
            self.color = COLOR_EVENT_MOON
            self.symbol = "M"
        elif self.type == 'TURBO':
            self.color = COLOR_EVENT_TURBO
            self.symbol = "T"
        else: # GLITCH
            self.color = COLOR_EVENT_GLITCH
            self.symbol = "?"

    def check_collision(self, ball_x, ball_y, ball_radius):
        if not self.active: return False
        
        # Distance check
        dist = math.hypot(self.x - ball_x, self.y - ball_y)
        return dist < (self.radius + ball_radius)

    def draw(self, surface, font):
        if not self.active: return
        
        # Bobbing animation
        t = pygame.time.get_ticks() / 300.0
        offset_y = math.sin(t + self.anim_offset) * 3
        
        draw_x = int(self.x)
        draw_y = int(self.y + offset_y)
        
        # Draw Glow
        # pygame.draw.circle(surface, (self.color[0]//3, self.color[1]//3, self.color[2]//3), (draw_x, draw_y), self.radius + 4)
        
        # Draw Main Orb
        pygame.draw.circle(surface, self.color, (draw_x, draw_y), self.radius)
        
        # Draw Symbol
        txt = font.render(self.symbol, True, (0,0,0))
        rect = txt.get_rect(center=(draw_x, draw_y))
        surface.blit(txt, rect)
        
        # Draw Border
        pygame.draw.circle(surface, WHITE, (draw_x, draw_y), self.radius, 1)
