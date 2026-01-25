import pygame
import random
from src.config import COLOR_TEXT

class FloatingText:
    def __init__(self, x, y, text, color=COLOR_TEXT, size=40, duration=1.0):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.duration = duration
        self.life = duration
        self.vy = -100 
        self.vx = random.uniform(-20, 20)
        self.size = size

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

class EffectsManager:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.floating_texts = []
        self.flash_alpha = 0
        self.flash_color = (255, 255, 255)
        self.chromatic_offset = 0
        
        # Pre-render Vignette mask correctly
        # We use a radial gradient that is transparent in the center and black at edges
        self.vignette = pygame.Surface((width, height), pygame.SRCALPHA)
        center = (width // 2, height // 2)
        max_dist = math.sqrt(center[0]**2 + center[1]**2)
        
        # Draw concentric circles with increasing alpha towards the edges
        for r in range(int(max_dist), 0, -10):
            alpha = int(min(200, (r / max_dist) ** 3 * 255))
            if alpha > 0:
                pygame.draw.circle(self.vignette, (0, 0, 0, alpha), center, r)
        
        try:
            self.font = pygame.font.SysFont("consolas", 40, bold=True)
        except:
            self.font = pygame.font.Font(None, 40)

    def add_floating_text(self, x, y, text, color=COLOR_TEXT, size=40):
        self.floating_texts.append(FloatingText(x, y, text, color, size))

    def screen_flash(self, color=(255, 255, 255), duration=0.2):
        self.flash_alpha = 150
        self.flash_color = color
        self.chromatic_offset = 12 

    def update(self, dt):
        self.floating_texts = [t for t in self.floating_texts if t.life > 0]
        for t in self.floating_texts:
            t.update(dt)
        
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - 500 * dt)
        
        if self.chromatic_offset > 0:
            self.chromatic_offset = max(0, self.chromatic_offset - 40 * dt)

    def draw_world_effects(self, surface, camera):
        for t in self.floating_texts:
            alpha = int(255 * (t.life / t.duration))
            text_surf = self.font.render(t.text, True, t.color)
            text_surf.set_alpha(alpha)
            pos = camera.apply(t.x, t.y)
            surface.blit(text_surf, (pos[0] - text_surf.get_width()//2, pos[1]))

    def draw_screen_effects(self, surface):
        # 1. Vignette (Normal alpha blending is safer than BLEND_MULT here)
        surface.blit(self.vignette, (0, 0))
        
        # 2. Screen Flash
        if self.flash_alpha > 0:
            flash_surf = pygame.Surface((self.width, self.height))
            flash_surf.fill(self.flash_color)
            flash_surf.set_alpha(int(self.flash_alpha))
            surface.blit(flash_surf, (0, 0))

    def apply_chromatic_aberration(self, surface):
        """Cheap chromatic aberration: only offset if offset is significant."""
        if self.chromatic_offset < 2: return
        
        off = int(self.chromatic_offset)
        # Avoid direct array manipulation if it's too buggy, 
        # instead blit the surface itself with offsets
        temp = surface.copy()
        surface.blit(temp, (off, 0), special_flags=pygame.BLEND_ADD) # Simplified effect
import math # Needed for vignette calculation
