import random
import math
from src import config
from src.entities.enemy import Enemy

class GameManager:
    def __init__(self):
        self.xp = 0
        self.max_xp = 100
        self.level = 1
        self.kills = 0
        self.time_elapsed = 0.0
        
        self.spawn_timer = 0.0
        self.spawn_interval = 0.8 
        self.upgrade_pending = False
        self.boss_spawned = False
        self.horde_events = [12.0, 25.0, 38.0] # More frequent chaos
        self.victory = False
        self.ambient_xp_timer = 0.0

    def add_xp(self, amount: int):
        self.xp += amount
        if self.xp >= self.max_xp:
            self.level_up()

    def level_up(self):
        self.xp -= self.max_xp
        self.level += 1
        # Player scales slower than before
        self.max_xp = int(self.max_xp * 1.4) 
        self.spawn_interval = max(0.08, self.spawn_interval * 0.88)
        self.upgrade_pending = True

    def apply_upgrade(self, upgrade_type: str, player, weapon):
        # Balanced Upgrades (Nerfed slightly to prevent god-mode)
        if upgrade_type == "speed": 
            player.speed += 25.0
        elif upgrade_type == "damage": 
            weapon.damage += 6
        elif upgrade_type == "rotation": 
            weapon.rotation_speed += 1.2
        elif upgrade_type == "weapon_count": 
            weapon.num_orbs = min(10, weapon.num_orbs + 1)
        elif upgrade_type == "weapon_range":
            weapon.orbit_radius += 20
        elif upgrade_type == "heal":
            player.health = min(player.max_health, player.health + 30)
            
        self.upgrade_pending = False

    def get_random_upgrades(self):
        pool = ["speed", "damage", "rotation", "weapon_count", "weapon_range", "heal"]
        return random.sample(pool, 3)

    def update_spawn(self, dt: float, enemies: list, xp_orbs: list = None):
        self.time_elapsed += dt
        if self.upgrade_pending or self.victory: return

        # DIFFICULTY MULTIPLIER: 1.0 at start, ~2.0 at 45 seconds
        diff_mult = 1.0 + (self.time_elapsed / 40.0)

        # AMBIENT XP SPAWN
        if xp_orbs is not None:
            self.ambient_xp_timer += dt
            if self.ambient_xp_timer > 2.5:
                self.ambient_xp_timer = 0
                from src.entities.orb import XPOrb
                for _ in range(2): # Fewer ambient XP to make kills more important
                    rx = random.uniform(200, config.WORLD_W - 200)
                    ry = random.uniform(200, config.WORLD_H - 200)
                    xp_orbs.append(XPOrb(rx, ry))

        # HORDE EVENTS
        for event_time in self.horde_events:
            if event_time <= self.time_elapsed < event_time + dt:
                for _ in range(20 + int(self.time_elapsed/2)):
                    angle = random.uniform(0, math.tau)
                    dist = 900
                    ex = config.WORLD_W/2 + math.cos(angle) * dist
                    ey = config.WORLD_H/2 + math.sin(angle) * dist
                    enemies.append(Enemy(ex, ey, "swarm", diff_mult))

        # BOSS SPAWN (At 45s)
        if self.time_elapsed > 45.0 and not self.boss_spawned:
            self.boss_spawned = True
            # Boss uses the multiplier too!
            enemies.append(Enemy(config.WORLD_W/2, config.WORLD_H/2 - 800, "boss", diff_mult))
            return

        # REGULAR SPAWN
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            
            rand = random.random()
            etype = "common"
            
            if self.time_elapsed > 35:
                if rand < 0.25: etype = "tank"
                elif rand < 0.6: etype = "fast"
                elif rand < 0.7: etype = "elite"
            elif self.time_elapsed > 15:
                if rand < 0.3: etype = "fast"
                elif rand < 0.45: etype = "swarm"

            angle = random.uniform(0, math.tau)
            dist = 1000
            ex = config.WORLD_W/2 + math.cos(angle) * dist
            ey = config.WORLD_H/2 + math.sin(angle) * dist
            
            enemies.append(Enemy(ex, ey, etype, diff_mult))
