import pygame
import math
from .base import Entity
from ..config import WHITE, STRIKER_RADIUS, STRIKER_SPEED, STRIKER_FIRE_RATE, STRIKER_PROJ_SPEED, STRIKER_DAMAGE, STRIKER_COLOR
from ..audio import generate_note_sound
from ..effects import spawn_particles

class OrbitStriker(Entity):
    NAME = "ORBIT STRIKER"
    COLOR = STRIKER_COLOR
    
    def __init__(self, center, rings, projectile_manager=None):
        super().__init__(center, rings, projectile_manager)
        self.angle = 0.0
        self.radius = STRIKER_RADIUS
        self.speed = STRIKER_SPEED
        self.fire_timer = 0.0
        self.fire_rate = STRIKER_FIRE_RATE
        self.color = STRIKER_COLOR
        
    def update(self, dt):
        self.angle += self.speed * dt
        self.fire_timer -= dt
        
        orbiter_x = self.center[0] + math.cos(self.angle) * self.radius
        orbiter_y = self.center[1] + math.sin(self.angle) * self.radius
        
        # Fire
        if self.fire_timer <= 0:
            self.fire_timer = self.fire_rate
            # Shoot towards center
            dx = self.center[0] - orbiter_x
            dy = self.center[1] - orbiter_y
            dist = math.hypot(dx, dy)
            # Use ProjectileManager if available, otherwise local logic (removed)
            # To strictly follow the pattern, I should use ProjectileManager.
            # But the original logic had specialized hit logic (check rings).
            # ProjectileManager has generic hit logic.
            # I will adapt to use ProjectileManager which simplifies this significantly.
            
            if self.projectile_manager:
                 # ProjectileManager handles movement and collision
                 self.projectile_manager.add_projectile(
                    pos=[orbiter_x, orbiter_y],
                    target=[self.center[0], self.center[1]], # Target center
                    speed=STRIKER_PROJ_SPEED,
                    damage=STRIKER_DAMAGE,
                    color=WHITE,
                    collision_mode='continuous'
                )

    def draw(self, surface):
        # Draw Orbiter
        orbiter_x = self.center[0] + math.cos(self.angle) * self.radius
        orbiter_y = self.center[1] + math.sin(self.angle) * self.radius
        
        pygame.draw.circle(surface, self.color, (int(orbiter_x), int(orbiter_y)), 15)
