"""
Game entities for Marble War.
Includes Marble and Projectile classes.
"""

import math
import random

import pymunk

import config
from game_types import Color



# ============================================================================
# PROJECTILE
# ============================================================================

class Projectile:
    """Bullet fired by marbles in assassin mode."""
    
    def __init__(self, x: float, y: float, angle: float, team: str, 
                 color: Color, space: pymunk.Space) -> None:
        self.team = team
        self.color = color
        self.radius = config.PROJECTILE_RADIUS
        self.life = config.PROJECTILE_LIFETIME
        
        # Physics body
        mass = 0.5
        moment = pymunk.moment_for_circle(mass, 0, self.radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = x, y
        
        # Initial velocity
        vx = math.cos(angle) * config.PROJECTILE_SPEED
        vy = math.sin(angle) * config.PROJECTILE_SPEED
        self.body.velocity = (vx, vy)
        
        # Collision shape (sensor - no physical collision)
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.collision_type = 2
        self.shape.sensor = True
        self.shape.data = self
        
        space.add(self.body, self.shape)

    def update(self) -> bool:
        """Update projectile lifetime. Returns True if still alive."""
        self.life -= config.TIMESTEP
        return self.life > 0

    def draw(self, screen, image=None) -> None:
        """Draw projectile as simple black ball."""
        import pygame
        pos = (int(self.body.position.x), int(self.body.position.y))
        pygame.draw.circle(screen, (0, 0, 0), pos, self.radius)
        pygame.draw.circle(screen, (50, 50, 50), pos, self.radius, 1)


# ============================================================================
# MARBLE
# ============================================================================

class Marble:
    """Playable marble with AI and power-ups."""
    
    def __init__(self, x: float, y: float, team: str, color: Color, 
                 space: pymunk.Space) -> None:
        self.team = team
        self.color = color
        
        # Physics setup
        mass = 1
        radius = config.MARBLE_RADIUS
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = x, y
        
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 1.0
        self.shape.friction = 0.1
        self.shape.collision_type = 1
        self.shape.data = self
        
        # Power-up states
        self.speed_boost: float = 1.0
        self.brush_multiplier: int = 1
        self.assassin_mode: bool = False
        self.powerup_timer: float = 0.0
        self.shoot_timer: float = 0.0
        self.ammo: int = 0
        self.face_timer: float = 0.0
        self.current_face: str = "bravo"
        
        space.add(self.body, self.shape)

    def apply_ai_force(self) -> bool:
        """
        Apply random force for chaotic movement.
        Returns True if marble should shoot.
        """
        # Random force
        strength = 2500 * self.speed_boost
        angle = random.uniform(0, math.tau)
        force = (math.cos(angle) * strength, math.sin(angle) * strength)
        self.body.apply_force_at_local_point(force)
        
        # Update timers
        if self.powerup_timer > 0:
            self.powerup_timer -= config.TIMESTEP
            if self.powerup_timer <= 0:
                self._reset_powerups()
        
        if self.face_timer > 0:
            self.face_timer -= config.TIMESTEP
        
        # Shooting logic
        should_shoot = False
        if self.assassin_mode and self.ammo > 0:
            self.shoot_timer -= config.TIMESTEP
            if self.shoot_timer <= 0:
                self.shoot_timer = config.ASSASSIN_FIRE_RATE
                self.ammo -= 1
                should_shoot = True
        
        return should_shoot
    
    def _reset_powerups(self) -> None:
        """Reset all power-up effects."""
        self.speed_boost = 1.0
        self.brush_multiplier = 1
        self.assassin_mode = False
        self.ammo = 0
