import pygame
from ..config import RING_THICKNESS, WHITE
from ..audio import generate_note_sound
from ..effects import get_fonts

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
        
    def take_damage(self, amount):
        if not self.alive: return
        self.hp -= amount * self.damage_multiplier
        self.flash_timer = 0.1
        if self.note_frequency:
            generate_note_sound(self.note_frequency).play()
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            
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
