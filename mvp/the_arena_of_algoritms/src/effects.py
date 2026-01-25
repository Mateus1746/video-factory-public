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

class Fragment:
    """Represents a shattered piece of a ring."""
    def __init__(self, x, y, color, speed_mult=1.0):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(4, 12) * speed_mult
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-10, 10)
        self.life = 1.0
        self.decay = random.uniform(0.015, 0.03)
        self.size = random.uniform(3, 8)
        self.length = random.uniform(8, 20)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.angle += self.spin
        self.life -= self.decay

    def draw(self, surface):
        if self.life > 0:
            # Draw a rotating line segment
            rad = math.radians(self.angle)
            dx = math.cos(rad) * self.length / 2
            dy = math.sin(rad) * self.length / 2
            
            p1 = (self.x - dx, self.y - dy)
            p2 = (self.x + dx, self.y + dy)
            
            alpha = int(255 * self.life)
            # Pygame lines don't support alpha directly on main surf easily without surface blit, 
            # but we'll stick to solid fading color for performance in MVP
            c = (int(self.color[0]*self.life), int(self.color[1]*self.life), int(self.color[2]*self.life))
            
            pygame.draw.line(surface, c, p1, p2, int(self.size * self.life))

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
CRACKS_CACHE = {}

def spawn_particles(x, y, color, count=10):
    for _ in range(count):
        GLOBAL_PARTICLES.append(Particle(x, y, color))

def spawn_ring_explosion(center, radius, color, count=40):
    """Spawns fragments in a ring shape expanding outwards."""
    for i in range(count):
        angle = (i / count) * 2 * math.pi + random.uniform(-0.1, 0.1)
        # Position on the ring
        px = center[0] + math.cos(angle) * radius
        py = center[1] + math.sin(angle) * radius
        
        frag = Fragment(px, py, color)
        # Velocity mostly outwards
        frag.vx = math.cos(angle) * random.uniform(5, 15)
        frag.vy = math.sin(angle) * random.uniform(5, 15)
        GLOBAL_PARTICLES.append(frag)

def update_particles():
    global GLOBAL_PARTICLES
    for p in GLOBAL_PARTICLES:
        p.update()
    GLOBAL_PARTICLES = [p for p in GLOBAL_PARTICLES if p.life > 0]

def draw_particles(surface):
    for p in GLOBAL_PARTICLES:
        p.draw(surface)

def generate_cracks(radius, num_cracks=5):
    """Generates random crack paths for a ring."""
    cracks = []
    for _ in range(num_cracks):
        angle_start = random.uniform(0, 2 * math.pi)
        points = []
        curr_r = radius - RING_THICKNESS/2
        curr_a = angle_start
        
        # Jagged line moving inwards or along arc
        steps = random.randint(3, 6)
        for i in range(steps):
            x = math.cos(curr_a) * curr_r
            y = math.sin(curr_a) * curr_r
            points.append((x, y))
            
            curr_r -= random.uniform(0, 5)
            curr_a += random.uniform(-0.2, 0.2)
            
        cracks.append(points)
    return cracks

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

class RetroGrid:
    def __init__(self):
        self.offset_y = 0.0
        self.speed = 100.0
        self.spacing = 100
        self.horizon_y = SCREEN_HEIGHT // 2
        # Perspective projection params
        self.fov = 300
        
    def update(self, dt):
        self.offset_y = (self.offset_y + self.speed * dt) % self.spacing
        
    def draw(self, surface):
        # Draw Vertical Lines (Perspective)
        # Center X is vanishing point
        cx = SCREEN_WIDTH // 2
        cy = self.horizon_y
        
        # Bottom width is screen width + margin
        num_v_lines = 20
        bottom_width = SCREEN_WIDTH * 4
        
        for i in range(num_v_lines + 1):
            # Calculate x position at bottom
            x_bottom = (i / num_v_lines) * bottom_width - (bottom_width / 2) + cx
            
            # Line from (cx, cy) to (x_bottom, SCREEN_HEIGHT)
            # Fade out near horizon
            # Since we can't easily do gradient lines in pygame primitive, we draw full
            # Or we can draw segments.
            # Simple version: solid lines
            color = (40, 0, 60) # Dark Purple
            pygame.draw.line(surface, color, (cx, cy), (x_bottom, SCREEN_HEIGHT), 2)
            pygame.draw.line(surface, color, (cx, cy), (x_bottom, 0), 2) # Mirror top

        # Draw Horizontal Lines (Scanning)
        # Exponential spacing for depth illusion
        # y = horizon + (y_screen / z)
        
        # Simple version: Linear scrolling lines but mapped to perspective Y
        # We iterate "virtual z"
        num_h_lines = 15
        for i in range(num_h_lines):
            # Z moves from far (large) to near (small) or vice versa
            # Let's map normalized progress (0 to 1) to screen Y with curve
            
            # virtual_y goes from 0 (horizon) to 1 (bottom)
            # base offset
            base = (i * self.spacing + self.offset_y) 
            # normalized 0..TotalHeight
            max_depth = num_h_lines * self.spacing
            
            # Wrap around manually implemented by modulo in update, 
            # here we just draw visible set
            
            # Better approach:
            # We want lines at Z positions.
            # Z = 1 to 10
            # ScreenY = Horizon + Scale/Z
            pass

        # Simplified Grid (Top-Down 2D moving vertical, simpler for this view)
        # Since the game is 2D top-down abstract, a 3D perspective grid might clash 
        # with the 2D physics.
        # Let's do a scrolling 2D grid that pulses.
        
        cols = SCREEN_WIDTH // self.spacing + 2
        rows = SCREEN_HEIGHT // self.spacing + 2
        
        off_y = int(self.offset_y)
        
        color = (20, 20, 40)
        
        # Horizontals
        for r in range(rows):
            y = r * self.spacing + off_y - self.spacing
            if 0 <= y <= SCREEN_HEIGHT:
                pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y), 1)
                
        # Verticals
        for c in range(cols):
            x = c * self.spacing
            pygame.draw.line(surface, color, (x, 0), (x, SCREEN_HEIGHT), 1)

FONT_SMALL = None
FONT_LARGE = None

def get_fonts():
    global FONT_SMALL, FONT_LARGE
    if FONT_SMALL is None:
        FONT_SMALL = pygame.font.SysFont("Arial", 16, bold=True)
    if FONT_LARGE is None:
        FONT_LARGE = pygame.font.SysFont("Arial", 40, bold=True)
    return FONT_SMALL, FONT_LARGE
