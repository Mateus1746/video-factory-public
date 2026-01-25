import pygame
import math
from src.config import *

class HUD:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pulse = 0.0
        try:
            self.font_main = pygame.font.SysFont("consolas", int(40 * (width/1080)), bold=True)
            self.font_big = pygame.font.SysFont("consolas", int(100 * (width/1080)), bold=True)
            self.font_small = pygame.font.SysFont("consolas", int(28 * (width/1080)), bold=True)
        except:
            self.font_main = pygame.font.Font(None, 40)
            self.font_big = pygame.font.Font(None, 100)
            self.font_small = pygame.font.Font(None, 28)

    def draw(self, surface, gm, player, corner_time, victory, game_over):
        dt = 1.0/60.0 # Approximate
        self.pulse += 5.0 * dt
        
        # 1. XP Bar (Top)
        xp_h = 20
        pygame.draw.rect(surface, (10, 10, 20), (0, 0, self.width, xp_h))
        xp_ratio = gm.xp / gm.max_xp
        pygame.draw.rect(surface, COLOR_XP, (0, 0, self.width * xp_ratio, xp_h))
        # XP Glow line
        pygame.draw.line(surface, (255, 255, 255), (0, xp_h), (self.width * xp_ratio, xp_h), 2)
        
        # 2. Stats
        lvl_txt = self.font_main.render(f"LEVEL {gm.level}", True, COLOR_TEXT)
        surface.blit(lvl_txt, (30, 40))

        # Boss Progress Bar (Subtle)
        boss_progress = min(1.0, gm.time_elapsed / EVENT_BOSS_TIME)
        if not gm.boss_spawned:
            bar_w = 400
            bx = (self.width - bar_w) // 2
            pygame.draw.rect(surface, (20, 20, 40), (bx, 50, bar_w, 10), border_radius=5)
            pygame.draw.rect(surface, (255, 50, 50), (bx, 50, bar_w * boss_progress, 10), border_radius=5)
            boss_lbl = self.font_small.render("BOSS APPROACHING", True, (255, 100, 100))
            surface.blit(boss_lbl, (self.width//2 - boss_lbl.get_width()//2, 65))

        m, s = divmod(int(gm.time_elapsed), 60)
        timer_txt = self.font_main.render(f"{m:02d}:{s:02d}", True, COLOR_TEXT)
        kill_txt = self.font_main.render(f"{gm.kills} KILLS", True, COLOR_ENEMY_COMMON)
        surface.blit(timer_txt, (self.width - 150, 40))
        surface.blit(kill_txt, (self.width - 180, 85))

        # 3. Health Bar (Bottom)
        is_low = player.health < 30
        pulse_val = math.sin(self.pulse * 2) * 10 if is_low else 0
        
        bar_w, bar_h = 700, 45
        bx, by = (self.width - bar_w)//2, self.height - 100
        
        # Health Glow when low
        if is_low:
             glow_surf = pygame.Surface((bar_w + 40, bar_h + 40), pygame.SRCALPHA)
             pygame.draw.rect(glow_surf, (255, 0, 0, 50 + int(pulse_val * 5)), (0, 0, bar_w+40, bar_h+40), border_radius=20)
             surface.blit(glow_surf, (bx-20, by-20), special_flags=pygame.BLEND_ADD)

        pygame.draw.rect(surface, (10, 10, 20), (bx-4, by-4, bar_w+8, bar_h+8), border_radius=15)
        pygame.draw.rect(surface, (40, 0, 0), (bx, by, bar_w, bar_h), border_radius=10)
        
        hp_ratio = max(0, player.health / player.max_health)
        hp_color = (0, 255, 100) if not is_low else (255, 50, 50)
        pygame.draw.rect(surface, hp_color, (bx, by, bar_w * hp_ratio, bar_h), border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), (bx, by, bar_w, bar_h), 2, border_radius=10)
        
        hp_val_txt = self.font_small.render(f"INTEGRITY: {int(hp_ratio*100)}%", True, COLOR_TEXT)
        surface.blit(hp_val_txt, (bx + bar_w//2 - hp_val_txt.get_width()//2, by + 8))

        # 4. Warnings
        if corner_time > 3.0:
            warn_color = (255, 50, 50) if int(self.pulse * 2) % 2 == 0 else (255, 255, 255)
            warn = self.font_big.render("OUT OF BOUNDS!", True, warn_color)
            surface.blit(warn, (self.width//2 - warn.get_width()//2, 250))

        if victory:
            self._draw_overlay(surface, "MISSION ACCOMPLISHED", (0, 255, 255))
        elif game_over:
            self._draw_overlay(surface, "SYSTEM CRITICAL: FAILED", (255, 0, 0))

    def _draw_overlay(self, surface, message, color):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) # Darken background
        surface.blit(overlay, (0,0))
        
        # Glow Effect for victory/defeat text
        txt = self.font_big.render(message, True, COLOR_TEXT)
        rect = txt.get_rect(center=(self.width/2, self.height/2))
        
        for i in range(8):
             glow = self.font_big.render(message, True, color)
             glow.set_alpha(100 - i*10)
             surface.blit(glow, (rect.x - i, rect.y), special_flags=pygame.BLEND_ADD)
             surface.blit(glow, (rect.x + i, rect.y), special_flags=pygame.BLEND_ADD)
        
        surface.blit(txt, rect)