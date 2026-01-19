import pygame
import os
import math
import random
from typing import List
from . import config # Importa o módulo inteiro para acessar flags dinâmicas como DEBUG
from .config import WIDTH, HEIGHT, FPS, DURATION, HEADLESS, OUTPUT_DIR, COLORS, BALANCE
from .assets import AssetManager
from .components import Camera, Particle, FloatingText
from .entities import Enemy, Tower, Projectile
from .director import Director
from .grid import Grid
from .recorder import VideoRecorder
from .bot import BotController

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
        self.bot = BotController() # Inicializa o Bot
        
        self.frame_count = 0 # Restaurando contador de frames
        
        # Gravador
        self.recorder = VideoRecorder()
        if HEADLESS:
            self.recorder.start()
        
        # Estado
        self.towers: List[Tower] = []
        self.enemies: List[Enemy] = []
        self.projectiles: List[Projectile] = []
        self.particles: List[Particle] = []
        self.floating_texts: List[FloatingText] = []
        
        self.gold = BALANCE["GOLD_START"]
        self.tower_cost = BALANCE["TOWER_COST"]
        self.base_hp = BALANCE["BASE_HP"]
        self.wave_active = False
        self.spawn_timer = 0
        self.victory = False
        self.game_over = False
        self.base_rotation = 0

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.update()
            self.draw()
            self.handle_input()
        
        # Encerramento seguro
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
            rate = max(15, 60 - (self.director.current_wave * 5))
            if self.spawn_timer > rate:
                hp, spd, type_ = self.director.calculate_enemy_stats(self.towers, self.director.current_wave)
                self.enemies.append(Enemy(hp, spd, type_))
                self.director.enemies_spawned_in_wave += 1
                self.spawn_timer = 0
                if self.director.enemies_spawned_in_wave >= self.director.enemies_per_wave:
                    self.wave_active = False
                    self.director.current_wave += 1

        # --- Física ---
        for e in self.enemies[:]:
            if e.move():
                self.base_hp -= 15
                self.enemies.remove(e)
                self.assets.play_sfx("hit")
                self.camera.shake(20)
                for _ in range(20): self.particles.append(Particle(e.x, e.y, COLORS["RED"], 8))
            elif e.hp <= 0:
                reward = 25 * self.director.current_wave
                if e.type == "boss": reward *= 5
                self.gold += int(reward)
                self.enemies.remove(e)
                self.assets.play_sfx("explosion")
                self.camera.shake(5)
                color = COLORS["GOLD"] if e.type == "boss" else COLORS["RED"]
                for _ in range(10): self.particles.append(Particle(e.x, e.y, color, 6))
                self.floating_texts.append(FloatingText(e.x, e.y, f"+{int(reward)}", COLORS["GOLD"], self.assets.get_font("dmg")))

        # Update Torres
        for t in self.towers:
            t.update(self.enemies, self.projectiles, self.assets)

        # Update Projéteis (Refatorado + Variantes)
        for p in self.projectiles[:]:
            alive = p.update() # Retorna False se sair da tela
            hit = False
            
            if alive:
                for e in self.enemies:
                    if math.hypot(e.x - p.x, e.y - p.y) < e.radius + 40:
                        hit = True
                        
                        # Lógica de Impacto Baseada no Tipo
                        if p.type == "fire":
                            # Dano em Área (AOE)
                            self.assets.play_sfx("explosion") # Som extra para fogo
                            for neighbor in self.enemies:
                                if math.hypot(neighbor.x - p.x, neighbor.y - p.y) < 150: # Raio da explosão
                                    neighbor.take_damage(p.damage * 0.8, "fire")
                            
                            # Partículas de explosão
                            for _ in range(8):
                                self.particles.append(Particle(p.x, p.y, (255, 100, 0), 6))
                                
                        else:
                            # Dano Único (Standard ou Ice)
                            e.take_damage(p.damage, p.type)
                            self.particles.append(Particle(p.x, p.y, p.color, 3))
                        
                        self.floating_texts.append(FloatingText(e.x, e.y - 30, f"-{int(p.damage)}", COLORS["WHITE"], self.assets.get_font("dmg")))
                        break
            
            if hit or not alive:
                self.projectiles.remove(p)

        if self.base_hp <= 0: self.game_over = True
        
        # Limpeza
        for pt in self.particles[:]:
            if not pt.update(): self.particles.remove(pt)
        for ft in self.floating_texts[:]:
            if not ft.update(): self.floating_texts.remove(ft)

        # Encerramento Inteligente
        end_condition = self.game_over or (self.victory and len(self.enemies) == 0)
        
        if end_condition:
            if not hasattr(self, 'end_timer'): 
                self.end_timer = 0
                if self.victory: self.assets.play_sfx("victory")
            
            self.end_timer += 1
            if self.end_timer > FPS * 2:
                self.running = False

    def draw(self):
        self.screen.fill(COLORS["BG"])
        offset = self.camera.get_offset()
        
        # Grid (Refatorado)
        self.grid.draw(self.screen, offset)

        # Base (Redesign)
        self.base_rotation += 2
        cx, cy = WIDTH//2 + offset[0], HEIGHT//2 + offset[1]
        
        # 1. Escudo de Energia (Anel externo giratório)
        pygame.draw.circle(self.screen, (30, 40, 60), (cx, cy), int(WIDTH*0.14))
        pygame.draw.circle(self.screen, (0, 0, 0), (cx, cy), int(WIDTH*0.13)) # Buraco do anel
        
        # Detalhes do anel (4 pequenos ticks girando)
        for i in range(0, 360, 90):
            rad = math.radians(i - self.base_rotation) # Gira ao contrário
            sx = cx + math.cos(rad) * (WIDTH*0.135)
            sy = cy + math.sin(rad) * (WIDTH*0.135)
            pygame.draw.circle(self.screen, COLORS["CYAN"], (sx, sy), 3)

        # 2. Núcleo da Base
        # Cor pulsa se estiver com pouco HP
        base_color = COLORS["CYAN"]
        if self.base_hp < BALANCE["BASE_HP"] * 0.3:
            if (self.frame_count // 10) % 2 == 0:
                base_color = COLORS["RED"]
            else:
                base_color = (150, 0, 0)
        
        pygame.draw.circle(self.screen, (20, 20, 30), (cx, cy), int(WIDTH*0.065)) # Fundo do núcleo
        pygame.draw.circle(self.screen, base_color, (cx, cy), int(WIDTH*0.06), 3)  # Borda do núcleo
        
        # Radar Scan
        rad = math.radians(self.base_rotation)
        ex = cx + math.cos(rad) * (WIDTH*0.055)
        ey = cy + math.sin(rad) * (WIDTH*0.055)
        pygame.draw.line(self.screen, base_color, (cx, cy), (ex, ey), 2)

        # 3. HUD da Base (HP)
        hp_pct = max(0, self.base_hp / BALANCE["BASE_HP"])
        bar_w = WIDTH * 0.2
        bar_h = 8
        bar_x = cx - bar_w // 2
        bar_y = cy + WIDTH * 0.08
        
        # Fundo da Barra
        pygame.draw.rect(self.screen, (30, 0, 0), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        # Frente da Barra
        pygame.draw.rect(self.screen, COLORS["GREEN"] if hp_pct > 0.5 else COLORS["RED"], 
                         (bar_x, bar_y, bar_w * hp_pct, bar_h), border_radius=4)
        
        # Texto de HP numérico
        hp_font = pygame.font.Font(None, 24)
        hp_txt = hp_font.render(f"{int(self.base_hp)}/{BALANCE['BASE_HP']}", True, COLORS["WHITE"])
        self.screen.blit(hp_txt, hp_txt.get_rect(center=(cx, bar_y + 15)))

        # Entidades
        for e in self.enemies: e.draw(self.screen, offset, self.assets.get_font("ui"))
        for t in self.towers: t.draw(self.screen, offset, self.assets.get_font("ui"))
        
        # Projéteis (Refatorado + Variantes)
        for p in self.projectiles:
            p.draw(self.screen, offset)
        
        for pt in self.particles: pt.draw(self.screen, offset)
        for ft in self.floating_texts: ft.draw(self.screen, offset)

        # UI
        ui_font = self.assets.get_font("ui")
        
        # Wave Bar (Topo Central)
        progress = (self.director.current_wave - 1) / self.director.total_waves
        if self.wave_active:
            progress += (self.director.enemies_spawned_in_wave / self.director.enemies_per_wave) * (1/self.director.total_waves)
        
        # Pequena barra de progresso discreta no topo
        pygame.draw.rect(self.screen, (30,30,40), (WIDTH*0.25, 10, WIDTH*0.5, 6), border_radius=3)
        pygame.draw.rect(self.screen, COLORS["CYAN"], (WIDTH*0.25, 10, WIDTH*0.5 * min(1, progress), 6), border_radius=3)
        
        wave_txt = ui_font.render(f"WAVE {min(self.director.current_wave, self.director.total_waves)}", True, COLORS["WHITE"])
        self.screen.blit(wave_txt, wave_txt.get_rect(midtop=(WIDTH//2, 20)))
        
        # Gold (Canto Superior Direito)
        gold_color = COLORS["GOLD"]
        # Efeito de piscar se tiver dinheiro suficiente para comprar
        if self.gold >= self.tower_cost and (self.frame_count // 30) % 2 == 0:
            gold_color = (255, 255, 150)
            
        gold_txt = ui_font.render(f"$ {self.gold}", True, gold_color)
        # Posiciona no canto direito com margem de 20px
        self.screen.blit(gold_txt, (WIDTH - gold_txt.get_width() - 20, 20))
        
        # Tower Cost (Pequeno, abaixo do Gold)
        cost_txt = pygame.font.Font(None, 24).render(f"NEXT: ${self.tower_cost}", True, (150, 150, 150))
        self.screen.blit(cost_txt, (WIDTH - cost_txt.get_width() - 20, 55))

        if self.game_over:
            over_txt = self.assets.get_font("title").render("DEFEAT", True, COLORS["RED"])
            self.screen.blit(over_txt, over_txt.get_rect(center=(WIDTH//2, HEIGHT//2)))
        elif self.victory and len(self.enemies) == 0:
            win_txt = self.assets.get_font("title").render("VICTORY!", True, COLORS["GREEN"])
            self.screen.blit(win_txt, win_txt.get_rect(center=(WIDTH//2, HEIGHT//2)))

        if HEADLESS:
            self.recorder.capture(self.screen)

        # Debug FPS
        if config.DEBUG:
            fps = int(self.clock.get_fps())
            fps_txt = self.assets.get_font("ui").render(f"FPS: {fps}", True, COLORS["GREEN"])
            self.screen.blit(fps_txt, (10, 10))

        pygame.display.flip()