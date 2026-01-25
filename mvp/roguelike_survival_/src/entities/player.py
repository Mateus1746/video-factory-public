import pygame
import math
import os
from src.config import *
from src.utils import draw_glow

class Player:
    def __init__(self):
        self.pos = pygame.Vector2(WORLD_W / 2, WORLD_H / 2)
        self.radius = PLAYER_RADIUS
        self.speed = PLAYER_SPEED
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.trail = []
        
        self.angle = 0.0
        self.velocity = pygame.Vector2(0, 0)
        
        # Sprite Loading
        self.original_sprite = None
        sprite_path = "assets/sprites/player/player.png"
        if os.path.exists(sprite_path):
            self.original_sprite = pygame.image.load(sprite_path).convert_alpha()
            # Scale sprite to match new duplicated radius
            size = int(self.radius * 2.8) 
            self.original_sprite = pygame.transform.scale(self.original_sprite, (size, size))
            
        self.bob_timer = 0.0

    @property
    def x(self): return self.pos.x
    @property
    def y(self): return self.pos.y

    def update(self, dt: float, enemies: list, xp_orbs: list):
        self.bob_timer += 10 * dt
        
        # Trail Logic
        if len(self.trail) > 12: self.trail.pop(0)
        if len(self.trail) % 2 == 0:
             self.trail.append((self.pos.x, self.pos.y))

        # AI Heuristics
        num_slots = 16
        slots = [pygame.Vector2(math.cos((i/num_slots)*math.tau), math.sin((i/num_slots)*math.tau)) for i in range(num_slots)]
        danger = [0.0] * num_slots
        interest = [0.0] * num_slots

        for e in enemies:
            dir_to = (e.pos - self.pos)
            dist = dir_to.length()
            if dist < PLAYER_AI_DANGER_RADIUS:
                danger_val = math.pow(max(0, 1.0 - (dist / PLAYER_AI_DANGER_RADIUS)), 2)
                if dist < PLAYER_AI_DANGER_CLOSE: danger_val *= 2.0
                norm_dir = dir_to.normalize()
                for i, s in enumerate(slots):
                    dot = s.dot(norm_dir)
                    if dot > 0: danger[i] = max(danger[i], dot * danger_val)

        if self.pos.x < CORNER_MARGIN: danger[slots.index(min(slots, key=lambda s: s.x if s.x < 0 else 1))] = 1.5
        if self.pos.x > WORLD_W - CORNER_MARGIN: danger[slots.index(max(slots, key=lambda s: s.x))] = 1.5

        if xp_orbs:
            sorted_orbs = sorted(xp_orbs, key=lambda o: (o.x-self.pos.x)**2 + (o.y-self.pos.y)**2)[:10]
            for orb in sorted_orbs:
                dir_to = pygame.Vector2(orb.x - self.pos.x, orb.y - self.pos.y)
                dist = dir_to.length()
                weight = 1.0 / (dist + 50)
                norm_dir = dir_to.normalize()
                for i, s in enumerate(slots):
                    dot = s.dot(norm_dir)
                    if dot > 0: interest[i] += dot * weight * PLAYER_AI_INTEREST_WEIGHT

        chosen_dir = pygame.Vector2(0, 0)
        for i in range(num_slots):
            score = interest[i] * (1.0 - danger[i])
            if score <= 0 and danger[i] > 0.1: score = -danger[i] * 0.5
            chosen_dir += slots[i] * score

        if chosen_dir.length() > 0:
            target_vel = chosen_dir.normalize() * self.speed
        else:
            target_vel = (pygame.Vector2(WORLD_W/2, WORLD_H/2) - self.pos).normalize() * (self.speed * 0.2)

        self.velocity = self.velocity.lerp(target_vel, min(1.0, 10.0 * dt))
        self.pos += self.velocity * dt
        
        if self.velocity.length() > 10:
            target_angle = -math.degrees(math.atan2(self.velocity.y, self.velocity.x))
            angle_diff = (target_angle - self.angle + 180) % 360 - 180
            self.angle += angle_diff * 10 * dt

        self.pos.x = max(20, min(WORLD_W - 20, self.pos.x))
        self.pos.y = max(20, min(WORLD_W - 20, self.pos.y))

    def take_damage(self, amount: int):
        self.health -= amount

    def is_alive(self) -> bool:
        return self.health > 0

    def draw(self, screen: pygame.Surface, camera):
        pos = camera.apply(self.pos.x, self.pos.y)
        rad = camera.apply_scale(self.radius)
        cx, cy = pos
        scale = camera.zoom
        
        # 1. Trail
        for i, trail_pos in enumerate(self.trail):
            alpha = int(120 * (i / len(self.trail)))
            t_pos = camera.apply(trail_pos[0], trail_pos[1])
            # Scale trail to match larger player
            t_rad = camera.apply_scale(int((i/len(self.trail)) * 24))
            pygame.draw.circle(screen, (*COLOR_PLAYER, alpha), t_pos, t_rad)

        # 2. Main Sprite
        if self.original_sprite:
            bob = math.sin(self.bob_timer) * 10 * scale # Increased bobbing for larger size
            rotated_surf = pygame.transform.rotate(self.original_sprite, self.angle)
            if scale != 1.0:
                new_size = (int(rotated_surf.get_width() * scale), int(rotated_surf.get_height() * scale))
                rotated_surf = pygame.transform.scale(rotated_surf, new_size)
            
            rect = rotated_surf.get_rect(center=(cx, cy + bob))
            screen.blit(rotated_surf, rect)
        else:
            # Fallback
            rad_angle = -math.radians(self.angle)
            pts = [
                (cx + math.cos(rad_angle) * 50 * scale, cy + math.sin(rad_angle) * 50 * scale),
                (cx + math.cos(rad_angle + 2.5) * 44 * scale, cy + math.sin(rad_angle + 2.5) * 44 * scale),
                (cx, cy),
                (cx + math.cos(rad_angle - 2.5) * 44 * scale, cy + math.sin(rad_angle - 2.5) * 44 * scale)
            ]
            pygame.draw.polygon(screen, COLOR_PLAYER, pts)
