"""
Video Renderer for Velocity Odds.
Encapsulates all rendering logic for clean separation of concerns.
"""
import pygame
import math
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
        self.font_team_name = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_hud = pygame.font.SysFont("Arial", 16)
        self.font_big = pygame.font.SysFont("Arial", 50, bold=True)
        self.font_event = pygame.font.SysFont("Impact", 48)
        self.font_item = pygame.font.SysFont("Arial", 14, bold=True)
        
        # Prerender backgrounds
        self.background = self._create_background()
        self.header_bg = self._create_header()
    
    def _create_background(self) -> pygame.Surface:
        """Create static background surface with concentric circles."""
        bg = pygame.Surface((self.width, self.height))
        bg.fill(BLACK)
        for r in range(0, 500, 50):
            pygame.draw.circle(bg, (20, 20, 30), self.center, r, 1)
        return bg
    
    def _create_header(self) -> pygame.Surface:
        """Create static header background."""
        header = pygame.Surface((self.width, self.header_height))
        header.fill((15, 15, 20))
        pygame.draw.line(header, (50, 50, 50), (self.width//2, 0), 
                        (self.width//2, self.header_height), 2)
        pygame.draw.line(header, (50, 50, 50), (0, self.header_height), 
                        (self.width, self.header_height), 2)
        return header
    
    def render_frame(self, screen, sim, particles, trails, shaker, frame_count):
        """
        Main rendering orchestration for a single frame.
        
        Args:
            screen: Pygame surface to render to
            sim: Simulation object with game state
            particles: List of particle effects
            trails: List of player trails
            shaker: ScreenShake instance
            frame_count: Current frame number for animations
        """
        offset_x, offset_y = shaker.get_offset()
        
        # Layer 1: Background
        screen.fill(BLACK)
        screen.blit(self.background, (offset_x, offset_y))
        
        draw_center_x = self.center[0] + offset_x
        draw_center_y = self.center[1] + offset_y
        
        # Layer 2: Trails
        self._draw_trails(screen, trails, offset_x, offset_y)
        
        # Layer 3: Rings
        self._draw_rings(screen, sim, draw_center_x, draw_center_y)
        
        # Layer 4: Items
        self._draw_items(screen, sim, offset_x, offset_y, frame_count)
        
        # Layer 5: Players
        self._draw_players(screen, sim, draw_center_x, draw_center_y)
        
        # Layer 6: Particles
        self._draw_particles(screen, particles, offset_x, offset_y)
        
        # Layer 7: UI
        self._draw_header_ui(screen, sim)
        
        # Layer 8: Chaos Overlay
        if sim.current_chaos:
            self._draw_chaos_overlay(screen, sim, offset_x, offset_y)
    
    def _draw_trails(self, screen, trails, offset_x, offset_y):
        """Draw motion trails for players."""
        for trail in trails:
            trail.draw(screen, offset_x, offset_y)
    
    def _draw_rings(self, screen, sim, draw_center_x, draw_center_y):
        """Draw concentric rings with gaps."""
        # Optimize: Only draw rings at or ahead of player progress
        active_indices = [p.current_ring_index for p in sim.players if not p.finished]
        
        if not active_indices and sim.players:
            min_ring_index = len(RINGS_CONFIG)
        elif active_indices:
            min_ring_index = min(active_indices)
        else:
            min_ring_index = 0
        
        for i, ring in enumerate(RINGS_CONFIG):
            if i < min_ring_index:
                continue
            
            # Color based on ring type
            if ring["type"] == "green":
                base = NEON_GREEN
            else:
                base = NEON_RED
            
            color = (base[0]//2, base[1]//2, base[2]//2)
            draw_neon_arc(screen, color, (draw_center_x, draw_center_y), 
                         ring["radius"], sim.ring_angles[i], ring["gap"], 3)
    
    def _draw_items(self, screen, sim, offset_x, offset_y, frame_count):
        """Draw power-up items with animation."""
        for item in sim.items:
            if item.active:
                # Floating animation
                t = frame_count / 300.0
                anim_y = math.sin(t + item.anim_offset) * 3
                
                dx = int(self.center[0] + item.x + offset_x)
                dy = int(self.center[1] + item.y + offset_y + anim_y)
                
                pygame.draw.circle(screen, item.color, (dx, dy), item.radius)
                pygame.draw.circle(screen, WHITE, (dx, dy), item.radius, 1)
    
    def _draw_players(self, screen, sim, draw_center_x, draw_center_y):
        """Draw player balls."""
        for player in sim.players:
            if not player.finished:
                player.draw(screen, draw_center_x, draw_center_y)
    
    def _draw_particles(self, screen, particles, offset_x, offset_y):
        """Draw particle effects."""
        for p in particles:
            if p.life > 0:
                alpha = int(p.life * 255)
                s_p = pygame.Surface((int(p.size*4), int(p.size*4)), pygame.SRCALPHA)
                col_rgb = (int(p.color[0]), int(p.color[1]), int(p.color[2]))
                pygame.draw.circle(s_p, (*col_rgb, alpha), 
                                 (int(p.size*2), int(p.size*2)), int(p.size))
                screen.blit(s_p, (p.x + offset_x - p.size*2, p.y + offset_y - p.size*2))
    
    def _draw_header_ui(self, screen, sim):
        """Draw header with team names and money."""
        screen.blit(self.header_bg, (0, 0))
        
        # Player 1 (Left)
        p1 = sim.players[0]
        col1 = p1.color if p1.money >= 0 else (100, 50, 50)
        name1 = self.font_team_name.render(p1.name, True, p1.color)
        money1 = self.font_money.render(f"${p1.money:,.0f}", True, col1)
        screen.blit(name1, (20, 10))
        screen.blit(money1, (20, 40))
        
        # Player 2 (Right)
        p2 = sim.players[1]
        col2 = p2.color if p2.money >= 0 else (100, 50, 50)
        name2 = self.font_team_name.render(p2.name, True, p2.color)
        money2 = self.font_money.render(f"${p2.money:,.0f}", True, col2)
        n2_rect = name2.get_rect(topright=(self.width-20, 10))
        m2_rect = money2.get_rect(topright=(self.width-20, 40))
        screen.blit(name2, n2_rect)
        screen.blit(money2, m2_rect)
        
        # VS label
        self._draw_centered_text(screen, self.font_team_name, "VS", 
                                (100, 100, 100), (self.width//2, self.header_height//2))
    
    def _draw_chaos_overlay(self, screen, sim, offset_x, offset_y):
        """Draw chaos event overlay with timer."""
        chaos_name = sim.current_chaos
        col = WHITE
        txt = chaos_name
        
        if chaos_name == "INVERT":
            txt = "⚠ GRAVITY INVERT ⚠"
            col = COLOR_EVENT_INVERT
        elif chaos_name == "MOON":
            txt = "☾ MOON GRAVITY ☾"
            col = COLOR_EVENT_MOON
        elif chaos_name == "TURBO":
            txt = "⚡ TURBO MODE ⚡"
            col = COLOR_EVENT_TURBO
        elif chaos_name == "GLITCH":
            txt = "✖ SYSTEM GLITCH ✖"
            col = COLOR_EVENT_GLITCH
        
        render = self.font_event.render(txt, True, col)
        dest = render.get_rect(center=(self.center[0] + offset_x, 150 + offset_y))
        screen.blit(render, dest)
        
        # Timer bar
        bar_fill = (sim.chaos_duration / EVENT_DURATION) * 200
        pygame.draw.rect(screen, (50, 50, 50), 
                        (self.center[0]-100+offset_x, 185+offset_y, 200, 8))
        pygame.draw.rect(screen, col, 
                        (self.center[0]-100+offset_x, 185+offset_y, bar_fill, 8))
    
    def _draw_centered_text(self, surface, font, text, color, pos):
        """Helper to draw centered text."""
        render = font.render(text, True, color)
        rect = render.get_rect(center=pos)
        surface.blit(render, rect)
