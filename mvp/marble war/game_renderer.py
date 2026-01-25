"""
Renderer for Marble War.
Handles all drawing operations.
"""

import math
import pygame
import config
from themes import ThemeManager, Theme
from entities import Marble
from effects import ParticleSystem, Explosion, FloatingText, PowerUp

class GameRenderer:
    def __init__(self, screen: pygame.Surface, assets, theme: Theme):
        self.screen = screen
        self.assets = assets
        self.theme = theme
        
        # Pre-render grid
        self.grid_surface = pygame.Surface((config.WIDTH, config.HEIGHT))
        self.grid_surface.fill(self.theme.bg_color)
        grid_size = config.GRID_SIZE
        for x in range(0, config.WIDTH, grid_size):
            pygame.draw.line(self.grid_surface, self.theme.grid_color, (x, 0), (x, config.HEIGHT))
        for y in range(0, config.HEIGHT, grid_size):
            pygame.draw.line(self.grid_surface, self.theme.grid_color, (0, y), (config.WIDTH, y))

    def draw(self, marbles, powerups, projectiles, particles, explosions, floating_texts, 
             arena_gen, zone_active, zone_radius, shake_offset, 
             bomb_active, bomb_holder, winner_team, kill_feed, portals, frame_count):
        
        # Clear & Grid
        self.screen.fill(self.theme.bg_color)
        self.screen.blit(self.grid_surface, shake_offset)
        
        # Draw Portals
        for p in portals:
            pygame.draw.circle(self.screen, p.color, p.entry, p.radius, 3)
            pygame.draw.circle(self.screen, p.color, p.exit, p.radius // 2, 2)
            t = pygame.time.get_ticks() / 200.0
            r_glow = p.radius + math.sin(t) * 10
            pygame.draw.circle(self.screen, (*p.color, 50), p.entry, int(r_glow), 1)

        # Arena
        arena_gen.draw(self.screen)
        
        # Zone
        if zone_active:
            center = (config.WIDTH//2 + shake_offset[0], config.HEIGHT//2 + shake_offset[1])
            pygame.draw.circle(self.screen, (255, 0, 0), center, int(zone_radius), 5)
            
            # Sudden Death Warning
            t = pygame.time.get_ticks() / 200.0
            if math.sin(t) > 0:
                font_sd = pygame.font.SysFont("Arial", 100, bold=True)
                txt = font_sd.render("SUDDEN DEATH", True, (255, 0, 0))
                self.screen.blit(txt, (config.WIDTH//2 - txt.get_width()//2, 100))

        # Powerups
        for p in powerups:
            p.draw(self.screen, self.assets.powerup_images)
            
        # Projectiles
        for p in projectiles:
            p.draw(self.screen, self.assets.projectile_img)
            
        # Particles
        particles.draw(self.screen)
        
        # Explosions
        for e in explosions:
            e.draw(self.screen)
            
        # Marbles
        for m in marbles:
            pos = (int(m.body.position.x + shake_offset[0]), int(m.body.position.y + shake_offset[1]))
            pygame.draw.circle(self.screen, m.color, pos, config.MARBLE_RADIUS)
            
            # Countdown text if trapped
            trapped_t = getattr(m, 'trapped_timer', 0)
            if trapped_t > 0:
                pulse = 10 + math.sin(pygame.time.get_ticks() / 100.0) * 5
                pygame.draw.circle(self.screen, (255, 255, 255), pos, config.MARBLE_RADIUS + int(pulse), 3)
                
                font_c = pygame.font.SysFont("Arial", 50, bold=True)
                txt_str = f"{trapped_t:.1f}s"
                txt_bg = font_c.render(txt_str, True, (0, 0, 0))
                txt = font_c.render(txt_str, True, (255, 255, 255))
                t_pos = (pos[0] - txt.get_width()//2, pos[1] - 100)
                self.screen.blit(txt_bg, (t_pos[0]+2, t_pos[1]+2))
                self.screen.blit(txt, t_pos)

            if m.assassin_mode:
                pygame.draw.circle(self.screen, (255, 255, 255), pos, config.MARBLE_RADIUS + 5, 2)
            pygame.draw.circle(self.screen, (0, 0, 0), pos, config.MARBLE_RADIUS, 2)
            
            if m.freeze_active:
                pygame.draw.circle(self.screen, (0, 255, 255), pos, config.MARBLE_RADIUS, 4)
            if m.magnet_active:
                pygame.draw.circle(self.screen, (148, 0, 211), pos, config.MARBLE_RADIUS + 10, 2)
                
            self._draw_face(m, pos)
            
        # Bomb
        if bomb_active and bomb_holder:
            self._draw_bomb(bomb_holder, shake_offset)
            
        # Floating Text
        for ft in floating_texts:
            ft.draw(self.screen)
            
        # HUD
        self._draw_ui(marbles, kill_feed, frame_count)
        
        # Victory
        if winner_team:
            self._draw_victory(winner_team)

    def _draw_face(self, marble: Marble, pos: tuple):
        if not (-10000 < pos[0] < 10000 and -10000 < pos[1] < 10000): return
        face_img = self.assets.face_assets.get(marble.current_face)
        if face_img:
            rect = face_img.get_rect(center=(int(pos[0]), int(pos[1])))
            self.screen.blit(face_img, rect)
        if marble.assassin_mode and self.assets.weapon_img:
            rect = self.assets.weapon_img.get_rect(center=(int(pos[0]+20), int(pos[1]+10)))
            self.screen.blit(self.assets.weapon_img, rect)

    def _draw_bomb(self, holder, offset):
        pos = (int(holder.body.position.x + offset[0]), int(holder.body.position.y + offset[1]))
        if self.assets.bomb_img:
            rect = self.assets.bomb_img.get_rect(center=pos)
            self.screen.blit(self.assets.bomb_img, rect)
        else:
            pygame.draw.circle(self.screen, (255, 0, 0), pos, config.MARBLE_RADIUS + 10, 3)

    def _draw_ui(self, marbles, kill_feed, frame_count):
        pygame.draw.rect(self.screen, (0, 0, 0, 180), (0, 0, config.WIDTH, 60))
        counts = {}
        for m in marbles:
            counts[m.team] = counts.get(m.team, 0) + 1
            if m.max_hp > 10: # Boss Bar
                bx, by = int(m.body.position.x), int(m.body.position.y)
                pct = m.hp / m.max_hp
                pygame.draw.rect(self.screen, (255, 0, 0), (bx-100, by-150, int(200*pct), 20))
                pygame.draw.rect(self.screen, (255, 255, 255), (bx-100, by-150, 200, 20), 2)
        
        font = pygame.font.SysFont("Arial", 30, bold=True)
        x_off = 20
        for team, count in sorted(counts.items()):
            color = (255, 255, 255)
            if team == "civilian": color = (0, 100, 255)
            elif team == "zombie": color = (50, 255, 50)
            elif team == "attacker": color = (0, 200, 255)
            elif team == "boss": color = (255, 0, 0)
            else: color = config.TEAM_COLORS.get(f"team_{team}", (255, 255, 255))
            
            txt = font.render(f"{team.upper()}: {count}", True, color)
            self.screen.blit(txt, (x_off, 15))
            x_off += 250
            
        # Survival Timer
        if "civilian" in counts and "zombie" in counts:
            time_left = max(0, 50 - (frame_count / config.FPS))
            if time_left > 0:
                timer_txt = font.render(f"HUMAN WIN IN: {time_left:.1f}s", True, (255, 255, 255))
                self.screen.blit(timer_txt, (config.WIDTH - 350, 15))

        y = config.HEIGHT - 150
        f_font = pygame.font.SysFont("Arial", 20)
        for msg in kill_feed[-5:]:
            txt = f_font.render(msg, True, self.theme.text_color)
            self.screen.blit(txt, (20, y))
            y += 25

    def _draw_victory(self, winner):
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        font = pygame.font.SysFont("Arial", 80, bold=True)
        txt = font.render(f"WINNER: {winner}!", True, (255, 215, 0))
        self.screen.blit(txt, (config.WIDTH//2 - txt.get_width()//2, config.HEIGHT//2))