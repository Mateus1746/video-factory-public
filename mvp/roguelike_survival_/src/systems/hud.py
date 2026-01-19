import pygame
from src.config import *

class HUD:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        try:
            self.font_main = pygame.font.SysFont("consolas", int(40 * (width/1080)), bold=True)
            self.font_big = pygame.font.SysFont("consolas", int(80 * (width/1080)), bold=True)
            self.font_small = pygame.font.SysFont("consolas", int(28 * (width/1080)), bold=True)
        except:
            self.font_main = pygame.font.Font(None, 40)
            self.font_big = pygame.font.Font(None, 80)
            self.font_small = pygame.font.Font(None, 28)

    def draw(self, surface, gm, player, corner_time, victory, game_over):
        # 1. XP Bar (Top)
        xp_h = 15
        pygame.draw.rect(surface, (20, 20, 30), (0, 0, self.width, xp_h))
        xp_ratio = gm.xp / gm.max_xp
        pygame.draw.rect(surface, COLOR_XP, (0, 0, self.width * xp_ratio, xp_h))
        
        # 2. Stats
        lvl_txt = self.font_main.render(f"LVL {gm.level}", True, COLOR_TEXT)
        surface.blit(lvl_txt, (20, 30))

        m, s = divmod(int(gm.time_elapsed), 60)
        timer_txt = self.font_main.render(f"{m:02d}:{s:02d}", True, COLOR_TEXT)
        kill_txt = self.font_main.render(f"KILLS {gm.kills}", True, COLOR_ENEMY_COMMON)
        surface.blit(timer_txt, (self.width - 150, 30))
        surface.blit(kill_txt, (self.width - 250, 75))

        # 3. Health Bar (Bottom)
        bar_w, bar_h = 600, 35
        bx, by = (self.width - bar_w)//2, self.height - 80
        pygame.draw.rect(surface, (10, 10, 20), (bx-4, by-4, bar_w+8, bar_h+8), border_radius=15)
        pygame.draw.rect(surface, (40, 0, 0), (bx, by, bar_w, bar_h), border_radius=10)
        hp_ratio = max(0, player.health / player.max_health)
        pygame.draw.rect(surface, (0, 255, 100), (bx, by, bar_w * hp_ratio, bar_h), border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), (bx, by, bar_w, bar_h), 2, border_radius=10)
        
        hp_val_txt = self.font_small.render(f"{int(player.health)} / {int(player.max_health)}", True, COLOR_TEXT)
        surface.blit(hp_val_txt, (bx + bar_w//2 - hp_val_txt.get_width()//2, by + 4))

        # 4. Warnings & Overlays
        if corner_time > 3.0:
            warn = self.font_main.render("EXIT CORNER!", True, (255, 50, 50))
            surface.blit(warn, (self.width//2 - warn.get_width()//2, 150))

        if victory:
            self._draw_overlay(surface, "SYSTEM PURIFIED", (0, 255, 150))
        elif game_over:
            self._draw_overlay(surface, "SYSTEM FAILURE", (255, 50, 50))

    def _draw_overlay(self, surface, message, color):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((*color, 60))
        surface.blit(overlay, (0,0))
        txt = self.font_big.render(message, True, COLOR_TEXT)
        rect = txt.get_rect(center=(self.width/2, self.height/2))
        for i in range(5):
             glow = self.font_big.render(message, True, color)
             surface.blit(glow, (rect.x-i, rect.y), special_flags=pygame.BLEND_ADD)
        surface.blit(txt, rect)
