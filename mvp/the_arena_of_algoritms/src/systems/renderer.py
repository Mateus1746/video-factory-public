import pygame
import random
from ..config import *
from ..effects import Starfield, draw_particles, get_fonts

class RenderSystem:
    def __init__(self, screen):
        self.screen = screen
        self.render_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.font = pygame.font.SysFont("Arial", 30, bold=True)
        self.starfield = Starfield(150)
        
    def update_visuals(self):
        self.starfield.update()

    def draw(self, battle_manager, recorder=None, debug_mode=False, telemetry=None):
        # Draw to offscreen surface
        self.render_surf.fill(BLACK)
        self.starfield.draw(self.render_surf)

        # UI & World
        pygame.draw.line(self.render_surf, GRAY, (0, HALF_HEIGHT), (SCREEN_WIDTH, HALF_HEIGHT), 2)
        
        # Labels
        label_top = self.font.render(battle_manager.top_name, True, battle_manager.top_color)
        self.render_surf.blit(label_top, (SCREEN_WIDTH//2 - label_top.get_width()//2, 10))
        
        label_bot = self.font.render(battle_manager.bot_name, True, battle_manager.bot_color)
        self.render_surf.blit(label_bot, (SCREEN_WIDTH//2 - label_bot.get_width()//2, HALF_HEIGHT + 10))
        
        # Entities
        for ring in battle_manager.rings_top + battle_manager.rings_bot:
            ring.draw(self.render_surf)
            
        battle_manager.algo_top.draw(self.render_surf)
        battle_manager.algo_bot.draw(self.render_surf)
        
        draw_particles(self.render_surf)

        # Shake Implementation
        shake_offset = (0, 0)
        if battle_manager.shake_intensity > 0:
            shake_offset = (random.randint(-int(battle_manager.shake_intensity), int(battle_manager.shake_intensity)), 
                            random.randint(-int(battle_manager.shake_intensity), int(battle_manager.shake_intensity)))
        
        self.screen.fill(BLACK)
        self.screen.blit(self.render_surf, shake_offset)
        
        # Victory Overlay
        if battle_manager.winner_text:
            self.draw_victory(battle_manager.winner_text, battle_manager.winner_color)
        
        if recorder:
            recorder.capture_frame(self.screen)
            
        if debug_mode and telemetry:
            self.draw_debug_overlay(telemetry)

        pygame.display.flip()

    def draw_victory(self, text, color):
        _, font_l = get_fonts()
        text_surf = font_l.render(text, True, color)
        shadow_surf = font_l.render(text, True, BLACK)
        
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        self.screen.blit(shadow_surf, (center_x - text_surf.get_width()//2 + 4, center_y - text_surf.get_height()//2 + 4))
        self.screen.blit(text_surf, (center_x - text_surf.get_width()//2, center_y - text_surf.get_height()//2))

    def draw_debug_overlay(self, telemetry):
        stats = telemetry.get_diagnostics()
        font_s, _ = get_fonts()
        
        debug_lines = [
            f"FPS: {stats['fps']}",
            f"Update: {stats['update_ms']}ms",
            f"Draw: {stats['draw_ms']}ms",
            f"Errors: {stats['error_count']}",
            f"Uptime: {stats['uptime']}s"
        ]
        
        y = 50
        for line in debug_lines:
            txt = font_s.render(line, True, (0, 255, 0))
            bg_rect = txt.get_rect(topleft=(10, y))
            pygame.draw.rect(self.screen, (0, 0, 0, 150), bg_rect)
            self.screen.blit(txt, (10, y))
            y += 20
