"""
Video Renderer for Velocity Odds.
Encapsulates all rendering logic for clean separation of concerns.
"""
import os
import pygame
import math
import random
from config import *
from visuals import draw_neon_arc


class VelocityOddsRenderer:
    """Handles all drawing operations for Velocity Odds video generation."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.center = (width // 2, height // 2)
        self.header_height = 80
        
        # Initialize fonts
        self.font_money = pygame.font.SysFont("Courier New", 28, bold=True)
        self.font_team_name = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_hud = pygame.font.SysFont("Arial", 16)
        self.font_big = pygame.font.SysFont("Arial", 60, bold=True)
        self.font_event = pygame.font.SysFont("Impact", 56)
        self.font_item = pygame.font.SysFont("Arial", 14, bold=True)
        
        # Load Assets (Fail-fast)
        self.team_assets = {}
        self._load_assets()
        
        # Prerender backgrounds
        self.background = self._create_background()
        self.header_bg = self._create_header()
        
        # Optimization: Precompute particles
        self.particle_cache = {} 
        
        # New Visual States
        self.impact_flash = 0.0 # 0 to 1
        self.zoom_level = 1.0
    
    def _load_assets(self):
        """Load team sprites. Only 'default' is mandatory."""
        teams = [TEAM_A, TEAM_B]
        team_ids = ["TEAM_A", "TEAM_B"]
        
        for idx, team_conf in enumerate(teams):
            tid = team_ids[idx]
            self.team_assets[tid] = {}
            sprites_conf = team_conf.get("sprites", {})
            
            for key, path in sprites_conf.items():
                if os.path.exists(path):
                    try:
                        img = pygame.image.load(path).convert_alpha()
                        scaled = pygame.transform.scale(img, (BALL_RADIUS*2, BALL_RADIUS*2))
                        self.team_assets[tid][key] = scaled
                    except Exception as e:
                        print(f"⚠️ Warning: Could not load {path}: {e}")
                elif key == "default":
                    print(f"❌ CRITICAL: Default asset missing for {team_conf['name']}: {path}")
                    # Create a placeholder surface if default is missing to avoid crash
                    surf = pygame.Surface((BALL_RADIUS*2, BALL_RADIUS*2), pygame.SRCALPHA)
                    pygame.draw.circle(surf, team_conf["color"], (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)
                    self.team_assets[tid]["default"] = surf

    def _create_background(self) -> pygame.Surface:
        """Create static background surface."""
        bg = pygame.Surface((self.width, self.height))
        bg.fill(BLACK)
        for r in range(0, 800, 100):
            pygame.draw.circle(bg, (20, 20, 35), self.center, r, 1)
        return bg
    
    def _create_header(self) -> pygame.Surface:
        header = pygame.Surface((self.width, self.header_height))
        header.fill((10, 10, 20))
        pygame.draw.rect(header, (30, 30, 45), (0, 0, self.width, self.header_height), 2)
        return header
    
    def _get_particle_surface(self, color, size, alpha_val):
        key = (color, size)
        if key not in self.particle_cache:
            self.particle_cache[key] = []
            for a in range(0, 256, 255 // PARTICLE_CACHE_STEPS):
                s = pygame.Surface((size*4, size*4), pygame.SRCALPHA)
                col_rgb = (int(color[0]), int(color[1]), int(color[2]))
                pygame.draw.circle(s, (*col_rgb, a), (size*2, size*2), size)
                self.particle_cache[key].append((a, s))
        
        best_surf = self.particle_cache[key][-1][1]
        min_diff = 255
        for a, surf in self.particle_cache[key]:
            diff = abs(a - alpha_val)
            if diff < min_diff:
                min_diff = diff
                best_surf = surf
            else: break 
        return best_surf

    def render_frame(self, screen, sim, particles, trails, floating_texts, shaker, frame_count):
        offset_x, offset_y = shaker.get_offset()
        
        # Dynamic Zoom Logic
        target_zoom = 1.0
        active_p = [p for p in sim.players if not p.finished]
        if active_p:
            # Zoom in as players get closer to center/finish
            max_idx = max(p.current_ring_index for p in active_p)
            target_zoom = 1.0 + (max_idx / len(RINGS_CONFIG)) * 0.4
        self.zoom_level += (target_zoom - self.zoom_level) * 0.1

        # Layer 1: Background
        screen.fill(BLACK)
        screen.blit(self.background, (offset_x, offset_y))
        
        draw_center_x = self.center[0] + offset_x
        draw_center_y = self.center[1] + offset_y
        
        # Apply Zoom by scaling everything else (Conceptual for this 2D project)
        # For simplicity, we scale radii and positions
        
        # Layer 2: Trails
        for trail in trails:
            trail.draw(screen, offset_x, offset_y)
        
        # Layer 3: Rings
        self._draw_rings(screen, sim, draw_center_x, draw_center_y)
        
        # Layer 4: Items
        for item in sim.items:
            if item.active:
                t = frame_count / 300.0
                anim_y = math.sin(t + item.anim_offset) * 3
                dx = int(self.center[0] + item.x + offset_x)
                dy = int(self.center[1] + item.y + offset_y + anim_y)
                col = globals().get(item.color_key, WHITE)
                self._draw_item_entity(screen, dx, dy, item.radius, col, item.symbol)

        # Layer 5: Players
        for player in sim.players:
            if not player.finished:
                self._draw_player_entity(screen, player, draw_center_x, draw_center_y)
        
        # Layer 6: Particles
        for p in particles:
            if p.life > 0:
                alpha = int(p.life * 255)
                surf = self._get_particle_surface(p.color, int(p.size), alpha)
                screen.blit(surf, (p.x + offset_x - p.size*2, p.y + offset_y - p.size*2))
        
        # Layer 7: Floating Texts
        for ft in floating_texts:
            ft.draw(screen, offset_x, offset_y)
            
        # Layer 8: UI Header & Progress
        self._draw_header_ui(screen, sim)
        self._draw_progress_bars(screen, sim)
        
        # Layer 9: Chaos Overlay
        if sim.current_chaos:
            self._draw_chaos_overlay(screen, sim, offset_x, offset_y)
            
        # Layer 10: Impact Flash
        if self.impact_flash > 0:
            flash_surf = pygame.Surface((self.width, self.height))
            flash_surf.fill((255, 255, 255))
            flash_surf.set_alpha(int(self.impact_flash * 180))
            screen.blit(flash_surf, (0,0))
            self.impact_flash -= 0.1

    def _draw_rings(self, screen, sim, draw_center_x, draw_center_y):
        active_indices = [p.current_ring_index for p in sim.players if not p.finished]
        min_ring_index = min(active_indices) if active_indices else len(RINGS_CONFIG)
        
        for i, ring in enumerate(RINGS_CONFIG):
            if i < min_ring_index: continue
            base = NEON_GREEN if ring["type"] == "green" else NEON_RED
            color = (base[0]//2, base[1]//2, base[2]//2)
            # Apply Zoom to radius
            z_radius = int(ring["radius"] * self.zoom_level)
            draw_neon_arc(screen, base, (draw_center_x, draw_center_y), 
                         z_radius, sim.ring_angles[i], ring["gap"], 4)

    def _draw_player_entity(self, surface, player, center_x, center_y):
        # Apply Zoom to position
        dx = int(center_x + player.pos_x * self.zoom_level)
        dy = int(center_y + player.pos_y * self.zoom_level)
        team_sprites = self.team_assets.get(player.team_id, {})
        sprite = team_sprites.get(player.emotion, team_sprites.get("default"))
        if sprite:
            if self.zoom_level != 1.0:
                s_size = int(BALL_RADIUS * 2 * self.zoom_level)
                sprite = pygame.transform.scale(sprite, (s_size, s_size))
            rect = sprite.get_rect(center=(dx, dy))
            surface.blit(sprite, rect)
        else:
            pygame.draw.circle(surface, player.color, (dx, dy), int(BALL_RADIUS * self.zoom_level))
        pygame.draw.circle(surface, WHITE, (dx, dy), int(BALL_RADIUS * self.zoom_level), 1)

    def _draw_item_entity(self, surface, x, y, radius, color, symbol):
        pygame.draw.circle(surface, color, (x, y), radius)
        txt = self.font_item.render(symbol, True, BLACK)
        rect = txt.get_rect(center=(x, y))
        surface.blit(txt, rect)
        pygame.draw.circle(surface, WHITE, (x, y), radius, 1)

    def _draw_progress_bars(self, screen, sim):
        """Draw comparative progress bars below header."""
        bar_w = 400
        bar_h = 12
        y_start = self.header_height + 20
        
        for idx, p in enumerate(sim.players):
            progress = p.current_ring_index / len(RINGS_CONFIG)
            x = 50 if idx == 0 else self.width - 50 - bar_w
            # BG
            pygame.draw.rect(screen, (40, 40, 50), (x, y_start, bar_w, bar_h), border_radius=6)
            # Fill
            fill_w = int(progress * bar_w)
            pygame.draw.rect(screen, p.color, (x, y_start, fill_w, bar_h), border_radius=6)
            # Label
            label = self.font_hud.render(f"{int(progress*100)}%", True, WHITE)
            lx = x + bar_w + 10 if idx == 0 else x - 40
            screen.blit(label, (lx, y_start - 4))

    def _draw_header_ui(self, screen, sim):
        screen.blit(self.header_bg, (0, 0))
        
        p1, p2 = sim.players[0], sim.players[1]
        
        # Determine who is winning by cash for UI feedback
        p1_leading = p1.money > p2.money
        p2_leading = p2.money > p1.money
        
        # Player 1 UI
        col1 = p1.color if not p1_leading else NEON_GREEN
        screen.blit(self.font_team_name.render(p1.name, True, p1.color), (20, 10))
        screen.blit(self.font_money.render(f"${p1.money:,.0f}", True, col1), (20, 40))
        
        # Player 2 UI
        col2 = p2.color if not p2_leading else NEON_GREEN
        name2 = self.font_team_name.render(p2.name, True, p2.color)
        money2 = self.font_money.render(f"${p2.money:,.0f}", True, col2)
        screen.blit(name2, name2.get_rect(topright=(self.width-20, 10)))
        screen.blit(money2, money2.get_rect(topright=(self.width-20, 40)))
        
        self._draw_centered_text(screen, self.font_team_name, "CASH BATTLE", (200, 200, 200), (self.width//2, self.header_height//2))

    def _draw_chaos_overlay(self, screen, sim, offset_x, offset_y):
        chaos_name = sim.current_chaos
        col = globals().get(f"COLOR_EVENT_{chaos_name}", WHITE)
        render = self.font_event.render(f"⚠ {chaos_name} ⚠", True, col)
        dest = render.get_rect(center=(self.center[0] + offset_x, 150 + offset_y))
        screen.blit(render, dest)
        bar_fill = (sim.chaos_duration / EVENT_DURATION) * 300
        pygame.draw.rect(screen, (30, 30, 40), (self.center[0]-150+offset_x, 195+offset_y, 300, 10), border_radius=5)
        pygame.draw.rect(screen, col, (self.center[0]-150+offset_x, 195+offset_y, bar_fill, 10), border_radius=5)

    def _draw_centered_text(self, surface, font, text, color, pos):
        render = font.render(text, True, color)
        rect = render.get_rect(center=pos)
        surface.blit(render, rect)
