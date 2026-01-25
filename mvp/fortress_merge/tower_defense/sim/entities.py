"""
Game entities class definitions.
"""
import math
import random
from typing import List, Optional
from dataclasses import dataclass
from sim import config

@dataclass
class Vector2:
    x: float
    y: float

    def distance_to(self, other: 'Vector2') -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

class Entity:
    def __init__(self, x, y):
        self.pos = Vector2(x, y)
        self.alive = True
        self.radius = 10

class Zombie(Entity):
    def __init__(self, x, y, z_type='normal'):
        super().__init__(x, y)
        self.type = z_type
        stats = config.ZOMBIE_STATS[z_type]
        
        self.speed = random.uniform(*stats['speed'])
        self.radius = stats['radius']
        self.max_health = stats['hp']
        self.health = self.max_health
        self.damage_to_base = stats['damage']
        
        # Add some vertical jitter to movement
        self.y_jitter_speed = random.uniform(-0.5, 0.5)

    def update(self):
        # Move Left
        self.pos.x -= self.speed
        
        # Slight vertical weave
        self.pos.y += self.y_jitter_speed
        
        # Bounce off top/bottom limits (stay in bounds)
        if self.pos.y < 50 or self.pos.y > config.VIDEO_HEIGHT - 250: 
            self.y_jitter_speed *= -1

    def hit(self, dmg=1):
        self.health -= dmg
        if self.health <= 0:
            self.alive = False

class Projectile(Entity):
    def __init__(self, x, y, target: Entity, dmg=1, p_type='bullet'):
        super().__init__(x, y)
        self.target = target 
        self.damage = dmg
        self.type = p_type # 'bullet', 'rocket', 'flame', 'laser'
        
        self.speed = config.PROJECTILE_SPEED
        self.pierce = 1 # Default hits 1 enemy
        
        if p_type == 'rocket': 
            self.speed *= 0.6
        elif p_type == 'flame':
            self.speed *= 0.4
            self.radius = random.uniform(3, 8)
            # Flame jitter
            self.velocity = Vector2(0,0) # Placeholder, set below
        elif p_type == 'laser':
            self.speed *= 2.0 # Very fast
            self.pierce = 5 # Hits up to 5 enemies
            self.radius = 4
        
        # Initial velocity
        self._point_to_target()
        
        if p_type == 'bullet': self.radius = 5
        if p_type == 'rocket': self.radius = 8

    def _point_to_target(self):
        if self.target and self.target.alive:
            dx = self.target.pos.x - self.pos.x
            dy = self.target.pos.y - self.pos.y
            dist = math.hypot(dx, dy)
            
            if dist > 0:
                vx = (dx/dist) * self.speed
                vy = (dy/dist) * self.speed
                
                if self.type == 'flame':
                    # Add heavy spread for flamethrower
                    angle = random.uniform(-0.3, 0.3)
                    cos_a = math.cos(angle)
                    sin_a = math.sin(angle)
                    nx = vx * cos_a - vy * sin_a
                    ny = vx * sin_a + vy * cos_a
                    vx, vy = nx, ny
                    
                self.velocity = Vector2(vx, vy)

    def update(self):
        # Homing Logic: Adjust course towards target every frame
        if self.target and self.target.alive:
            # Agility factor: Rockets turn slower, bullets turn instant
            # Flames/Lasers don't home after launch (dumb fire)
            if self.type in ['bullet', 'rocket']:
                self._point_to_target()
            
        self.pos.x += self.velocity.x
        self.pos.y += self.velocity.y
        
        # Flame grows and slows down
        if self.type == 'flame':
            self.radius += 0.2
            self.velocity.x *= 0.95
            self.velocity.y *= 0.95
            if self.radius > 15: self.alive = False # Burn out
        
        if (self.pos.x < 0 or self.pos.x > config.VIDEO_WIDTH + 100 or
            self.pos.y < 0 or self.pos.y > config.VIDEO_HEIGHT):
            self.alive = False

class Soldier(Entity):
    def __init__(self, x, y, s_type='rifle'):
        super().__init__(x, y)
        self.type = s_type
        stats = config.SOLDIER_STATS[s_type]
        
        self.range = stats['range']
        self.fire_rate = stats['rate']
        self.damage = stats['dmg']
        self.color = stats['color']
        
        self.cooldown = 0
        self.target: Optional[Zombie] = None

    def update(self, zombies: List[Zombie]) -> List[Projectile]:
        if self.cooldown > 0:
            self.cooldown -= 1
            return []

        # Find nearest zombie
        nearest_zombie = None
        min_dist = self.range

        for z in zombies:
            if not z.alive: continue
            if z.pos.x > self.pos.x + self.range: continue 
            
            dist = self.pos.distance_to(z.pos)
            if dist < min_dist:
                min_dist = dist
                nearest_zombie = z

        new_projs = []
        if nearest_zombie:
            self.cooldown = self.fire_rate
            
            p_type = 'bullet'
            if self.type == 'rocket': p_type = 'rocket'
            elif self.type == 'flame': p_type = 'flame'
            elif self.type == 'railgun': p_type = 'laser'
            
            target_pos = nearest_zombie
            
            new_projs.append(Projectile(self.pos.x, self.pos.y, target_pos, dmg=self.damage, p_type=p_type))
        
        return new_projs
