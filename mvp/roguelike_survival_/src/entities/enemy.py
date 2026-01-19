import pygame
import math
import random
from src.config import *
from src.utils import draw_glow

_enemy_id_counter = 0

class Enemy:
    # Static Data Map for cleaner initialization
    DATA = {
        "common": {"radius": 18, "speed": 110, "health": 35, "color": COLOR_ENEMY_COMMON, "damage": 12},
        "fast": {"radius": 14, "speed": 210, "health": 20, "color": COLOR_ENEMY_FAST, "damage": 8},
        "tank": {"radius": 35, "speed": 80, "health": 200, "color": COLOR_ENEMY_TANK, "damage": 25},
        "swarm": {"radius": 10, "speed": 160, "health": 10, "color": COLOR_ENEMY_SWARM, "damage": 5},
        "elite": {"radius": 26, "speed": 100, "health": 500, "color": COLOR_ENEMY_ELITE, "damage": 20},
        "boss": {"radius": 90, "speed": 70, "health": 10000, "color": COLOR_ENEMY_BOSS, "damage": 50}
    }

    def __init__(self, x: float, y: float, enemy_type="common", time_multiplier=1.0):
        global _enemy_id_counter
        self.id = _enemy_id_counter
        _enemy_id_counter += 1
        
        self.type = enemy_type
        self.pos = pygame.Vector2(x, y)
        self.angle = 0.0 
        self.damage_cooldown = 0.0
        self.flash_timer = 0.0
        
        stats = self.DATA.get(enemy_type, self.DATA["common"])
        self.radius = stats["radius"]
        self.speed = stats["speed"] * (1.0 + (time_multiplier - 1.0) * 0.5)
        self.max_health = stats["health"] * time_multiplier
        self.health = self.max_health
        self.color = stats["color"]
        self.damage = stats["damage"] * time_multiplier

    def update(self, dt: float, player, camera):
        if not player.is_alive(): return
        
        # Behavior Logic
        current_speed = self.speed
        if self.type == "boss":
            health_pct = self.health / self.max_health
            current_speed *= (1.0 + (1.0 - health_pct))
            self.angle += 3.0 * dt
        else:
            self.angle += 2.0 * dt

        # Movement towards player
        target = pygame.Vector2(player.x, player.y)
        dir_vec = (target - self.pos)
        dist = dir_vec.length()
        if dist > 0:
            self.pos += dir_vec.normalize() * current_speed * dt

        # Damage Logic
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt
        elif dist < self.radius + player.radius:
            player.take_damage(self.damage)
            self.damage_cooldown = 0.4
            camera.add_shake(8.0)

        if self.flash_timer > 0:
            self.flash_timer -= dt

    def take_damage(self, amount: int):
        self.health -= amount
        self.flash_timer = 0.1

    def is_dead(self) -> bool:
        return self.health <= 0

    def draw(self, screen: pygame.Surface, offset):
        ox, oy = offset
        cx, cy = int(self.pos.x + ox), int(self.pos.y + oy)
        color = (255, 255, 255) if self.flash_timer > 0 else self.color
        
        if self.flash_timer <= 0:
            draw_glow(screen, self.color, (cx, cy), self.radius)

        if self.type == "boss":
            self._draw_boss(screen, cx, cy, color)
        elif self.type == "elite":
            self._draw_elite(screen, cx, cy, color)
        else:
            pygame.draw.circle(screen, color, (cx, cy), self.radius)

    def _draw_boss(self, screen, cx, cy, color):
        pts = []
        for i in range(8):
            theta = self.angle + (i * 0.785)
            pts.append((cx + math.cos(theta) * self.radius, cy + math.sin(theta) * self.radius))
        pygame.draw.polygon(screen, color, pts)
        pygame.draw.polygon(screen, COLOR_TEXT, pts, 4)
        
        # Floating HP Bar
        hp_pct = max(0, self.health / self.max_health)
        pygame.draw.rect(screen, (40, 0, 0), (cx - 80, cy - self.radius - 30, 160, 12))
        pygame.draw.rect(screen, COLOR_ENEMY_BOSS, (cx - 80, cy - self.radius - 30, 160 * hp_pct, 12))

    def _draw_elite(self, screen, cx, cy, color):
        pts = []
        for i in range(4):
            theta = self.angle + (i * 1.57)
            pts.append((cx + math.cos(theta) * self.radius * 1.3, cy + math.sin(theta) * self.radius * 1.3))
        pygame.draw.polygon(screen, color, pts)
