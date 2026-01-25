import pygame
import math
import random
from typing import List, Optional, Tuple, Any, Deque
from collections import deque
from .config import WIDTH, HEIGHT, COLORS, BALANCE, DEBUG

class Entity:
    _shadow_cache = {} # Class-level cache for shadows by radius

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.scale = 1.0 # Para animações de "Pop"

    def draw_shadow(self, surface: pygame.Surface, offset: Tuple[float, float], radius: float):
        """Desenha uma sombra projetada abaixo da entidade usando cache."""
        ox, oy = offset
        radius_key = int(radius)
        
        if radius_key not in Entity._shadow_cache:
            # Sombra é uma elipse achatada preta com transparência
            shadow_surf = pygame.Surface((radius * 2.2, radius * 0.8), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), shadow_surf.get_rect())
            Entity._shadow_cache[radius_key] = shadow_surf
            
        surface.blit(Entity._shadow_cache[radius_key], (self.x - radius * 1.1 + ox, self.y + radius * 0.5 + oy))

class Projectile(Entity):
    def __init__(self, x: float, y: float, angle: float, damage: float, color: Tuple[int, int, int], p_type: str):
        super().__init__(x, y)
        self.vx = math.cos(angle) * (WIDTH * 0.04)
        self.vy = math.sin(angle) * (WIDTH * 0.04)
        self.damage = damage
        self.color = color
        self.type = p_type # "standard", "ice", "fire"
        self.radius = 6
        
        # Rastro (Trail)
        self.trail: Deque[Tuple[float, float]] = deque(maxlen=8)

    def update(self) -> bool:
        self.trail.appendleft((self.x, self.y)) # Salva posição anterior
        self.x += self.vx
        self.y += self.vy
        return 0 < self.x < WIDTH and 0 < self.y < HEIGHT

    def draw(self, surface: pygame.Surface, offset: Tuple[float, float]):
        ox, oy = offset
        
        # Desenha Rastro
        if len(self.trail) > 1:
            points = [(px + ox, py + oy) for px, py in self.trail]
            points.insert(0, (self.x + ox, self.y + oy))
            # Desenha linhas com transparência simulada (afinamento)
            if len(points) > 2:
                pygame.draw.lines(surface, self.color, False, points, 3)

        # Desenha Núcleo
        pygame.draw.circle(surface, self.color, (int(self.x + ox), int(self.y + oy)), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + ox), int(self.y + oy)), max(2, self.radius-3))

class Enemy(Entity):
    _id_counter = 0

    def __init__(self, hp: float, speed: float, type_: str):
        super().__init__(WIDTH / 2 + random.uniform(-50, 50), -HEIGHT * 0.05)
        self.id = Enemy._id_counter
        Enemy._id_counter += 1
        
        self.max_hp = float(hp)
        self.hp = self.max_hp
        self.base_speed = speed
        self.current_speed = speed
        self.type = type_
        self.radius = WIDTH * 0.035
        self.flash_timer = 0
        
        # Status Effects
        self.slow_timer = 0
        self.frozen_color = (150, 200, 255)
        
        self.target_x = WIDTH // 2
        self.target_y = HEIGHT // 2
        
        if type_ == "tank": self.radius *= 1.5
        elif type_ == "runner": self.radius *= 0.7
        elif type_ == "boss": self.radius *= 2.5

    def take_damage(self, amount: float, damage_type: str = "standard") -> bool:
        self.hp -= amount
        self.flash_timer = 3
        
        if damage_type == "ice":
            self.slow_timer = 60 # 2 segundos a 30 FPS
        
        return self.hp <= 0

    def move(self) -> bool:
        # Lógica de Slow (Gelo)
        speed_mult = 1.0
        if self.slow_timer > 0:
            speed_mult = 0.5
            self.slow_timer -= 1
        
        self.current_speed = self.base_speed * speed_mult

        if self.flash_timer > 0: self.flash_timer -= 1
        
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            self.x += (dx / dist) * self.current_speed
            self.y += (dy / dist) * self.current_speed
            
        return dist < (WIDTH * 0.12)

    def draw(self, surface: pygame.Surface, offset: Tuple[float, float], font: Optional[pygame.font.Font] = None):
        self.draw_shadow(surface, offset, self.radius)
        
        ox, oy = offset
        color = COLORS["RED"]
        if self.type == "runner": color = (255, 150, 0)
        elif self.type == "tank": color = (150, 50, 50)
        elif self.type == "boss": color = (100, 0, 0)
        
        # Efeito Visual de Gelo
        if self.slow_timer > 0:
            color = self.frozen_color

        if self.flash_timer > 0: color = COLORS["WHITE"]

        # Barra de Vida
        hp_pct = max(0.0, self.hp / self.max_hp)
        bar_w = self.radius * 3
        bar_h = 10
        pygame.draw.rect(surface, COLORS["HP_BG"], (self.x - bar_w/2 + ox, self.y - self.radius - 20 + oy, bar_w, bar_h))
        if hp_pct > 0:
            fill_w = max(1, bar_w * hp_pct)
            pygame.draw.rect(surface, COLORS["HP_FG"], (self.x - bar_w/2 + ox, self.y - self.radius - 20 + oy, fill_w, bar_h))

        # Corpo
        pygame.draw.circle(surface, color, (int(self.x + ox), int(self.y + oy)), int(self.radius))
        
        # Detalhe interno
        if self.flash_timer == 0:
            pygame.draw.circle(surface, COLORS["WHITE"], (int(self.x + ox), int(self.y + oy)), int(self.radius*0.7), 2)

