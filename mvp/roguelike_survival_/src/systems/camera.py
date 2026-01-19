import pygame
import random

class Camera:
    def __init__(self):
        self.shake_magnitude = 0
        self.offset = pygame.Vector2(0, 0)
        self.world_offset = pygame.Vector2(0, 0)

    def add_shake(self, amount):
        self.shake_magnitude = min(self.shake_magnitude + amount, 40)

    def follow(self, target_x, target_y, screen_w, screen_h):
        # Calculate where the camera should be to center the player
        # world_offset is used to transform world coordinates to screen coordinates
        self.world_offset.x = (screen_w / 2) - target_x
        self.world_offset.y = (screen_h / 2) - target_y

    def update(self, dt):
        # Apply shake on top of world offset
        if self.shake_magnitude > 0:
            self.shake_magnitude = max(0, self.shake_magnitude - 30.0 * dt)
            shake_x = random.uniform(-self.shake_magnitude, self.shake_magnitude)
            shake_y = random.uniform(-self.shake_magnitude, self.shake_magnitude)
            self.offset.x = self.world_offset.x + shake_x
            self.offset.y = self.world_offset.y + shake_y
        else:
            self.offset.x = self.world_offset.x
            self.offset.y = self.world_offset.y