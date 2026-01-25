import pygame
import math
from src.config import *
from src.utils import draw_glow

class Weapon:
    def __init__(self, player):
        self.player = player
        self.angle = 0.0
        self.rotation_speed = WEAPON_ROTATION_SPEED
        self.damage = WEAPON_DAMAGE
        self.orbit_radius = WEAPON_ORBIT_RADIUS
        self.hit_radius = WEAPON_HIT_RADIUS
        self.num_orbs = WEAPON_INITIAL_ORBS
        self.hit_cooldowns = {} 

    def update(self, dt: float, enemies: list, particle_sys, camera, sound_manager=None, spatial_hash=None):
        self.angle += self.rotation_speed * dt
        
        for i in range(self.num_orbs):
            orb_angle = self.angle + (i * (math.tau / self.num_orbs))
            wx = self.player.x + math.cos(orb_angle) * self.orbit_radius
            wy = self.player.y + math.sin(orb_angle) * self.orbit_radius

            target_enemies = enemies
            if spatial_hash:
                target_enemies = spatial_hash.get_nearby(wx, wy, self.hit_radius + 50)

            for enemy in target_enemies:
                enemy_key = f"{enemy.id}_{i}"
                if enemy_key in self.hit_cooldowns and self.hit_cooldowns[enemy_key] > 0:
                    self.hit_cooldowns[enemy_key] -= dt
                    continue

                dx = enemy.pos.x - wx
                dy = enemy.pos.y - wy
                dist_sq = dx*dx + dy*dy
                rad_sum = self.hit_radius + enemy.radius
                
                if dist_sq < rad_sum * rad_sum:
                    enemy.take_damage(self.damage)
                    self.hit_cooldowns[enemy_key] = 0.2
                    particle_sys.emit(wx, wy, COLOR_WEAPON, count=4, speed=80)
                    camera.add_shake(1.2)
                    if sound_manager:
                        sound_manager.play_sfx("impact")

    def draw(self, screen: pygame.Surface, camera):
        rad = camera.apply_scale(self.hit_radius)
        orbit = self.orbit_radius 
        
        for i in range(self.num_orbs):
            orb_angle = self.angle + (i * (math.tau / self.num_orbs))
            wx = self.player.x + math.cos(orb_angle) * orbit
            wy = self.player.y + math.sin(orb_angle) * orbit
            pos = camera.apply(wx, wy)

            # Trail
            for j in range(1, 4):
                trail_angle = orb_angle - (j * 0.12)
                tx = self.player.x + math.cos(trail_angle) * orbit
                ty = self.player.y + math.sin(trail_angle) * orbit
                t_pos = camera.apply(tx, ty)
                alpha = 100 - (j * 25)
                
                t_rad = camera.apply_scale(self.hit_radius - j*2)
                if t_rad > 0:
                    surf = pygame.Surface((t_rad*2, t_rad*2), pygame.SRCALPHA)
                    pygame.draw.circle(surf, (*COLOR_WEAPON, alpha), (t_rad, t_rad), t_rad)
                    screen.blit(surf, (t_pos[0]-t_rad, t_pos[1]-t_rad))

            # Draw only the weapon core without the glow circle
            pygame.draw.circle(screen, COLOR_WEAPON, pos, rad)
            pygame.draw.circle(screen, COLOR_TEXT, pos, max(1, rad - camera.apply_scale(8)))
