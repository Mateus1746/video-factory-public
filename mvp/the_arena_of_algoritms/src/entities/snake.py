import pygame
import math
import random
from .base import Entity
from ..config import WHITE, SNAKE_SPEED, SNAKE_DAMAGE, SNAKE_COLOR

class SnakeEater(Entity):
    NAME = "SNAKE EATER"
    COLOR = SNAKE_COLOR

    def __init__(self, center, rings, projectile_manager=None):
        super().__init__(center, rings, projectile_manager)
        self.segments = []
        self.num_segments = 25
        self.head_pos = [center[0], center[1]]
        self.angle = 0.0
        self.speed = SNAKE_SPEED
        self.color = SNAKE_COLOR
        self.target_ring = None
        self.change_target_timer = 0.0
        
        # Init segments at center
        for _ in range(self.num_segments):
            self.segments.append([center[0], center[1]])
            
    def update(self, dt):
        self.change_target_timer -= dt
        
        # AI: Pick target ring
        if not self.target_ring or not self.target_ring.alive or self.change_target_timer <= 0:
            alive_rings = [r for r in self.rings if r.alive]
            if alive_rings:
                # Prioritize closest or random? Random is fine for chaos.
                self.target_ring = random.choice(alive_rings)
                self.change_target_timer = 1.5 # Switch faster if stuck
            else:
                self.target_ring = None
        
        # Move Head
        if self.target_ring:
            # Improved Logic: Orbit the ring by leading the current angle
            # Find angle from center to snake head
            dx_curr = self.head_pos[0] - self.center[0]
            dy_curr = self.head_pos[1] - self.center[1]
            current_angle = math.atan2(dy_curr, dx_curr)
            
            # Target is a point slightly ahead on the ring (Counter-Clockwise)
            # Reduced lead angle for tighter tracking (less chord cutting error)
            target_angle = current_angle + 0.2 
            
            tx = self.center[0] + math.cos(target_angle) * self.target_ring.radius
            ty = self.center[1] + math.sin(target_angle) * self.target_ring.radius
            
            # Move towards that leading point
            dx = tx - self.head_pos[0]
            dy = ty - self.head_pos[1]
            dist_to_target = math.hypot(dx, dy)
            
            # Normalize and move
            if dist_to_target > 0:
                self.head_pos[0] += (dx / dist_to_target) * self.speed * dt
                self.head_pos[1] += (dy / dist_to_target) * self.speed * dt
            
            # Damage on contact (relaxed distance check)
            dist_from_center = math.hypot(self.head_pos[0] - self.center[0], self.head_pos[1] - self.center[1])
            # Increased hitbox from 30 to 50 to ensure contact even if drifting slightly
            if abs(dist_from_center - self.target_ring.radius) < 50: 
                self.target_ring.take_damage(SNAKE_DAMAGE * dt)
        else:
            # Idle circle - Only happens if NO target_ring selected
            # Sanity check: If we are here, but rings exist, something is wrong.
            alive_check = [r for r in self.rings if r.alive]
            if alive_check:
                 # Force retarget immediately if we drifted into idle by mistake
                 self.target_ring = random.choice(alive_check)
            else:
                self.angle += 2.0 * dt
                self.head_pos[0] = self.center[0] + math.cos(self.angle) * 100
                self.head_pos[1] = self.center[1] + math.sin(self.angle) * 100

        # Update Body (Inverse Kinematics / Follow Leader)
        spacing = 15
        target = self.head_pos
        for i in range(self.num_segments):
            seg = self.segments[i]
            dx = target[0] - seg[0]
            dy = target[1] - seg[1]
            dist = math.hypot(dx, dy)
            if dist > spacing:
                ratio = (dist - spacing) / dist
                seg[0] += dx * ratio
                seg[1] += dy * ratio
            target = seg

    def draw(self, surface):
        if len(self.segments) < 2: return
        # Draw body
        points = [self.head_pos] + self.segments
        pygame.draw.lines(surface, self.color, False, points, 14)
        pygame.draw.lines(surface, (0, 100, 0), False, points, 6)
        
        # Head
        pygame.draw.circle(surface, WHITE, (int(self.head_pos[0]), int(self.head_pos[1])), 8)
