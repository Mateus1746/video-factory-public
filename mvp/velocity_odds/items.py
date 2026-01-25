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
        
        # Metadata for Renderer
        if self.type == 'INVERT':
            self.symbol = "I"
            self.color_key = "COLOR_EVENT_INVERT"
        elif self.type == 'MOON':
            self.symbol = "M"
            self.color_key = "COLOR_EVENT_MOON"
        elif self.type == 'TURBO':
            self.symbol = "T"
            self.color_key = "COLOR_EVENT_TURBO"
        else: # GLITCH
            self.symbol = "?"
            self.color_key = "COLOR_EVENT_GLITCH"

    def check_collision(self, ball_x, ball_y, ball_radius):
        if not self.active: return False
        
        # Squared Distance check (Optimization: no math.hypot)
        dx = self.x - ball_x
        dy = self.y - ball_y
        dist_sq = dx*dx + dy*dy
        rad_sum = self.radius + ball_radius
        return dist_sq < (rad_sum * rad_sum)

