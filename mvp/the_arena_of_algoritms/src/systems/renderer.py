import pygame
import random
import math
from ..config import *
from ..effects import Starfield, RetroGrid, draw_particles, get_fonts

class RenderSystem:
    def __init__(self, screen):
        self.screen = screen
        self.render_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.font = pygame.font.SysFont("Arial", 30, bold=True)
        self.starfield = Starfield(150)
        self.grid = RetroGrid()
        
    def update_visuals(self):
        self.starfield.update()
        self.grid.update(0.016) # Approx dt

    def draw(self, battle_manager, recorder=None, debug_mode=False, telemetry=None):
        # Draw to offscreen surface
        self.render_surf.fill(BLACK)
        
        # Layer 0: Grid
        self.grid.draw(self.render_surf)
        
        # Layer 1: Stars (Parallax on top)
        self.starfield.draw(self.render_surf)

        # Enrage Visuals (Subtle Red Pulse)
        if battle_manager.enrage_active:
            pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 0.5
            red_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            red_overlay.set_alpha(int(30 * pulse))
            red_overlay.fill((255, 0, 0))
            self.render_surf.blit(red_overlay, (0, 0))

        # UI & World
        pygame.draw.line(self.render_surf, GRAY, (0, HALF_HEIGHT), (SCREEN_WIDTH, HALF_HEIGHT), 2)
        
        # Labels
        label_top = self.font.render(battle_manager.top_name, True, battle_manager.top_color)
        self.render_surf.blit(label_top, (SCREEN_WIDTH//2 - label_top.get_width()//2, 60)) # Moved down for HUD
        
        label_bot = self.font.render(battle_manager.bot_name, True, battle_manager.bot_color)
        self.render_surf.blit(label_bot, (SCREEN_WIDTH//2 - label_bot.get_width()//2, HALF_HEIGHT + 60))
        
        # Entities
        for ring in battle_manager.rings_top + battle_manager.rings_bot:
            ring.draw(self.render_surf)
            
        battle_manager.algo_top.draw(self.render_surf)
        battle_manager.algo_bot.draw(self.render_surf)
        
        battle_manager.projectile_manager.draw(self.render_surf)
        
        draw_particles(self.render_surf)

        # --- HUD: HEALTH BARS ---
        bar_height = 20
        # TOP TEAM BAR (Top of screen)
        pct_top = battle_manager.get_team_hp_pct("top")
        pygame.draw.rect(self.render_surf, (50, 50, 50), (0, 0, SCREEN_WIDTH, bar_height))
        pygame.draw.rect(self.render_surf, battle_manager.top_color, (0, 0, int(SCREEN_WIDTH * pct_top), bar_height))
        
        # BOT TEAM BAR (Bottom of screen)
        pct_bot = battle_manager.get_team_hp_pct("bot")
        pygame.draw.rect(self.render_surf, (50, 50, 50), (0, SCREEN_HEIGHT - bar_height, SCREEN_WIDTH, bar_height))
        pygame.draw.rect(self.render_surf, battle_manager.bot_color, (0, SCREEN_HEIGHT - bar_height, int(SCREEN_WIDTH * pct_bot), bar_height))

        # --- CALL TO ACTION (First 4 seconds) ---
        if battle_manager.time_elapsed < 4.0:
            alpha = int(255 * (1.0 - (battle_manager.time_elapsed / 4.0)))
            if alpha > 0:
                font_cta = pygame.font.SysFont("Arial", 80, bold=True)
                cta_surf = font_cta.render("CHOOSE YOUR SIDE", True, WHITE)
                cta_surf.set_alpha(alpha)
                # Blink effect
                if int(battle_manager.time_elapsed * 4) % 2 == 0:
                    self.render_surf.blit(cta_surf, (SCREEN_WIDTH//2 - cta_surf.get_width()//2, HALF_HEIGHT - cta_surf.get_height()//2))

        # Shake Implementation
        shake_offset = (0, 0)
        if battle_manager.shake_intensity > 0:
            shake_offset = (random.randint(-int(battle_manager.shake_intensity), int(battle_manager.shake_intensity)), 
                            random.randint(-int(battle_manager.shake_intensity), int(battle_manager.shake_intensity)))
        
        # Camera Logic (Zoom on Victory)
        final_surf = self.render_surf
        if battle_manager.game_over and battle_manager.victory_timer > 0:
            # Zoom factor from 1.0 to 1.5 over 2 seconds
            zoom = 1.0 + min(0.5, battle_manager.victory_timer * 0.25)
            
            # Determine focus point
            if battle_manager.winner_team == 'top':
                focus = (SCREEN_WIDTH // 2, HALF_HEIGHT // 2)
            elif battle_manager.winner_team == 'bot':
                focus = (SCREEN_WIDTH // 2, HALF_HEIGHT + HALF_HEIGHT // 2)
            else:
                focus = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                
            # Scale and crop
            new_w = int(SCREEN_WIDTH * zoom)
            new_h = int(SCREEN_HEIGHT * zoom)
            scaled = pygame.transform.smoothscale(self.render_surf, (new_w, new_h))
            
            # Blit centered on focus
            # We want 'focus' on original surface to be at center of screen
            # Scaled focus position
            sx = focus[0] * zoom
            sy = focus[1] * zoom
            
            # We want sx, sy to be at screen center
            blit_x = (SCREEN_WIDTH // 2) - sx
            blit_y = (SCREEN_HEIGHT // 2) - sy
            
            # Add shake to this final transform
            self.screen.fill(BLACK)
            self.screen.blit(scaled, (blit_x + shake_offset[0], blit_y + shake_offset[1]))
        else:
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
