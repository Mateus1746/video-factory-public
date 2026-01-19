import pygame
import math
import random
from ..config import WHITE
from ..audio import generate_note_sound
from ..effects import spawn_particles

class TeslaStorm:
    """
    Tesla Storm uses Recursive Midpoint Displacement (Fractal logic)
    to generate jagged lightning arcs between targets.
    """
    def __init__(self, center, rings):
        self.center = center
        self.rings = rings
        self.timer = 0.0
        self.interval = 0.15 # Faster strikes
        self.arcs = []
        self.color = (200, 200, 255) # Electric Blue-White
        
    def update(self, dt):
        self.timer -= dt
        # Fade arcs
        self.arcs = [(pts, life - dt) for pts, life in self.arcs if life > 0]
        
        if self.timer <= 0:
            self.timer = self.interval
            active_rings = [r for r in self.rings if r.alive]
            if active_rings:
                # Target the rings
                targets = random.sample(active_rings, k=min(len(active_rings), 2))
                
                # Start from HOME center
                prev_point = self.center
                for ring in targets:
                    angle = random.uniform(0, 2 * math.pi)
                    # Target point is on the RING
                    rx = ring.center[0] + math.cos(angle) * ring.radius
                    ry = ring.center[1] + math.sin(angle) * ring.radius
                    target_point = (rx, ry)
                    
                    # Generate fractal lightning connecting Home/Prev to Target
                    points = []
                    self.generate_fractal_lightning(prev_point, target_point, 50, points)
                    # Add start and end
                    points = [prev_point] + points + [target_point]
                    
                    self.arcs.append((points, 0.12))
                    
                    ring.take_damage(9500) # Balanced (was 12000)
                    if ring.note_frequency:
                        generate_note_sound(ring.note_frequency, 0.05).play()
                    spawn_particles(rx, ry, self.color, 10)
                    # Chain lightning (optional, but let's reset to center for next arc to look like a source)
                    # prev_point = target_point # Chaining
                    prev_point = self.center # Radial burst looks better for "Base vs Base"

    def generate_fractal_lightning(self, start, end, displace, points):
        """Recursive Midpoint Displacement"""
        dist = math.hypot(end[0] - start[0], end[1] - start[1])
        if dist < 10:
            return
            
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        
        # Displace midpoint perpendicularly
        mid_x += (random.random() - 0.5) * displace
        mid_y += (random.random() - 0.5) * displace
        
        # We need to keep points in order, so this recursive structure is simplified:
        # For a real implementation we'd use a more robust sorting or tree,
        # but for visual effect, simple subdivision works.
        self.generate_fractal_lightning(start, (mid_x, mid_y), displace / 2, points)
        points.append((mid_x, mid_y))
        self.generate_fractal_lightning((mid_x, mid_y), end, displace / 2, points)

    def draw(self, surface):
        for points, life in self.arcs:
            if len(points) < 2: continue
            # Glow effect with multiple lines
            pygame.draw.lines(surface, self.color, False, points, 4)
            pygame.draw.lines(surface, WHITE, False, points, 1)