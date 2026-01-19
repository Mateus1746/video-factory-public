import pygame
import math
import random
from ..config import WHITE
from ..audio import generate_note_sound
from ..effects import create_glow_surface, spawn_particles

class LaserSweeper:
    def __init__(self, center, rings):
        self.center = center
        self.rings = rings
        self.x_offset = 0
        self.direction = 1
        self.speed = 300
        self.color = (50, 255, 255) 
        self.damage_per_sec = 35000 # Increased damage (+25%) 
        self.width = 10 
        self.max_scan = 350

    def update(self, dt):
        if not self.rings: return
        
        # Scan X axis locally
        self.x_offset += self.speed * self.direction * dt
        if self.x_offset > self.max_scan:
            self.direction = -1
            self.x_offset = self.max_scan
        elif self.x_offset < -self.max_scan:
            self.direction = 1
            self.x_offset = -self.max_scan
            
        laser_x = self.center[0] + self.x_offset
        
        # Fire Vertical Beam to Enemy Y
        # Check intersection with rings
        for ring in self.rings:
            if not ring.alive: continue
            
            # The beam is a vertical line at laser_x
            # A ring is a circle at ring.center with radius r
            # Intersection if |laser_x - ring.center.x| < r
            dist_x = abs(laser_x - ring.center[0])
            
            if dist_x < ring.radius:
                # Beam hits the ring (two points usually, top and bottom arc)
                ring.take_damage(self.damage_per_sec * dt)
                
                if random.random() < 0.3 and ring.note_frequency:
                    generate_note_sound(ring.note_frequency, 0.05).play()
                    
                # Visual particles at intersection (Vertical line vs Circle)
                # y = sqrt(r^2 - x^2) + cy
                dy = math.sqrt(ring.radius**2 - dist_x**2)
                spawn_particles(laser_x, ring.center[1] + dy, self.color, 1)
                spawn_particles(laser_x, ring.center[1] - dy, self.color, 1)

    def draw(self, surface):
        laser_x = int(self.center[0] + self.x_offset)
        
        # Draw Emitter at Home
        pygame.draw.rect(surface, self.color, (laser_x - 10, self.center[1] - 10, 20, 20))
        
        # Draw Beam
        if self.rings:
            from ..config import HALF_HEIGHT, SCREEN_HEIGHT
            
            # Determine Territory Boundaries based on center
            if self.center[1] < HALF_HEIGHT:
                # Top Territory
                min_y = 0
                max_y = HALF_HEIGHT
            else:
                # Bot Territory
                min_y = HALF_HEIGHT
                max_y = SCREEN_HEIGHT

            # Draw vertical beam spanning the territory (or reasonable range)
            # We want it to look like it's scanning the rings.
            # Rings are centered at self.center.
            # Draw from center - 400 to center + 400, but clamped.
            
            y1 = max(min_y, self.center[1] - 400)
            y2 = min(max_y, self.center[1] + 400)
            
            pygame.draw.line(surface, self.color, (laser_x, y1), (laser_x, y2), 4)
            pygame.draw.line(surface, WHITE, (laser_x, y1), (laser_x, y2), 1)
