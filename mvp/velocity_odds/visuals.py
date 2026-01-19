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
    
    # Draw Glow (Outer layers)
    # We iterate to create a fading halo
    r, g, b = color
    for i in range(GLOW_INTENSITY, 0, -1):
        alpha = 50 // i
        glow_thick = thickness + (i * 4)
        
        # Create a temporary surface for alpha blending if needed, 
        # but pygame.draw.arc doesn't support alpha directly on the main surface well without SRCALPHA.
        # For simplicity/performance in this loop, we might just draw lines or use a simpler trick.
        # Ideally, we'd blit a texture, but let's stick to vector drawing.
        # Alternative: Draw mostly the solid core, maybe one faint outline.
        pass # Pygame's draw.arc is tricky with alpha. Let's stick to a solid bright core for now.

    # Main Core
    pygame.draw.arc(surface, color, rect, p_start, p_end, thickness)
    
    # White Highlight (Simulate hot core)
    pygame.draw.arc(surface, (255, 255, 255), rect, p_start, p_end, 1)


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        # Ensure color is int tuple (R, G, B)
        try:
            self.color = (int(color[0]), int(color[1]), int(color[2]))
        except:
            self.color = (255, 255, 255)
            
        # Explosive velocity
        speed = random.uniform(2, 6)
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.05)
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        self.size = max(0, self.size - 0.1)

    def draw(self, surface):
        if self.life > 0:
            # Create a surface for alpha
            s = pygame.Surface((int(self.size*4), int(self.size*4)), pygame.SRCALPHA)
            alpha = int(self.life * 255)
            
            # Draw glowy circle
            pygame.draw.circle(s, (*self.color, alpha), (int(self.size*2), int(self.size*2)), int(self.size))
            surface.blit(s, (self.x - self.size*2, self.y - self.size*2))


class Trail:
    def __init__(self, color, max_length=TRAIL_LENGTH):
        self.points = deque(maxlen=max_length)
        self.color = color

    def update(self, x, y):
        # Only add point if it moved enough (optimization)
        if not self.points or math.hypot(self.points[-1][0] - x, self.points[-1][1] - y) > 2:
            self.points.append((x, y))

    def draw(self, surface, offset_x=0, offset_y=0):
        if len(self.points) < 2:
            return

        pts = list(self.points)
        # Shift points
        shifted_pts = [(p[0]+offset_x, p[1]+offset_y) for p in pts]
        
        for i in range(len(shifted_pts) - 1):
            start = shifted_pts[i]
            end = shifted_pts[i+1]
            
            progress = i / len(shifted_pts)
            # Fade out to black/transparent or dim version of self.color
            # Simple fade:
            alpha_ratio = progress
            
            # Mix self.color with black based on progress
            # r = int(self.color[0] * alpha_ratio)
            # g = int(self.color[1] * alpha_ratio)
            # b = int(self.color[2] * alpha_ratio)
            # Actually simpler: standard alpha doesn't work well with lines without surface.
            # Let's just scale brightness.
            
            col = (
                int(self.color[0] * alpha_ratio),
                int(self.color[1] * alpha_ratio),
                int(self.color[2] * alpha_ratio)
            )
            
            thickness = int(progress * BALL_RADIUS)
            if thickness < 1: thickness = 1
            
            pygame.draw.line(surface, col, start, end, thickness)

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
