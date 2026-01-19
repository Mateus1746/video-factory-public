import pygame
import math
import json
import argparse
import sys
import random

# --- CONFIGURAÇÃO GLOBAL ---
WIDTH, HEIGHT = 1080, 1920
FPS = 60
CENTER_X = WIDTH // 2
GROUND_Y = HEIGHT * 0.75

# --- BASE THEME CLASS ---
class Theme:
    def __init__(self):
        self.bg_color = (0, 0, 0)
        
    def draw_background(self, screen, pulse, shake_offset):
        screen.fill(self.bg_color)

    def draw_grid(self, screen, grid, pulse, shake_offset):
        pass

    def draw_ball(self, screen, pos, radius, scale, color, pulse, shake_offset):
        # Default simple ball
        s_pos = (int(pos.x + shake_offset[0]), int(pos.y + shake_offset[1]))
        pygame.draw.circle(screen, color, s_pos, int(radius * scale[0]))

    def draw_particles(self, screen, particles, shake_offset):
        for p in particles:
            p.draw(screen, shake_offset)
            
    def draw_trail(self, screen, trail, shake_offset):
        pass

    def create_particles(self, pos, sub_bass, color):
        return []

# --- NEON TOKYO (CLASSIC) ---
class NeonTheme(Theme):
    def __init__(self):
        self.bg_color = (8, 8, 12)
        self.grid_color = (40, 0, 60)
        self.grid_highlight = (100, 20, 140)

    def draw_background(self, screen, pulse, shake_offset):
        screen.fill(self.bg_color)
        ox, oy = shake_offset
        
        # Glow Central
        center_glow_size = int(WIDTH * (0.8 + pulse * 0.2))
        glow_surf = pygame.Surface((center_glow_size*2, center_glow_size*2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (20, 10, 40, 50), (center_glow_size, center_glow_size), center_glow_size)
        screen.blit(glow_surf, (WIDTH//2 - center_glow_size + ox, HEIGHT//2 - center_glow_size + oy), special_flags=pygame.BLEND_ADD)

    def draw_grid(self, screen, grid, pulse, shake_offset):
        ox, oy = shake_offset
        # Dynamic Grid Color
        c_r = min(255, self.grid_highlight[0] + int(pulse * 100))
        c_g = min(255, self.grid_highlight[1] + int(pulse * 50))
        c_b = min(255, self.grid_highlight[2] + int(pulse * 100))
        grid_c = (c_r, c_g, c_b)
        
        # Draw the grid object's logic (reusing existing Grid class logic within Theme)
        # Perspective lines
        vanishing_y = GROUND_Y
        num_v_lines = 12
        for i in range(num_v_lines + 1):
            x_base = (WIDTH * 2) * (i / num_v_lines) - (WIDTH * 0.5)
            start_pos = (int(x_base + ox), int(HEIGHT + oy))
            end_pos = (int(CENTER_X + (x_base - CENTER_X) * 0.2 + ox), int(vanishing_y + oy))
            pygame.draw.line(screen, grid_c, end_pos, start_pos, 2)
            
        # Horizontal lines
        num_h_lines = 10
        for i in range(num_h_lines):
            p = (i + (grid.offset_y / 100.0)) / num_h_lines
            depth = p * p * p 
            y_pos = vanishing_y + (depth * (HEIGHT - vanishing_y))
            if y_pos > vanishing_y:
                width_factor = 0.2 + (depth * 0.8)
                x_left = CENTER_X - (WIDTH * width_factor)
                x_right = CENTER_X + (WIDTH * width_factor)
                thickness = max(1, int(depth * 4))
                alpha = int(depth * 255)
                c = (*grid_c[:3], alpha)
                
                # Manual Alpha Line Trick (simplified)
                if thickness > 0:
                    pygame.draw.line(screen, c, (x_left+ox, y_pos+oy), (x_right+ox, y_pos+oy), thickness)

        # Ground Line with Glow
        pygame.draw.rect(screen, grid_c, (0, GROUND_Y-2, WIDTH, 4))
        if pulse > 0.1:
            glow_h = int(10 * pulse)
            s_line = pygame.Surface((WIDTH, glow_h*2), pygame.SRCALPHA)
            s_line.fill((0,0,0,0))
            pygame.draw.rect(s_line, (*grid_c, 100), (0, 0, WIDTH, glow_h*2))
            screen.blit(s_line, (0, GROUND_Y - glow_h + oy), special_flags=pygame.BLEND_ADD)

    def draw_ball(self, screen, pos, radius, scale, color, pulse, shake_offset):
        ox, oy = shake_offset
        rw = radius * scale[0]
        rh = radius * scale[1]
        
        ball_surf_w = int(radius * 3)
        ball_surf_h = int(radius * 3)
        ball_surf = pygame.Surface((ball_surf_w, ball_surf_h), pygame.SRCALPHA)
        cx, cy = ball_surf_w // 2, ball_surf_h // 2
        
        # Glow
        glow_size = max(rw, rh) * (1.5 + pulse * 0.5)
        pygame.draw.ellipse(ball_surf, (*color, 60), (cx - glow_size, cy - glow_size, glow_size*2, glow_size*2))
        
        # Core
        pygame.draw.ellipse(ball_surf, color, (cx - rw, cy - rh, rw*2, rh*2))
        # Highlight
        pygame.draw.ellipse(ball_surf, (255, 255, 255), (cx - rw*0.5, cy - rh*0.5, rw*0.6, rh*0.4))
        
        screen.blit(ball_surf, (pos.x - cx + ox, pos.y - cy + oy), special_flags=pygame.BLEND_ADD)

    def draw_trail(self, screen, trail, shake_offset):
        ox, oy = shake_offset
        if len(trail) < 2: return
        
        # Draw polygon ribbon
        left_pts, right_pts = [], []
        for i, (t_pos, t_color, t_radius) in enumerate(trail):
            alpha = 150 - (i * 6)
            if alpha <= 0: break
            w = t_radius * (1 - i/30.0)
            left_pts.append((t_pos.x - w + ox, t_pos.y + oy))
            right_pts.append((t_pos.x + w + ox, t_pos.y + oy))
            
        for i in range(len(left_pts) - 1):
             c = trail[i][1]
             poly = [left_pts[i], right_pts[i], right_pts[i+1], left_pts[i+1]]
             pygame.draw.polygon(screen, c, poly)

    def create_particles(self, pos, sub_bass, color):
        new_parts = []
        num = int(15 + (sub_bass * 40))
        for _ in range(num):
             p_type = random.choice(["circle", "circle", "spark"])
             if sub_bass > 0.6 and random.random() < 0.2: p_type = "ring"
             size = random.randint(3, 10)
             speed = 8 + (sub_bass * 15)
             new_parts.append(Particle(pos.x, GROUND_Y, color, speed, size, 45, p_type))
        return new_parts

# --- ZEN GARDEN (SOFT/ORGANIC) ---
class ZenTheme(Theme):
    def __init__(self):
        super().__init__()
        # Gradient Sky colors (Top, Bottom)
        self.sky_top = (135, 206, 250) # Sky Blue
        self.sky_bot = (255, 182, 193) # Light Pink
        
    def draw_background(self, screen, pulse, shake_offset):
        # Draw Gradient
        # Simple optimization: draw fixed rects or pre-calc texture. 
        # For Pygame dynamic:
        h = HEIGHT
        for i in range(0, h, 20):
            factor = i / h
            r = self.sky_top[0] + (self.sky_bot[0] - self.sky_top[0]) * factor
            g = self.sky_top[1] + (self.sky_bot[1] - self.sky_top[1]) * factor
            b = self.sky_top[2] + (self.sky_bot[2] - self.sky_top[2]) * factor
            pygame.draw.rect(screen, (r,g,b), (0, i, WIDTH, 20))
            
        # Sun / Moon
        pygame.draw.circle(screen, (255, 255, 240, 100), (WIDTH//2, int(HEIGHT*0.3)), int(150 + pulse*20))

    def draw_grid(self, screen, grid, pulse, shake_offset):
        # Water Reflection / Ground
        # Just a flat colored surface with some alpha waves
        water_rect = pygame.Rect(0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y)
        pygame.draw.rect(screen, (70, 130, 180), water_rect) # Steel Blue
        
        # Ripples
        ox, oy = shake_offset
        for i in range(5):
             y = GROUND_Y + 50 + (i * 100) + (grid.offset_y * 2)
             if y > HEIGHT: y -= (HEIGHT - GROUND_Y)
             pygame.draw.aaline(screen, (255,255,255), (0, y+oy), (WIDTH, y+oy))

    def draw_ball(self, screen, pos, radius, scale, color, pulse, shake_offset):
        ox, oy = shake_offset
        rw = radius * scale[0]
        rh = radius * scale[1]
        
        # Bubble Style
        ball_surf = pygame.Surface((int(rw*4), int(rh*4)), pygame.SRCALPHA)
        cx, cy = int(rw*2), int(rh*2)
        
        # Soft core
        pygame.draw.ellipse(ball_surf, (*color, 200), (cx-rw, cy-rh, rw*2, rh*2))
        # Rim light
        pygame.draw.ellipse(ball_surf, (255,255,255), (cx-rw, cy-rh, rw*2, rh*2), width=4)
        # Shine
        pygame.draw.ellipse(ball_surf, (255,255,255), (cx-rw*0.5, cy-rh*0.6, rw*0.5, rh*0.3))
        
        screen.blit(ball_surf, (pos.x - cx + ox, pos.y - cy + oy))

    def draw_trail(self, screen, trail, shake_offset):
        ox, oy = shake_offset
        # Bubble trail
        for i, (t_pos, t_color, t_radius) in enumerate(trail):
            if i % 3 != 0: continue # Sparse trail
            alpha = int(100 - (i * 3))
            if alpha <= 0: break
            
            s = pygame.Surface((int(t_radius*2), int(t_radius*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (255,255,255, alpha), (int(t_radius), int(t_radius)), int(t_radius), width=1)
            screen.blit(s, (t_pos.x - t_radius + ox, t_pos.y - t_radius + oy))

    def create_particles(self, pos, sub_bass, color):
        # Floating Bubbles
        new_parts = []
        num = int(5 + (sub_bass * 10))
        for _ in range(num):
             size = random.randint(5, 20)
             speed = 2 + (sub_bass * 5)
             # Custom 'bubble' type handler in particle update needed, or just standard circle with slow gravity
             p = Particle(pos.x, GROUND_Y, (255,255,255), speed, size, 120, "bubble")
             new_parts.append(p)
        return new_parts


# --- GLITCH CORE (CHAOS) ---
class GlitchTheme(Theme):
    def __init__(self):
        self.bg_color = (10, 0, 0)
        
    def draw_background(self, screen, pulse, shake_offset):
        if random.random() < 0.05 + (pulse * 0.1):
             # flash inverted
             screen.fill((230, 230, 230))
        else:
             screen.fill(self.bg_color)
             
        # Random matrix-like chars or lines?
        if pulse > 0.5:
             for _ in range(5):
                 w = random.randint(10, 200)
                 h = random.randint(2, 10)
                 x = random.randint(0, WIDTH)
                 y = random.randint(0, HEIGHT)
                 pygame.draw.rect(screen, (255, 0, 0), (x,y,w,h))

    def draw_grid(self, screen, grid, pulse, shake_offset):
        # Wireframe messy
        ox, oy = shake_offset
        off = grid.offset_y
        
        color = (0, 255, 0) if random.random() > 0.1 else (255, 0, 255)
        if pulse > 0.4: color = (255, 255, 255)
        
        for i in range(0, HEIGHT, 80):
             start = (0, i + off + oy)
             end = (WIDTH, i + off + oy)
             if random.random() > 0.8: # Skipping lines
                 continue
             pygame.draw.line(screen, color, start, end, 1)
             
        # Vertical jitter
        for i in range(0, WIDTH, 100):
             x = i + random.randint(-5, 5) + ox
             pygame.draw.line(screen, color, (x, GROUND_Y), (x, HEIGHT), 1)

    def draw_ball(self, screen, pos, radius, scale, color, pulse, shake_offset):
        ox, oy = shake_offset
        # Split channels (RGB Split effect)
        offsets = [(-4, 0, (255, 0, 0)), (4, 0, (0, 255, 255)), (0, 0, (255, 255, 255))]
        
        for dx, dy, c in offsets:
            distort_x = 0
            if pulse > 0.3:
                 distort_x = random.randint(-10, 10)
            
            p = (int(pos.x + ox + dx + distort_x), int(pos.y + oy + dy))
            r = int(radius * scale[0])
            # Draw Square instead of circle
            pygame.draw.rect(screen, c, (p[0]-r, p[1]-r, r*2, r*2))

    def draw_trail(self, screen, trail, shake_offset):
        # Digital Glitch blocks
        for i, (t_pos, t_color, t_radius) in enumerate(trail):
            if i % 2 == 0: continue
            r = int(t_radius)
            pygame.draw.rect(screen, t_color, (t_pos.x - r, t_pos.y-r, r*2, r*2), 1)

    def create_particles(self, pos, sub_bass, color):
        # Squares
        new_parts = []
        num = int(10 + (sub_bass * 30))
        for _ in range(num):
             size = random.randint(2, 12)
             speed = 10 + (sub_bass * 20)
             p = Particle(pos.x, GROUND_Y, (255,0,0), speed, size, 30, "square")
             new_parts.append(p)
        return new_parts

# --- SHARED ENTITIES ---
class Particle:
    def __init__(self, x, y, color, speed, size, life, p_type="circle"):
        self.x, self.y = x, y
        self.color = color
        angle = random.uniform(math.pi, 2 * math.pi)
        if random.random() < 0.5: angle = random.uniform(math.pi * 1.1, math.pi * 1.9)
        speed_var = speed * random.uniform(0.5, 2.0)
        self.vx = math.cos(angle) * speed_var
        self.vy = math.sin(angle) * speed_var
        self.size = size
        self.life = life
        self.max_life = life
        self.gravity = 0.4
        self.type = p_type

        # Bubble fix: float up
        if self.type == "bubble":
             self.gravity = -0.1
             self.vy = random.uniform(-2, -5)
             self.vx = random.uniform(-1, 1)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
        
        if self.type == "spark": self.size *= 0.9
        elif self.type == "ring": 
            self.size += 1.5 
            self.life -= 1
        elif self.type == "bubble":
            self.vx += random.uniform(-0.1, 0.1) # Wiggle
        else: self.size *= 0.96

    def draw(self, screen, shake_offset):
        if self.life <= 0: return
        alpha = int((self.life / self.max_life) * 255)
        dx, dy = shake_offset
        pos = (int(self.x + dx), int(self.y + dy))
        
        if self.type == "ring":
             if self.size > 2:
                 pygame.draw.circle(screen, (*self.color, alpha), pos, int(self.size), 2)
        elif self.type == "spark":
             off = int(self.size)
             pts = [(pos[0], pos[1]-off), (pos[0]+off, pos[1]), (pos[0], pos[1]+off), (pos[0]-off, pos[1])]
             pygame.draw.polygon(screen, (*self.color, alpha), pts)
        elif self.type == "square":
             sz = int(self.size)
             pygame.draw.rect(screen, (*self.color, alpha), (pos[0]-sz, pos[1]-sz, sz*2, sz*2))
        else: # circle/bubble
             s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
             pygame.draw.circle(s, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
             screen.blit(s, (int(pos[0]-self.size), int(pos[1]-self.size)), special_flags=pygame.BLEND_ADD)

class Grid:
    def __init__(self):
        self.offset_y = 0.0
        self.speed = 2.0
    def update(self, speed_boost):
        self.offset_y += self.speed + (speed_boost * 10)
        if self.offset_y >= 100: self.offset_y = 0

class Player:
    def __init__(self, json_path, audio_path, theme_name="neon", preview_mode=True):
        try:
            with open(json_path, 'r') as f: self.data = json.load(f)
            self.beats = self.data['beats']
            self.duration = self.data['metadata']['duration']
        except:
             sys.exit(1)

        self.theme = self._get_theme(theme_name)
        print(f"🎨 Theme Selected: {theme_name}")

        self.ball_radius_base = 40
        self.ball_pos = pygame.Vector2(CENTER_X, GROUND_Y - self.ball_radius_base)
        self.ball_color = (255, 0, 100)
        self.trail = []
        self.particles = []
        self.velocity_y = 0
        self.scale_x, self.scale_y = 1.0, 1.0
        self.grid = Grid()
        self.shake_amount = 0.0
        self.pulse = 0.0
        self.last_beat_idx = -1
        self.current_bands = [0, 0, 0, 0]
        
        if preview_mode:
            pygame.mixer.init()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            self.start_ticks = pygame.time.get_ticks()
        else:
            self.start_ticks = 0

    def _get_theme(self, name):
        if name == "zen": return ZenTheme()
        if name == "glitch": return GlitchTheme()
        return NeonTheme()

    def get_current_time(self):
        return (pygame.time.get_ticks() - self.start_ticks) / 1000.0

    def update(self, manual_time=None):
        t = manual_time if manual_time is not None else self.get_current_time()
        
        # Audio & Physics Logic (Kept Identical to V1 to preserve sync)
        next_beat_idx = 0
        for i, beat in enumerate(self.beats):
            if beat['timestamp'] > t:
                next_beat_idx = i
                break
        else: next_beat_idx = len(self.beats)
        if next_beat_idx >= len(self.beats): return

        prev_beat = self.beats[next_beat_idx - 1] if next_beat_idx > 0 else self.beats[0]
        next_beat = self.beats[next_beat_idx]
        
        self.current_bands = prev_beat.get('energy_bands', [0,0,0,0])
        sub_bass = self.current_bands[0]
        
        start_time = prev_beat['timestamp']
        end_time = next_beat['timestamp']
        total_interval = end_time - start_time
        progress = (t - start_time) / total_interval if total_interval > 0 else 1.0
        progress = max(0.0, min(1.0, progress))
        
        jump_height = 300 + (sub_bass * 250)
        if isinstance(self.theme, ZenTheme): jump_height *= 0.8 # Gentle hop in Zen
        
        height_y = 4 * jump_height * progress * (1 - progress)
        self.ball_pos.y = GROUND_Y - self.ball_radius_base - height_y
        
        norm_vel = (1 - 2 * progress)
        stretch_amount = 0.3 * abs(norm_vel) * (1 + sub_bass)
        self.scale_y = 1.0 + stretch_amount
        self.scale_x = 1.0 - (stretch_amount * 0.5)
        
        impact_zone = 0.1
        if progress < impact_zone or progress > (1 - impact_zone):
             sq = (impact_zone - progress)/impact_zone if progress < impact_zone else (progress - (1-impact_zone))/impact_zone
             self.scale_y = 1.0 - (sq * 0.4 * (1+sub_bass))
             self.scale_x = 1.0 + (sq * 0.4 * (1+sub_bass))

        # Beat Trigger
        if next_beat_idx != self.last_beat_idx:
            self.last_beat_idx = next_beat_idx
            
            c_hex = prev_beat.get('color_hex', '#FF0064').lstrip('#')
            self.ball_color = tuple(int(c_hex[i:i+2], 16) for i in (0, 2, 4))
            
            if sub_bass > 0.3: self.shake_amount = 15.0 * sub_bass
            
            # Delegate particle creation to theme
            new_p = self.theme.create_particles(self.ball_pos, sub_bass, self.ball_color)
            self.particles.extend(new_p)
            
            self.pulse = 1.0

        self.grid.update(sub_bass)
        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        
        if len(self.trail) == 0 or self.ball_pos.distance_to(self.trail[0][0]) > 5:
            self.trail.insert(0, (pygame.Vector2(self.ball_pos), self.ball_color, self.scale_x * self.ball_radius_base))
        if len(self.trail) > 25: self.trail.pop()
        
        self.pulse *= 0.92
        self.shake_amount *= 0.85

    def draw(self, screen):
        ox = random.uniform(-self.shake_amount, self.shake_amount)
        oy = random.uniform(-self.shake_amount, self.shake_amount)
        shake_offset = (ox, oy)
        
        # Delegate drawing to Theme
        self.theme.draw_background(screen, self.pulse, shake_offset)
        self.theme.draw_grid(screen, self.grid, self.pulse, shake_offset)
        
        # Reflections (Custom per theme? Kept simple for now)
        # Assuming theme handles particle drawing, but reflections are global mechanic for now unless moved
        # Let's keep reflections generic but use theme.draw_particles for them (maybe too complex).
        # We'll just draw particles normally.
        
        self.theme.draw_particles(screen, self.particles, shake_offset)
        self.theme.draw_trail(screen, self.trail, shake_offset)
        self.theme.draw_ball(screen, self.ball_pos, self.ball_radius_base, (self.scale_x, self.scale_y), self.ball_color, self.pulse, shake_offset)
        
        # Progress Bar (Global)
        bar_h = 8
        fill_w = int((self.get_current_time() / self.duration) * WIDTH)
        pygame.draw.rect(screen, (30, 30, 30), (0, 0, WIDTH, bar_h))
        pygame.draw.rect(screen, self.ball_color, (0, 0, fill_w, bar_h))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("audio")
    parser.add_argument("json")
    parser.add_argument("--theme", default="neon", help="neon, zen, glitch")
    args = parser.parse_args()

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
    pygame.display.set_caption(f"Vibe Geometry - {args.theme.upper()}")
    clock = pygame.time.Clock()
    
    player = Player(args.json, args.audio, theme_name=args.theme)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False

        player.update()
        player.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()