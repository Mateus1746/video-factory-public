import pygame
import math
import random
from .base import Entity
from ..config import WHITE, CHAOS_JUMP_INTERVAL, CHAOS_PROJECTILE_SPEED, CHAOS_BASE_DAMAGE, CHAOS_COLOR

class ChaosJumper(Entity):
    NAME = "CHAOS JUMPER"
    COLOR = CHAOS_COLOR

    def __init__(self, center, rings, projectile_manager=None):
        super().__init__(center, rings, projectile_manager)
        self.x = center[0]
        self.y = center[1]
        self.jump_timer = 0.0
        self.jump_interval = CHAOS_JUMP_INTERVAL
        self.radius = 20
        self.color = CHAOS_COLOR
        self.r = 3.95
        self.lx = 0.5
        self.ly = 0.3

    def next_chaos(self):
        self.lx = self.r * self.lx * (1 - self.lx)
        self.ly = self.r * self.ly * (1 - self.ly)
        return self.lx, self.ly

    def update(self, dt):
        self.jump_timer -= dt
        
        # Local jumping (Visual Glitch at Base)
        if self.jump_timer <= 0:
            self.jump_timer = self.jump_interval
            cx, cy = self.next_chaos()
            angle = cy * 2 * math.pi
            # Jump around HOME base
            self.x = self.center[0] + math.cos(angle) * 50
            self.y = self.center[1] + math.sin(angle) * 50
            
            # Spawn Projectile targeting local rings
            if self.projectile_manager:
                alive_rings = [r for r in self.rings if r.alive]
                if alive_rings:
                    target_ring = random.choice(alive_rings)
                    # Target a random point ON the ring
                    angle_t = random.uniform(0, 2 * math.pi)
                    tx = target_ring.center[0] + math.cos(angle_t) * target_ring.radius
                    ty = target_ring.center[1] + math.sin(angle_t) * target_ring.radius

                    # Chaos Bomb
                    damage = CHAOS_BASE_DAMAGE + (cx * CHAOS_BASE_DAMAGE)
                    self.projectile_manager.add_projectile(
                        pos=[self.x, self.y],
                        target=[tx, ty],
                        speed=CHAOS_PROJECTILE_SPEED,
                        damage=damage,
                        color=self.color
                    )

    def draw(self, surface):
        # Draw Main Jumper
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        inner_r = int(self.radius * self.lx)
        if inner_r > 0:
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), inner_r, 1)