import pygame
import os
import math
import random
from typing import List
from . import config # Importa o módulo inteiro para acessar flags dinâmicas como DEBUG
from .config import WIDTH, HEIGHT, FPS, DURATION, HEADLESS, COLORS, BALANCE
from .assets import AssetManager
from .components import Camera, Particle, FloatingText, Shockwave, VirtualCursor
from .entities import Enemy, Tower, Projectile
from .director import Director
from .grid import Grid
from .recorder import VideoRecorder
from .bot import BotController
from .physics import PhysicsEngine

class Game:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error:
            print("⚠️ Áudio não disponível (Headless?), usando driver dummy.")
            os.environ["SDL_AUDIODRIVER"] = "dummy"
            pygame.mixer.init()
            
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Fortress Merge: Modular")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.assets = AssetManager(HEADLESS)
        self.camera = Camera()
        self.director = Director()
        self.grid = Grid()
        self.bot = BotController() 
        self.physics = PhysicsEngine(self) 
        
        self.frame_count = 0 
        
        # Gravador
        self.recorder = VideoRecorder()
        if HEADLESS:
            self.recorder.start()
        
        # --- Estado do Jogo ---
        self.towers: List[Tower] = []
        self.enemies: List[Enemy] = []
        self.projectiles: List[Projectile] = []
        self.particles: List[Particle] = []
        self.shockwaves: List[Shockwave] = []
        self.floating_texts: List[FloatingText] = []
        
        self.gold = BALANCE["GOLD_START"]
        self.tower_cost = BALANCE["TOWER_COST"]
        self.base_hp = BALANCE["BASE_HP"]
        self.wave_active = False
        self.spawn_timer = 0
        self.victory = False
        self.game_over = False
        self.base_rotation = 0
        
        # --- Humanização & Dopamina ---
        self.cursor = VirtualCursor()
        self.combo = 0
        self.combo_timer = 0

        # --- Visual Juice ---
        # 1. Background Pattern (Procedural Texture)
        self.bg_pattern = pygame.Surface((WIDTH, HEIGHT))
        self.bg_pattern.fill(COLORS["BG"])
        for _ in range(100):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            alpha = random.randint(20, 100)
            pygame.draw.circle(self.bg_pattern, (*COLORS["WHITE"][:3], alpha), (x, y), random.randint(1, 3))
        
        self.bg_scroll_y = 0
        
        # 2. Vignette (Dark corners)
        self.vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self.vignette, (0,0,0,100), self.vignette.get_rect())
        pygame.draw.circle(self.vignette, (0,0,0,0), (WIDTH//2, HEIGHT//2), int(WIDTH*0.6))
        
        # Scanlines
        self.scanlines = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(self.scanlines, (0, 0, 0, 30), (0, y), (WIDTH, y))

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.update()
            self.draw()
            self.handle_input()
        
        if HEADLESS:
            self.recorder.stop()
        pygame.quit()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    config.DEBUG = not config.DEBUG
                    print(f"DEBUG Mode: {config.DEBUG}")

    def update(self):
        self.frame_count += 1
        self.camera.update()
        
        # --- Bot de Auto Play ---
        self.bot.update(self)
        self.cursor.update()
        
        # Combo Logic
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0

        # --- Ondas ---
        if not self.wave_active and not self.victory and not self.game_over:
            if self.director.current_wave <= self.director.total_waves:
                self.wave_active = True
                self.director.enemies_spawned_in_wave = 0
                self.director.enemies_per_wave += 2
            else:
                self.victory = True

        if self.wave_active:
            self.spawn_timer += 1
            rate = max(BALANCE["SPAWN_RATE_MIN"], BALANCE["SPAWN_RATE_BASE"] - (self.director.current_wave * BALANCE["SPAWN_RATE_DECAY"]))
            if self.spawn_timer > rate:
                hp, spd, type_ = self.director.calculate_enemy_stats(self.towers, self.director.current_wave)
                self.enemies.append(Enemy(hp, spd, type_))
                self.director.enemies_spawned_in_wave += 1
                self.spawn_timer = 0
                if self.director.enemies_spawned_in_wave >= self.director.enemies_per_wave:
                    self.wave_active = False
                    self.director.current_wave += 1

        # --- Física e Colisão ---
        self.physics.check_base_damage()
        
        for t in self.towers:
            t.update(self.enemies, self.projectiles, self.assets)

        self.physics.check_collisions()

        if self.base_hp <= 0: self.game_over = True
        
        # Limpeza
        for pt in self.particles[:]:
            if not pt.update(): self.particles.remove(pt)
        for sw in self.shockwaves[:]:
            if not sw.update(): self.shockwaves.remove(sw)
        for ft in self.floating_texts[:]:
            if not ft.update(): self.floating_texts.remove(ft)

        # Encerramento
        end_condition = self.game_over or (self.victory and len(self.enemies) == 0)
        if end_condition:
            if not hasattr(self, 'end_timer'): 
                self.end_timer = 0
                if self.victory: self.assets.play_sfx("victory")
            self.end_timer += 1
            if self.end_timer > FPS * 2:
                self.running = False

    def draw(self):
        # 1. Background
        self.bg_scroll_y = (self.bg_scroll_y + 0.5) % HEIGHT
        self.screen.blit(self.bg_pattern, (0, self.bg_scroll_y))
        self.screen.blit(self.bg_pattern, (0, self.bg_scroll_y - HEIGHT))
        
        offset = self.camera.get_offset()
        self.grid.draw(self.screen, offset)

        # Base
        self.base_rotation += BALANCE["BASE_ROTATION_SPEED"]
        cx, cy = WIDTH//2 + offset[0], HEIGHT//2 + offset[1]
        
        pygame.draw.circle(self.screen, (30, 40, 60), (cx, cy), int(WIDTH*0.14))
        pygame.draw.circle(self.screen, (0, 0, 0), (cx, cy), int(WIDTH*0.13)) 
        
        for i in range(0, 360, 90):
            rad = math.radians(i - self.base_rotation)
            sx = cx + math.cos(rad) * (WIDTH*0.135)
            sy = cy + math.sin(rad) * (WIDTH*0.135)
            pygame.draw.circle(self.screen, COLORS["CYAN"], (sx, sy), 3)

        base_color = COLORS["CYAN"]
        if self.base_hp < BALANCE["BASE_HP"] * 0.3:
            base_color = COLORS["RED"] if (self.frame_count // 10) % 2 == 0 else (150, 0, 0)
        
        pygame.draw.circle(self.screen, (20, 20, 30), (cx, cy), int(WIDTH*0.065)) 
        pygame.draw.circle(self.screen, base_color, (cx, cy), int(WIDTH*0.06), 3)  
        
        rad = math.radians(self.base_rotation)
        ex = cx + math.cos(rad) * (WIDTH*0.055)
        ey = cy + math.sin(rad) * (WIDTH*0.055)
        pygame.draw.line(self.screen, base_color, (cx, cy), (ex, ey), 2)

        # HUD Base
        hp_pct = max(0, self.base_hp / BALANCE["BASE_HP"])
        bar_w, bar_h = WIDTH * 0.2, 8
        bar_x, bar_y = cx - bar_w // 2, cy + WIDTH * 0.08
        pygame.draw.rect(self.screen, (30, 0, 0), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        pygame.draw.rect(self.screen, COLORS["GREEN"] if hp_pct > 0.5 else COLORS["RED"], 
                         (bar_x, bar_y, bar_w * hp_pct, bar_h), border_radius=4)

        # Entidades
        for e in self.enemies: e.draw(self.screen, offset, self.assets.get_font("ui"))
        for t in self.towers: t.draw(self.screen, offset, self.assets.get_font("ui"))
        for p in self.projectiles: p.draw(self.screen, offset)
        for pt in self.particles: pt.draw(self.screen, offset)
        for sw in self.shockwaves: sw.draw(self.screen, offset)
        for ft in self.floating_texts: ft.draw(self.screen, offset)
        
        # Draw Cursor (UI Layer)
        self.cursor.draw(self.screen)

        # UI
        ui_font = self.assets.get_font("ui")
        
        # COMBO Display
        if self.combo > 1:
            scale_pulse = 1.0 + (math.sin(self.frame_count * 0.5) * 0.1)
            combo_txt = self.assets.get_font("title").render(f"COMBO x{self.combo}!", True, COLORS["GOLD"])
            
            # Center, slightly above center
            w = combo_txt.get_width()
            h = combo_txt.get_height()
            scaled_w = int(w * scale_pulse)
            scaled_h = int(h * scale_pulse)
            
            combo_scaled = pygame.transform.scale(combo_txt, (scaled_w, scaled_h))
            combo_rect = combo_scaled.get_rect(center=(WIDTH//2, HEIGHT*0.3))
            
            # Shadow
            shadow_s = pygame.transform.scale(combo_txt, (scaled_w, scaled_h))
            shadow_s.fill((0,0,0), special_flags=pygame.BLEND_RGBA_MULT) 
            self.screen.blit(shadow_s, (combo_rect.x+4, combo_rect.y+4))
            
            self.screen.blit(combo_scaled, combo_rect)

        wave_txt = ui_font.render(f"WAVE {min(self.director.current_wave, self.director.total_waves)}", True, COLORS["WHITE"])
        self.screen.blit(wave_txt, wave_txt.get_rect(midtop=(WIDTH//2, 20)))
        
        gold_txt = ui_font.render(f"$ {self.gold}", True, COLORS["GOLD"])
        self.screen.blit(gold_txt, (WIDTH - gold_txt.get_width() - 20, 20))

        if self.game_over:
            over_txt = self.assets.get_font("title").render("DEFEAT", True, COLORS["RED"])
            self.screen.blit(over_txt, over_txt.get_rect(center=(WIDTH//2, HEIGHT//2)))
        elif self.victory and len(self.enemies) == 0:
            win_txt = self.assets.get_font("title").render("VICTORY!", True, COLORS["GREEN"])
            self.screen.blit(win_txt, win_txt.get_rect(center=(WIDTH//2, HEIGHT//2)))

        if HEADLESS:
            self.recorder.capture(self.screen)

        # Overlays
        if self.base_hp < BALANCE["BASE_HP"] * 0.3:
            pulse = (math.sin(self.frame_count * 0.2) + 1) * 0.5
            pulse_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(pulse_surf, (255, 0, 0, int(50 * pulse)), pulse_surf.get_rect())
            self.screen.blit(pulse_surf, (0,0), special_flags=pygame.BLEND_ADD)
            
        self.screen.blit(self.vignette, (0,0), special_flags=pygame.BLEND_MULT) 
        self.screen.blit(self.scanlines, (0,0))

        pygame.display.flip()