class Tower(Entity):
    def __init__(self, level: int, row: int, col: int, grid_system):
        super().__init__(0, 0)
        self.level = level
        self.row = row
        self.col = col
        
        self.x, self.y = grid_system.get_pos(row, col)
        
        # Variantes de Torre
        types = ["standard", "ice", "fire"]
        # Lógica simples: alterna tipos baseados na posição para garantir variedade
        self.type = types[(row + col) % 3] 
        
        self.cooldown = 0
        self.max_cooldown = max(3, 12 - level)
        self.range = (HEIGHT * BALANCE["TOWER_RANGE_BASE"]) + (level * 50)
        self.damage = (BALANCE["TOWER_DAMAGE_BASE"] + (level * 6)) * 1.1
        self.angle = 0
        
        # Animação de Spawn
        self.scale = 0.1 
        self.target_scale = 1.0

    def trigger_merge_effect(self):
        """Chamado quando a torre evolui."""
        self.scale = 1.5 # Pop!

    def update(self, enemies: List[Enemy], projectiles: List[Projectile], assets: Any):
        # Animação suave de escala (Interpolation)
        if abs(self.scale - self.target_scale) > 0.01:
            self.scale += (self.target_scale - self.scale) * 0.2
        else:
            self.scale = self.target_scale

        if self.cooldown > 0: 
            self.cooldown -= 1
            return

        target = None
        closest_dist = float('inf')
        
        for e in enemies:
            d_tower = math.hypot(e.x - self.x, e.y - self.y)
            if d_tower < self.range:
                d_base = math.hypot(e.x - WIDTH//2, e.y - HEIGHT//2)
                if d_base < closest_dist:
                    closest_dist = d_base
                    target = e
        
        if target:
            self.angle = math.atan2(target.y - self.y, target.x - self.x)
            assets.play_sfx("shoot")
            
            # Cores baseadas no tipo
            p_color = COLORS["CYAN"]
            if self.type == "ice": p_color = (100, 255, 255) # Azul claro
            elif self.type == "fire": p_color = (255, 100, 50) # Laranja
            elif self.level > 1: p_color = COLORS["MAGENTA"]
            
            # Muzzle Flash Effect (Partícula rápida)
            muzzle_x = self.x + math.cos(self.angle) * 35
            muzzle_y = self.y + math.sin(self.angle) * 35
            # Import circular dependency workaround? No, Particle is in Game.particles list.
            # Tower doesn't have reference to game... passed in update? 
            # update signature: (enemies, projectiles, assets) -> No game particles list.
            # I need to change signature or hack it.
            # Ideally Tower shouldn't spawn particles directly, but return them or use a callback.
            # For MVP speed: I will assume 'projectiles' list can be used or I'll pass 'game' context instead of split lists.
            # But changing signature breaks compatibility.
            # Let's check where update is called: game.py line ~130: t.update(self.enemies, self.projectiles, self.assets)
            # I can't easily access particles list.
            
            # Alternative: Visual recoil (scale bump)
            self.scale = 1.3 # Big bump on shoot
            
            proj = Projectile(
                self.x + math.cos(self.angle)*20,
                self.y + math.sin(self.angle)*20,
                self.angle,
                self.damage,
                p_color,
                self.type
            )
            projectiles.append(proj)
            self.cooldown = self.max_cooldown

    def draw(self, surface: pygame.Surface, offset: Tuple[float, float], font: pygame.font.Font):
        radius = (WIDTH * 0.05) + (self.level * 2)
        self.draw_shadow(surface, offset, radius)
        
        draw_x = self.x + offset[0]
        draw_y = self.y + offset[1]
        
        # Define cor baseada no tipo
        if self.type == "ice":
            base_color = (0, 100, 255)
            ring_color = (100, 255, 255)
        elif self.type == "fire":
            base_color = (150, 50, 0)
            ring_color = (255, 100, 0)
        else: # Standard
            base_color = (20, 20, 30)
            ring_color = COLORS["CYAN"] if self.level == 1 else COLORS["MAGENTA"] if self.level == 2 else COLORS["GOLD"]

        # Aplica escala (Zoom effect)
        current_radius = radius * self.scale
        
        pygame.draw.circle(surface, base_color, (int(draw_x), int(draw_y)), int(current_radius))
        pygame.draw.circle(surface, ring_color, (int(draw_x), int(draw_y)), int(current_radius), 3)
        
        # Canhão
        end_x = draw_x + math.cos(self.angle) * current_radius * 1.5
        end_y = draw_y + math.sin(self.angle) * current_radius * 1.5
        pygame.draw.line(surface, ring_color, (draw_x, draw_y), (end_x, end_y), int(6 * self.scale))
        
        # Ícone do tipo (texto simples seguro)
        type_char = ""
        type_color = COLORS["WHITE"]
        
        if self.type == "ice": 
            type_char = "I"
            type_color = (100, 255, 255)
        elif self.type == "fire": 
            type_char = "F"
            type_color = (255, 100, 50)
        
        # Desenha Nível
        if self.scale > 0.8:
            # Renderiza o nível
            txt = font.render(str(self.level), True, COLORS["WHITE"])
            txt_rect = txt.get_rect(center=(draw_x, draw_y))
            surface.blit(txt, txt_rect)
            
            # Renderiza o tipo (pequeno, no canto superior direito)
            if type_char:
                type_txt = pygame.font.Font(None, int(radius)).render(type_char, True, type_color)
                surface.blit(type_txt, (draw_x + radius*0.4, draw_y - radius*0.8))