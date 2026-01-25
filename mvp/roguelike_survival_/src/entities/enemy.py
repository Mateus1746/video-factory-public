import pygame
import math
import random
import os
from src.config import *
from src.utils import draw_glow

_enemy_id_counter = 0

class Enemy:
    _SPRITE_CACHE = {}

    def __init__(self, x: float, y: float, enemy_type="common", time_multiplier=1.0):
        global _enemy_id_counter
        self.id = _enemy_id_counter
        _enemy_id_counter += 1
        
        self.type = enemy_type
        self.pos = pygame.Vector2(x, y)
        self.angle = random.uniform(0, 360) 
        self.damage_cooldown = 0.0
        self.flash_timer = 0.0
        
        # Spawn Animation
        self.spawn_timer = 0.0
        self.spawn_duration = 0.5 
        
        stats = ENEMY_STATS.get(enemy_type, ENEMY_STATS["common"])
        self.radius = stats["radius"]
        self.speed = stats["speed"] * (1.0 + (time_multiplier - 1.0) * 0.5)
        self.max_health = stats["health"] * time_multiplier
        self.health = self.max_health
        self.damage = stats["damage"] * time_multiplier
        self.color = ENEMY_COLORS.get(enemy_type, (255, 255, 255))
        
        self.sprite = self._load_sprite()
        self.hit_sprite = self._load_sprite(hit=True)
        self.bob_timer = random.uniform(0, math.tau)
        self.rotation_speed = random.uniform(50, 150) if enemy_type != "boss" else 30

    def _load_sprite(self, hit=False):
        cache_key = (self.type, hit)
        if cache_key in self._SPRITE_CACHE:
            return self._SPRITE_CACHE[cache_key]

        file_map = {
            "common": "slime.png", "swarm": "slime.png", "fast": "slime.png",
            "tank": "golem-de-pedra.png", "elite": "golem-de-pedra.png", "boss": "golem-de-pedra.png"
        }
        
        filename = file_map.get(self.type, "slime.png")
        if hit and self.type in ["tank", "elite", "boss"]:
            filename = "golem-de-pedra-sendo-atacado.png"
            
        path = os.path.join("assets/sprites/enemies", filename)
        if os.path.exists(path):
            surf = pygame.image.load(path).convert_alpha()
            scale_factor = 2.5 if self.type != "boss" else 2.2
            size = int(self.radius * scale_factor)
            surf = pygame.transform.scale(surf, (size, size))
            
            if hit and not "atacado" in filename:
                hit_surf = surf.copy()
                hit_surf.fill((255, 255, 255, 200), special_flags=pygame.BLEND_RGBA_ADD)
                surf = hit_surf
                
            self._SPRITE_CACHE[cache_key] = surf
            return surf
        return None

    def update(self, dt: float, player, camera):
        if self.spawn_timer < self.spawn_duration:
            self.spawn_timer += dt
            return 

        if not player.is_alive(): return
        
        self.bob_timer += 5 * dt
        self.angle += self.rotation_speed * dt
        
        current_speed = self.speed
        if self.type == "boss":
            health_pct = self.health / self.max_health
            current_speed *= (1.0 + (1.0 - health_pct))

        target = pygame.Vector2(player.x, player.y)
        dir_vec = (target - self.pos)
        dist = dir_vec.length()
        if dist > 0:
            self.pos += dir_vec.normalize() * current_speed * dt

        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt
        elif dist < self.radius + player.radius:
            player.take_damage(self.damage)
            self.damage_cooldown = 0.4
            camera.add_shake(8.0)

        if self.flash_timer > 0:
            self.flash_timer -= dt

    def take_damage(self, amount: int):
        if self.spawn_timer < self.spawn_duration: return 
        self.health -= amount
        self.flash_timer = 0.15

    def is_dead(self) -> bool:
        return self.health <= 0

    def draw(self, screen: pygame.Surface, camera):
        pos = camera.apply(self.pos.x, self.pos.y)
        rad = camera.apply_scale(self.radius)
        scale = camera.zoom
        
        spawn_pct = min(1.0, self.spawn_timer / self.spawn_duration)
        sprite_to_draw = self.hit_sprite if self.flash_timer > 0 else self.sprite
        
        if sprite_to_draw:
            squash = 1.0 + math.sin(self.bob_timer) * 0.1
            stretch = 1.0 - math.sin(self.bob_timer) * 0.1
            
            render_surf = sprite_to_draw
            if self.type != "boss":
                render_surf = pygame.transform.rotate(sprite_to_draw, self.angle * 0.2)
            
            w, h = render_surf.get_size()
            new_w = int(w * squash * scale * (0.5 + 0.5 * spawn_pct))
            new_h = int(h * stretch * scale * (0.5 + 0.5 * spawn_pct))
            
            if new_w > 0 and new_h > 0:
                render_surf = pygame.transform.scale(render_surf, (new_w, new_h))
                if spawn_pct < 1.0:
                    render_surf.set_alpha(int(255 * spawn_pct))
                
                rect = render_surf.get_rect(center=pos)
                screen.blit(render_surf, rect)
            
            if self.type == "boss" and spawn_pct >= 1.0:
                self._draw_boss_hp(screen, pos, rad)
        else:
            # Fallback
            color = (255, 255, 255) if self.flash_timer > 0 else self.color
            pygame.draw.circle(screen, color, pos, rad)

    def _draw_boss_hp(self, screen, pos, rad):
        cx, cy = pos
        hp_pct = max(0, self.health / self.max_health)
        bar_w = rad * 2.5
        pygame.draw.rect(screen, (20, 0, 0), (cx - bar_w/2, cy - rad - 40, bar_w, 14), border_radius=7)
        pygame.draw.rect(screen, self.color, (cx - bar_w/2, cy - rad - 40, bar_w * hp_pct, 14), border_radius=7)
        pygame.draw.rect(screen, (255, 255, 255), (cx - bar_w/2, cy - rad - 40, bar_w, 14), 2, border_radius=7)