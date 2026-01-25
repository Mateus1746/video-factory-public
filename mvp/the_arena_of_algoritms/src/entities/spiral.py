import pygame
import math
import random
from .base import Entity
from ..config import GOLDEN_ANGLE, FIB_SPEED, SPIRAL_RADIUS, FIB_DAMAGE, YELLOW

class FibonacciSpiral(Entity):
    NAME = "FIBONACCI SPIRAL"
    COLOR = YELLOW

    def __init__(self, center, rings, projectile_manager=None):
        super().__init__(center, rings, projectile_manager)
        self.x = float(center[0])
        self.y = float(center[1])
        self.n = 1
        self.fib_prev = 0
        self.fib_curr = 1
        self.angle = 0.0
        self.fire_timer = 0.0
        self.vx = 0
        self.vy = 0
        self.set_next_target()

    def get_next_fib(self):
        nxt = self.fib_prev + self.fib_curr
        self.fib_prev = self.fib_curr
        self.fib_curr = nxt
        if self.fib_curr > 1000:
            self.fib_prev = 0
            self.fib_curr = 1
        return self.fib_curr

    def set_next_target(self):
        self.n += 1
        # Spin locally
        self.angle = self.n * GOLDEN_ANGLE
        # Local visual movement (Orbiting center)
        self.vx = math.cos(self.angle) * 20
        self.vy = math.sin(self.angle) * 20

    def update(self, dt):
        # Local Spin Animation
        self.x = self.center[0] + self.vx
        self.y = self.center[1] + self.vy
        
        # Fire Projectiles (Fibonacci Shards)
        self.fire_timer -= dt
        if self.fire_timer <= 0:
            self.fire_timer = 0.1
            self.set_next_target() # Advance pattern
            
            # Fire at random enemy ring
            if self.rings and self.projectile_manager:
                active = [r for r in self.rings if r.alive]
                if active:
                    target = random.choice(active)
                    # Target circumference
                    angle_t = random.uniform(0, 2 * math.pi)
                    tx = target.center[0] + math.cos(angle_t) * target.radius
                    ty = target.center[1] + math.sin(angle_t) * target.radius
                    
                    self.projectile_manager.add_projectile(
                        pos=[self.x, self.y],
                        target=[tx, ty],
                        speed=700,
                        damage=FIB_DAMAGE,
                        color=YELLOW
                    )

    def draw(self, surface):
        # Draw Base
        from ..effects import create_glow_surface
        pos = (int(self.x), int(self.y))
        glow = create_glow_surface(SPIRAL_RADIUS, YELLOW)
        surface.blit(glow, (pos[0] - glow.get_width()//2, pos[1] - glow.get_height()//2), special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(surface, YELLOW, pos, SPIRAL_RADIUS)