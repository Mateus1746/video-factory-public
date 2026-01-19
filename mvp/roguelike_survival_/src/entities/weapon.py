import pygame
import math
from src.config import COLOR_WEAPON, COLOR_TEXT
from src.utils import draw_glow

class Weapon:
    def __init__(self, player):
        self.player = player
        self.angle = 0.0
        self.rotation_speed = 4.2
        self.damage = 12
        self.orbit_radius = 90
        self.hit_radius = 20
        self.num_orbs = 2
        self.hit_cooldowns = {} 

    def update(self, dt: float, enemies: list, particle_sys, camera, sound_manager=None):
        self.angle += self.rotation_speed * dt
        
        for i in range(self.num_orbs):
            orb_angle = self.angle + (i * (math.tau / self.num_orbs))
            wx = self.player.x + math.cos(orb_angle) * self.orbit_radius
            wy = self.player.y + math.sin(orb_angle) * self.orbit_radius

            for enemy in enemies:
                enemy_key = f"{enemy.id}_{i}"
                if enemy_key in self.hit_cooldowns and self.hit_cooldowns[enemy_key] > 0:
                    self.hit_cooldowns[enemy_key] -= dt
                    continue

                dx = enemy.pos.x - wx
                dy = enemy.pos.y - wy
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < self.hit_radius + enemy.radius:
                    enemy.take_damage(self.damage)
                    self.hit_cooldowns[enemy_key] = 0.2
                    particle_sys.emit(wx, wy, COLOR_WEAPON, count=4, speed=80)
                    camera.add_shake(1.2)
                    if sound_manager:
                        sound_manager.play_sfx("impact")

    def draw(self, screen: pygame.Surface, offset):
        ox, oy = offset
        for i in range(self.num_orbs):
            orb_angle = self.angle + (i * (math.tau / self.num_orbs))
            wx = self.player.x + math.cos(orb_angle) * self.orbit_radius
            wy = self.player.y + math.sin(orb_angle) * self.orbit_radius

            # Trail
            for j in range(1, 4):
                trail_angle = orb_angle - (j * 0.12)
                tx = self.player.x + math.cos(trail_angle) * self.orbit_radius
                ty = self.player.y + math.sin(trail_angle) * self.orbit_radius
                alpha = 100 - (j * 25)
                
                surf = pygame.Surface((self.hit_radius*2, self.hit_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*COLOR_WEAPON, alpha), (self.hit_radius, self.hit_radius), self.hit_radius - j*2)
                screen.blit(surf, (tx+ox-self.hit_radius, ty+oy-self.hit_radius))

            draw_glow(screen, COLOR_WEAPON, (wx+ox, wy+oy), self.hit_radius)
            pygame.draw.circle(screen, COLOR_WEAPON, (int(wx+ox), int(wy+oy)), self.hit_radius)
            pygame.draw.circle(screen, COLOR_TEXT, (int(wx+ox), int(wy+oy)), self.hit_radius - 8)
