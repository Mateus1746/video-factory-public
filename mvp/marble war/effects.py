"""
Visual effects system for Marble War.
Includes power-ups, explosions, and particle systems.
"""

import math
import random
from typing import Dict, List, Optional, Tuple

import pygame

import config
from game_types import Color, Particle, Position



# ============================================================================
# POWER-UPS
# ============================================================================

class PowerUp:
    """Power-up collectible with visual effects."""
    
    COLOR_MAP: Dict[str, Color] = {
        "speed": (255, 100, 0),
        "size": (200, 0, 255),
        "clone": (0, 255, 200),
        "assassin": (255, 0, 0),
    }
    
    def __init__(self, x: float, y: float, type: str) -> None:
        self.position = pygame.Vector2(x, y)
        self.type = type
        self.radius = config.POWERUP_RADIUS
        self.color = self.COLOR_MAP.get(type, (255, 255, 255))

    def draw(self, screen: pygame.Surface, images: Dict[str, pygame.Surface]) -> None:
        """Draw power-up with pulsing animation."""
        # Pulsing effect
        t = pygame.time.get_ticks() / 500.0
        r_pulse = self.radius + math.sin(t) * 5
        
        # Outer ring
        center = (int(self.position.x), int(self.position.y))
        pygame.draw.circle(screen, self.color, center, int(r_pulse), 2)
        
        # Draw icon or fallback
        if self.type in images:
            img = images[self.type]
            screen.blit(img, (center[0] - self.radius, center[1] - self.radius))
        else:
            self._draw_fallback_icon(screen, center)
    
    def _draw_fallback_icon(self, screen: pygame.Surface, center: Position) -> None:
        """Draw fallback icon if image not available."""
        cx, cy = center
        
        if self.type == "speed":
            # Wing boot icon
            pygame.draw.rect(screen, self.color, (cx - 10, cy, 20, 10))
            pygame.draw.rect(screen, self.color, (cx + 5, cy, 10, 15))
            pygame.draw.polygon(screen, (255, 255, 255), 
                              [(cx-10, cy+2), (cx-25, cy-8), (cx-10, cy-5)])
            pygame.draw.polygon(screen, (255, 255, 255), 
                              [(cx-10, cy+5), (cx-20, cy+0), (cx-10, cy+8)])
        elif self.type == "clone":
            font = pygame.font.SysFont("Arial", 30, bold=True)
            txt = font.render("X2", True, self.color)
            screen.blit(txt, (cx - txt.get_width()//2, cy - txt.get_height()//2))
        elif self.type == "assassin":
            pygame.draw.rect(screen, self.color, (cx - 15, cy - 5, 30, 10))
            pygame.draw.rect(screen, self.color, (cx - 15, cy - 5, 10, 20))
        elif self.type == "size":
            pygame.draw.rect(screen, self.color, (cx - 12, cy - 15, 24, 15))
            pygame.draw.rect(screen, (150, 75, 0), (cx - 5, cy, 10, 20))


# ============================================================================
# EXPLOSIONS
# ============================================================================

class Explosion:
    """Visual explosion effect."""
    
    DURATION = 0.5  # seconds
    
    def __init__(self, x: float, y: float, image: pygame.Surface) -> None:
        self.pos = pygame.Vector2(x, y)
        self.image = image
        self.life = self.DURATION
        self.alpha = 255

    def update(self) -> bool:
        """Update explosion. Returns True if still visible."""
        self.life -= config.TIMESTEP
        self.alpha = int(max(0, (self.life / self.DURATION) * 255))
        return self.life > 0

    def draw(self, screen: pygame.Surface) -> None:
        """Draw fading explosion."""
        img_copy = self.image.copy()
        img_copy.fill((255, 255, 255, self.alpha), special_flags=pygame.BLEND_RGBA_MULT)
        rect = img_copy.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        screen.blit(img_copy, rect)


# ============================================================================
# PARTICLE SYSTEM
# ============================================================================

class ParticleSystem:
    """Optimized particle system with object pooling."""
    
    PARTICLE_COUNT = 8
    PARTICLE_SPEED_MIN = 2
    PARTICLE_SPEED_MAX = 6
    FADE_RATE = 0.05
    PARTICLE_SIZE = 4
    
    def __init__(self) -> None:
        self.particles: List[Particle] = []
        # Pre-create surface for particles (reusable)
        self._particle_surface = pygame.Surface(
            (self.PARTICLE_SIZE, self.PARTICLE_SIZE), 
            pygame.SRCALPHA
        )

    def emit(self, pos: Tuple[float, float], color: Color) -> None:
        """Emit particle burst."""
        for _ in range(self.PARTICLE_COUNT):
            angle = random.uniform(0, math.tau)  # tau = 2*pi
            speed = random.uniform(self.PARTICLE_SPEED_MIN, self.PARTICLE_SPEED_MAX)
            vel = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            self.particles.append(Particle(
                pos=pygame.Vector2(pos),
                vel=vel,
                color=color
            ))

    def update(self) -> None:
        """Update all particles (vectorized removal)."""
        for p in self.particles:
            p.pos += p.vel
            p.life -= self.FADE_RATE
        
        # Remove dead particles in one pass
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, screen: pygame.Surface) -> None:
        """Draw all particles efficiently."""
        for p in self.particles:
            alpha = int(p.life * 255)
            self._particle_surface.fill((0, 0, 0, 0))  # Clear
            pygame.draw.circle(
                self._particle_surface, 
                (*p.color[:3], alpha), 
                (self.PARTICLE_SIZE // 2, self.PARTICLE_SIZE // 2), 
                self.PARTICLE_SIZE // 2
            )
            screen.blit(
                self._particle_surface, 
                (int(p.pos.x - self.PARTICLE_SIZE // 2), 
                 int(p.pos.y - self.PARTICLE_SIZE // 2))
            )
