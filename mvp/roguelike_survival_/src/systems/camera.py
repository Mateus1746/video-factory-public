import pygame
import random

class Camera:
    def __init__(self):
        self.shake_magnitude = 0
        self.offset = pygame.Vector2(0, 0)
        self.world_offset = pygame.Vector2(0, 0)
        
        # Zoom Logic
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.zoom_speed = 2.0

    def add_shake(self, amount):
        self.shake_magnitude = min(self.shake_magnitude + amount, 40)

    def set_zoom(self, level):
        self.target_zoom = level

    def follow(self, target_x, target_y, screen_w, screen_h):
        # Center target, but apply zoom factor
        # When zoomed in (zoom > 1), we need to adjust the center
        self.world_offset.x = (screen_w / 2) - (target_x * self.zoom)
        self.world_offset.y = (screen_h / 2) - (target_y * self.zoom)

    def update(self, dt):
        # Smooth Zoom
        self.zoom += (self.target_zoom - self.zoom) * self.zoom_speed * dt
        
        # Apply shake on top
        if self.shake_magnitude > 0:
            self.shake_magnitude = max(0, self.shake_magnitude - 30.0 * dt)
            shake_x = random.uniform(-self.shake_magnitude, self.shake_magnitude)
            shake_y = random.uniform(-self.shake_magnitude, self.shake_magnitude)
            self.offset.x = self.world_offset.x + shake_x
            self.offset.y = self.world_offset.y + shake_y
        else:
            self.offset.x = self.world_offset.x
            self.offset.y = self.world_offset.y

    def apply(self, x, y):
        """Transform world coordinates to screen coordinates with zoom."""
        return (int(x * self.zoom + self.offset.x), int(y * self.zoom + self.offset.y))
    
    def apply_scale(self, size):
        """Scale a size or radius based on zoom."""
        return int(size * self.zoom)
