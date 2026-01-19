import pygame
import math
from src.config import *
from src.utils import draw_glow

class Player:
    def __init__(self):
        self.pos = pygame.Vector2(WORLD_W / 2, WORLD_H / 2)
        self.radius = 20
        self.speed = 300.0
        self.max_health = 100
        self.health = self.max_health
        self.trail = []
        
        self.angle = 0.0
        self.ring_angle = 0.0
        self.velocity = pygame.Vector2(0, 0)

    @property
    def x(self): return self.pos.x
    @property
    def y(self): return self.pos.y

    def update(self, dt: float, enemies: list, xp_orbs: list):
        self.ring_angle += 2.0 * dt
        
        # Trail Logic
        if len(self.trail) > 10: self.trail.pop(0)
        if len(self.trail) % 2 == 0:
             self.trail.append((self.pos.x, self.pos.y))

        # --- AI HEURISTICS ---
        num_slots = 16
        slots = [pygame.Vector2(math.cos((i/num_slots)*math.tau), math.sin((i/num_slots)*math.tau)) for i in range(num_slots)]
        
        danger = [0.0] * num_slots
        interest = [0.0] * num_slots

        # 1. Threats
        for e in enemies:
            dir_to = (e.pos - self.pos)
            dist = dir_to.length()
            if dist < 400:
                danger_val = math.pow(max(0, 1.0 - (dist / 400.0)), 2)
                if dist < 120: danger_val *= 2.0
                norm_dir = dir_to.normalize()
                for i, s in enumerate(slots):
                    dot = s.dot(norm_dir)
                    if dot > 0: danger[i] = max(danger[i], dot * danger_val)

        # 2. Wall Danger
        if self.pos.x < CORNER_MARGIN: danger[slots.index(min(slots, key=lambda s: s.x if s.x < 0 else 1))] = 1.5
        if self.pos.x > WORLD_W - CORNER_MARGIN: danger[slots.index(max(slots, key=lambda s: s.x))] = 1.5

        # 3. Interest (XP)
        if xp_orbs:
            sorted_orbs = sorted(xp_orbs, key=lambda o: (o.x-self.pos.x)**2 + (o.y-self.pos.y)**2)[:10]
            for orb in sorted_orbs:
                dir_to = pygame.Vector2(orb.x - self.pos.x, orb.y - self.pos.y)
                dist = dir_to.length()
                weight = 1.0 / (dist + 50)
                norm_dir = dir_to.normalize()
                for i, s in enumerate(slots):
                    dot = s.dot(norm_dir)
                    if dot > 0: interest[i] += dot * weight * 2000

        # 4. Movement Synthesis
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
            target_angle = math.degrees(math.atan2(self.velocity.y, self.velocity.x))
            self.angle += (target_angle - self.angle + 180) % 360 - 180 * 5 * dt

        # Boundary Clamping
        self.pos.x = max(20, min(WORLD_W - 20, self.pos.x))
        self.pos.y = max(20, min(WORLD_H - 20, self.pos.y))

    def take_damage(self, amount: int):
        self.health -= amount

    def is_alive(self) -> bool:
        return self.health > 0

    def draw(self, screen: pygame.Surface, offset):
        ox, oy = offset
        cx, cy = self.pos.x + ox, self.pos.y + oy
        
        # Trail
        for i, pos in enumerate(self.trail):
            alpha = int(100 * (i / len(self.trail)))
            pygame.draw.circle(screen, (*COLOR_PLAYER, alpha), (int(pos[0]+ox), int(pos[1]+oy)), int((i/len(self.trail))*10))

        # Main Body
        rad_angle = math.radians(self.angle)
        pts = [
            (cx + math.cos(rad_angle) * 20, cy + math.sin(rad_angle) * 20),
            (cx + math.cos(rad_angle + 2.5) * 18, cy + math.sin(rad_angle + 2.5) * 18),
            (cx, cy),
            (cx + math.cos(rad_angle - 2.5) * 18, cy + math.sin(rad_angle - 2.5) * 18)
        ]
        draw_glow(screen, COLOR_PLAYER, (cx, cy), 20)
        pygame.draw.polygon(screen, COLOR_PLAYER, pts)
        pygame.draw.polygon(screen, (255, 255, 255), pts, 2)