"""
Visualization Module using Pygame
"""
import os
import pygame
import random
import math
from sim import config

class Renderer:
    def __init__(self, headless=True):
        if headless:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            
        pygame.init()
        # Initialize font
        pygame.font.init()
        self.font_large = pygame.font.SysFont("Arial", 80, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 40, bold=True)
        
        self.width = config.VIDEO_WIDTH
        self.height = config.VIDEO_HEIGHT
        self.surface = pygame.display.set_mode((self.width, self.height))
        
        # Particles: List of [x, y, vx, vy, color, life]
        self.particles = []
        self.shockwaves = [] # List of [x, y, radius, max_radius, life]
        
        # Create background surface
        self.bg_surface = self._create_bg()

    def _create_bg(self):
        s = pygame.Surface((self.width, self.height))
        s.fill(config.COLOR_BG_DARK)
        
        # Draw Neon Grid
        grid_size = 100
        for x in range(0, self.width, grid_size):
            pygame.draw.line(s, config.COLOR_GRID, (x, 0), (x, self.height), 1)
        for y in range(0, self.height, grid_size):
            pygame.draw.line(s, config.COLOR_GRID, (0, y), (self.width, y), 1)
            
        # Draw Wall with Glow
        wall_rect = (config.BASE_X_LIMIT - 10, 0, 15, self.height)
        # Glow effect
        for i in range(5):
            glow_surf = pygame.Surface((30 + i*4, self.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (0, 255, 255, 50 - i*10), (0, 0, 30 + i*4, self.height))
            s.blit(glow_surf, (config.BASE_X_LIMIT - 20 - i*2, 0))
            
        pygame.draw.rect(s, config.COLOR_WALL, wall_rect)
        return s

    def _emit_particles(self, x, y, color):
        for _ in range(config.PARTICLE_COUNT):
            angle = random.uniform(0, 3.1415 * 2)
            speed = random.uniform(2, 8)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append([x, y, vx, vy, color, config.PARTICLE_LIFESPAN])

    def _emit_shockwave(self, x, y):
        # x, y, radius, max_radius, life
        self.shockwaves.append([x, y, 10, 150, 1.0])

    def _draw_soldier(self, surface, x, y, s_type, color):
        # 1. Body/Vest (Rectangular with rounded corners)
        pygame.draw.rect(surface, color, (x-8, y-8, 16, 16), border_radius=4)
        
        # 2. Shoulders/Arms
        pygame.draw.circle(surface, color, (x-4, y-8), 5)
        pygame.draw.circle(surface, color, (x-4, y+8), 5)
        
        # 3. Head (Helmet)
        pygame.draw.circle(surface, (255, 200, 150), (x, y), 6) 
        pygame.draw.circle(surface, color, (x-2, y), 6)
        
        # 4. Weapon
        gun_len = 20
        gun_width = 4
        
        if s_type == 'sniper': 
            gun_len = 30; gun_width = 3
        elif s_type == 'shotgun': 
            gun_len = 15; gun_width = 6
        elif s_type == 'minigun':
            # Rotary barrel look
            pygame.draw.rect(surface, (50, 50, 50), (x, y-4, 25, 8))
            pygame.draw.line(surface, (200, 200, 200), (x, y-2), (x+25, y-2), 1)
            pygame.draw.line(surface, (200, 200, 200), (x, y+2), (x+25, y+2), 1)
            return # Skip default drawing
        elif s_type == 'rocket':
            # Large tube on shoulder
            pygame.draw.rect(surface, (50, 60, 50), (x-5, y-6, 30, 8))
            pygame.draw.circle(surface, (30, 30, 30), (x+25, y-2), 5) # Muzzle
            return

        # Default Gun
        pygame.draw.rect(surface, (10, 10, 10), (x, y+2, gun_len, gun_width))
        pygame.draw.circle(surface, (255, 200, 150), (x+10, y+4), 3)

    def _draw_zombie(self, surface, x, y, z_type, radius, color):
        wobble = math.sin(x * 0.1) * 3
        
        if z_type == 'tank':
            rect_size = radius * 1.8
            pygame.draw.rect(surface, color, (x-radius, y-radius+wobble, rect_size, rect_size), border_radius=8)
            pygame.draw.circle(surface, (100, 0, 100), (x-5, y-5+wobble), 6)
            pygame.draw.circle(surface, (100, 0, 100), (x+5, y+5+wobble), 8)
            
        elif z_type == 'fast':
            points = [
                (x - radius, y - radius + wobble),
                (x - radius, y + radius + wobble),
                (x + radius, y + wobble)
            ]
            pygame.draw.polygon(surface, color, points)
            
        else: # Normal
            pygame.draw.circle(surface, color, (x, y+wobble), radius)
            pygame.draw.line(surface, color, (x, y+wobble), (x-radius-5, y-5+wobble), 4)
            pygame.draw.line(surface, color, (x, y+wobble), (x-radius-5, y+8+wobble), 4)

        eye_color = (255, 255, 0) if z_type == 'fast' else (50, 255, 50)
        if z_type == 'tank': eye_color = (255, 0, 0)
        
        pygame.draw.circle(surface, eye_color, (x-radius/2, y-3+wobble), 3)
        pygame.draw.circle(surface, eye_color, (x-radius/2, y+3+wobble), 3)

    def render(self, engine):
        # 1. Background
        self.surface.blit(self.bg_surface, (0, 0))
        
        # 1.5 Event Overlay
        if engine.active_event:
            ev_name = engine.active_event[0]
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            if ev_name == "ZOMBIE FRENZY" or ev_name == "BOSS WARNING":
                overlay.fill(config.COLOR_EVENT_BOSS)
                txt_color = (255, 50, 50)
            elif ev_name == "AIR SUPPORT":
                overlay.fill((0, 50, 100, 80)) # Blue tint
                txt_color = (100, 255, 255)
            else:
                overlay.fill(config.COLOR_EVENT_MIST)
                txt_color = (100, 255, 100)
            
            self.surface.blit(overlay, (0,0))
            
            # Flashing Text
            if (engine.frame_count // 10) % 2 == 0:
                text_ev = self.font_large.render(f"⚠ {ev_name} ⚠", True, txt_color)
                r = text_ev.get_rect(center=(self.width//2, 250))
                self.surface.blit(text_ev, r)

        # 2. Particles
        for p in self.particles[:]:
            p[0] += p[2] # x
            p[1] += p[3] # y
            p[5] -= 1    # life
            if p[5] <= 0:
                self.particles.remove(p)
                continue
            alpha = max(0, min(255, int((p[5] / config.PARTICLE_LIFESPAN) * 255)))
            
            # Ensure RGB are valid ints
            r = max(0, min(255, int(p[4][0])))
            g = max(0, min(255, int(p[4][1])))
            b = max(0, min(255, int(p[4][2])))
            color = (r, g, b, alpha)
            
            p_size = max(1, int(config.PARTICLE_SIZE * (p[5] / config.PARTICLE_LIFESPAN)))
            p_surf = pygame.Surface((p_size*2, p_size*2), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, color, (p_size, p_size), p_size)
            self.surface.blit(p_surf, (int(p[0]-p_size), int(p[1]-p_size)))

        # 2.5 Shockwaves
        for s in self.shockwaves[:]:
            # x, y, rad, max, life
            s[2] += (s[3] - s[2]) * 0.1 # Grow
            s[4] -= 0.05
            if s[4] <= 0:
                self.shockwaves.remove(s)
                continue
            
            alpha = int(255 * s[4])
            rad = int(s[2])
            surf = pygame.Surface((rad*2, rad*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (100, 200, 255, alpha), (rad, rad), rad, 4)
            self.surface.blit(surf, (s[0]-rad, s[1]-rad), special_flags=pygame.BLEND_ADD)

        # 3. Events (Deaths, Explosions)
        for x, y, event_type in engine.recent_events:
            if event_type == "kill":
                self._emit_particles(x, y, config.COLOR_ZOMBIE_NORMAL)
            elif event_type == "base_hit":
                self._emit_particles(x, y, config.COLOR_WALL_DAMAGED)
            elif event_type == "explosion":
                # Big explosion
                self._emit_shockwave(x, y)
                for _ in range(10):
                    self.particles.append([x, y, random.uniform(-5,5), random.uniform(-5,5), (255, 100, 0), 30])
            elif event_type == "airdrop":
                # Green particles
                for _ in range(20):
                    self.particles.append([x, y, random.uniform(-8,8), random.uniform(-8,8), (0, 255, 200), 40])

        # 4. Entities
        # Zombies
        for z in engine.zombies:
            color = config.COLOR_ZOMBIE_NORMAL
            if z.type == 'fast': color = config.COLOR_ZOMBIE_FAST
            if z.type == 'tank': color = config.COLOR_ZOMBIE_TANK
            
            # Glow Check
            z_glow = pygame.Surface((int(z.radius*3), int(z.radius*3)), pygame.SRCALPHA)
            pygame.draw.circle(z_glow, (*color, 60), (int(z.radius*1.5), int(z.radius*1.5)), int(z.radius*1.2))
            self.surface.blit(z_glow, (int(z.pos.x - z.radius*1.5), int(z.pos.y - z.radius*1.5)))
            
            # Draw detailed monster
            self._draw_zombie(self.surface, int(z.pos.x), int(z.pos.y), z.type, z.radius, color)
            
        # Soldiers
        for s in engine.soldiers:
            # Draw detailed humanoid
            self._draw_soldier(self.surface, int(s.pos.x), int(s.pos.y), s.type, s.color)

        # Projectiles
        for p in engine.projectiles:
            pygame.draw.circle(self.surface, config.COLOR_PROJECTILE, (int(p.pos.x), int(p.pos.y)), int(p.radius))
            # Trail line
            pygame.draw.line(self.surface, config.COLOR_PROJECTILE, (int(p.pos.x), int(p.pos.y)), (int(p.pos.x-10), int(p.pos.y)), 2)

        # 5. HUD - Redesigned
        # Top Header (Stats)
        header_surf = pygame.Surface((self.width, 100), pygame.SRCALPHA)
        header_surf.fill((0, 0, 0, 180)) 
        self.surface.blit(header_surf, (0, 0))

        # Stats (Top)
        text_score = self.font_large.render(f"KILLS: {engine.zombies_defeated}", True, config.COLOR_TEXT_MAIN)
        self.surface.blit(text_score, (50, 25))
        
        text_money = self.font_large.render(f"$ {engine.money:,}", True, config.COLOR_GOLD)
        money_rect = text_money.get_rect(topright=(self.width - 50, 25))
        self.surface.blit(text_money, money_rect)
        
        # Base Health Bar (BOTTOM)
        bar_width = self.width - 100
        bar_height = 40
        bar_x = 50
        bar_y = self.height - 80
        
        # Bar Background
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.surface, (30, 0, 0), bg_rect, border_radius=10)
        pygame.draw.rect(self.surface, (255, 255, 255), bg_rect, 3, border_radius=10) # Border
        
        # Health Fill
        pct = max(0, engine.base_health / config.BASE_MAX_HEALTH)
        fill_width = int(bar_width * pct)
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(self.surface, config.COLOR_HP_BAR_FG, fill_rect, border_radius=10)
        
        # Text "BASE INTEGRITY"
        text_hp = self.font_small.render(f"BASE INTEGRITY: {int(pct*100)}%", True, (255, 255, 255))
        text_rect = text_hp.get_rect(center=(self.width//2, bar_y - 25))
        
        # Shadow for text
        text_shadow = self.font_small.render(f"BASE INTEGRITY: {int(pct*100)}%", True, (0, 0, 0))
        shadow_rect = text_rect.copy()
        shadow_rect.x += 2; shadow_rect.y += 2
        self.surface.blit(text_shadow, shadow_rect)
        self.surface.blit(text_hp, text_rect)

        # 6. Game Over / Win Screens
        if engine.game_result != "PLAYING":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.surface.blit(overlay, (0,0))
            
            msg = "BASE DESTROYED" if engine.game_result == "LOSE" else "VICTORY ACHIEVED"
            color = (255, 0, 0) if engine.game_result == "LOSE" else (0, 255, 0)
            
            text_end = self.font_large.render(msg, True, color)
            rect = text_end.get_rect(center=(self.width//2, self.height//2))
            self.surface.blit(text_end, rect)

        # Bottom "Fake Ad" UI
        # Only if we want that aesthetic. Let's keep it clean for now, maybe just upgrades.
        
    def get_frame_data(self):
        """Returns the raw byte strings for the current frame (RGB)"""
        return pygame.image.tostring(self.surface, 'RGB')
