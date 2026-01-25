import pygame
import math
from abc import ABC, abstractmethod
from ..config import RING_THICKNESS, WHITE
from ..audio import generate_note_sound
from ..effects import get_fonts, generate_cracks, spawn_ring_explosion

class Entity(ABC):
    """Abstract base class for all simulation entities."""
    
    def __init__(self, center, rings, projectile_manager=None):
        self.center = center
        self.rings = rings
        self.projectile_manager = projectile_manager
    
    @abstractmethod
    def update(self, dt):
        """Update entity logic."""
        pass
        
    @abstractmethod
    def draw(self, surface):
        """Draw entity to surface."""
        pass

class Ring:
    def __init__(self, radius, hp, center, color, note_frequency=None, is_core=False):
        self.radius = radius
        self.hp = hp
        self.max_hp = hp
        self.center = center
        self.color = color
        self.alive = True
        self.flash_timer = 0.0
        self.note_frequency = note_frequency
        self.is_core = is_core
        self.damage_multiplier = 1.0 # Adaptive buff multiplier
        self.cracks = []
        self.crack_stages = [False, False, False] # 75%, 50%, 25%
        
    def take_damage(self, amount):
        if not self.alive: return
        self.hp -= amount * self.damage_multiplier
        self.flash_timer = 0.1
        if self.note_frequency:
            # Dynamic Pitch based on Damage (Shepard Tone Effect)
            # The lower the HP, the higher the pitch (tension)
            hp_factor = 1.0 + (1.0 - (self.hp / self.max_hp)) * 0.5
            freq = self.note_frequency * hp_factor
            generate_note_sound(freq).play()
            
        # Check Crack Thresholds
        pct = self.hp / self.max_hp
        if pct < 0.75 and not self.crack_stages[0]:
            self.crack_stages[0] = True
            self.cracks.extend(generate_cracks(self.radius, 3))
        if pct < 0.50 and not self.crack_stages[1]:
            self.crack_stages[1] = True
            self.cracks.extend(generate_cracks(self.radius, 5))
        if pct < 0.25 and not self.crack_stages[2]:
            self.crack_stages[2] = True
            self.cracks.extend(generate_cracks(self.radius, 8))

        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            # VISCERAL DESTRUCTION
            spawn_ring_explosion(self.center, self.radius, self.color, 50)
            if self.is_core:
                spawn_ring_explosion(self.center, self.radius, WHITE, 100) # Core explosion is massive
            
    def update_visuals(self, dt):
        if self.flash_timer > 0:
            self.flash_timer -= dt
            
    def draw(self, surface):
        if not self.alive: return
        
        draw_color = self.color
        thickness = RING_THICKNESS
        
        if self.is_core:
            # Draw CORE indicator (Pulsing or distinct border)
            pygame.draw.circle(surface, (255, 0, 0), self.center, self.radius + 12, 2)
            pygame.draw.circle(surface, (255, 0, 0), self.center, self.radius - 8, 2)
        
        if self.flash_timer > 0:
            draw_color = WHITE
            thickness += 4
            pygame.draw.circle(surface, (self.color[0]//2, self.color[1]//2, self.color[2]//2), self.center, self.radius + 6, 4)

        pygame.draw.circle(surface, draw_color, self.center, self.radius, thickness)
        
        # Draw Cracks
        for crack in self.cracks:
            # Shift crack points by center
            pts = [(p[0] + self.center[0], p[1] + self.center[1]) for p in crack]
            if len(pts) > 1:
                pygame.draw.lines(surface, (20, 20, 30), False, pts, 2)
        
        font_s, _ = get_fonts()
        hp_str = f"{int(self.hp):,}"
        text = font_s.render(hp_str, True, WHITE)
        shadow = font_s.render(hp_str, True, (10, 10, 10))
        text_pos = (self.center[0] - text.get_width()//2, self.center[1] - self.radius - 25)
        
        surface.blit(shadow, (text_pos[0]+2, text_pos[1]+2))
        surface.blit(text, text_pos)
        
        if self.is_core:
            core_lbl = font_s.render("CORE", True, (255, 50, 50))
            surface.blit(core_lbl, (self.center[0] - core_lbl.get_width()//2, self.center[1] - self.radius + 10))
