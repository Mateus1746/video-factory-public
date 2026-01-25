import pygame
import math
import random
from collections import deque
from config import *

def draw_neon_arc(surface, color, center, radius, hole_angle, hole_width, thickness=4):
    """
    Draws an arc with a neon glow effect.
    """
    # Calculate angles
    start_angle = hole_angle + (hole_width / 2)
    end_angle = hole_angle - (hole_width / 2) + 360
    
    # Convert to radians for Pygame (CCW)
    p_start = math.radians(-end_angle)
    p_end = math.radians(-start_angle)
    
    rect = pygame.Rect(center[0]-radius, center[1]-radius, radius*2, radius*2)
    
    # Draw Glow layers for Bloom effect
    r, g, b = color
    for i in range(3, 0, -1):
        alpha = 40 // i
        glow_thick = thickness + (i * 6)
        # We use a custom blit for glow simulation
        glow_col = (r//(i*2), g//(i*2), b//(i*2))
        pygame.draw.arc(surface, glow_col, rect, p_start, p_end, glow_thick)

    # Main Core
    pygame.draw.arc(surface, color, rect, p_start, p_end, thickness)
    
    # White Highlight (Simulate hot core)
    pygame.draw.arc(surface, (255, 255, 255), rect, p_start, p_end, 2)


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        try:
            self.color = (int(color[0]), int(color[1]), int(color[2]))
        except:
            self.color = (255, 255, 255)
            
        speed = random.uniform(3, 8)
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.life = 1.0
        self.decay = random.uniform(0.015, 0.03)
        self.size = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        self.size = max(0, self.size - 0.1)

class Trail:
    def __init__(self, color, max_length=TRAIL_LENGTH):
        self.points = deque(maxlen=max_length)
        self.color = color

    def update(self, x, y):
        if not self.points or math.hypot(self.points[-1][0] - x, self.points[-1][1] - y) > 2:
            self.points.append((x, y))

    def draw(self, surface, offset_x=0, offset_y=0):
        if len(self.points) < 2: return
        pts = list(self.points)
        for i in range(len(pts) - 1):
            progress = i / len(pts)
            alpha_ratio = progress
            col = (int(self.color[0] * alpha_ratio), int(self.color[1] * alpha_ratio), int(self.color[2] * alpha_ratio))
            thickness = int(progress * BALL_RADIUS * 1.5)
            if thickness < 1: thickness = 1
            pygame.draw.line(surface, col, (pts[i][0]+offset_x, pts[i][1]+offset_y), 
                                           (pts[i+1][0]+offset_x, pts[i+1][1]+offset_y), thickness)

class FloatingText:
    def __init__(self, x, y, text, color, font):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = font
        self.life = 1.0
        self.vel_y = -3.0
        self.vx = random.uniform(-1, 1)
        
        self.surface = self.font.render(self.text, True, self.color)
        # Add shadow for readability
        self.shadow = self.font.render(self.text, True, (20, 20, 20))

    def update(self):
        self.y += self.vel_y
        self.x += self.vx
        self.life -= 0.02
        self.vel_y *= 0.95 # Slow down rise

    def draw(self, surface, offset_x=0, offset_y=0):
        if self.life <= 0: return
        
        # Simple fade by creating a copy with alpha would be slow per frame, 
        # so we just blit if life is high enough or handle it via renderer if optimized.
        # For simplicity in this step:
        pos = (int(self.x + offset_x), int(self.y + offset_y))
        surface.blit(self.shadow, (pos[0]+2, pos[1]+2))
        surface.blit(self.surface, pos)

class ScreenShake:
    def __init__(self):
        self.intensity = 0
        self.decay = 0.9

    def trigger(self, amount):
        self.intensity = amount

    def update(self):
        if self.intensity > 0.5:
            self.intensity *= self.decay
        else:
            self.intensity = 0

    def get_offset(self):
        if self.intensity > 0:
            dx = random.uniform(-self.intensity, self.intensity)
            dy = random.uniform(-self.intensity, self.intensity)
            return int(dx), int(dy)
        return 0, 0