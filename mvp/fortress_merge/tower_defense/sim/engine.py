"""
Main Game Engine Logic
"""
import random
from typing import List, Tuple
from sim import config
from sim.entities import Zombie, Soldier, Projectile

class GameEngine:
    def __init__(self):
        self.money = config.STARTING_MONEY
        self.zombies_defeated = 0
        self.frame_count = 0
        
        # Base Health
        self.base_health = config.BASE_MAX_HEALTH
        self.game_over = False
        self.game_result = "PLAYING" # PLAYING, WIN, LOSE
        
        # Events
        self.active_event = None # (name, duration_frames)
        self.event_timer = 0
        
        # Entity lists
        self.zombies: List[Zombie] = []
        self.soldiers: List[Soldier] = []
        self.projectiles: List[Projectile] = []
        
        # Dead entity records (x, y, type)
        self.recent_events: List[Tuple[float, float, str]] = []

        # Initial Setup 
        self._spawn_initial_soldiers()
        
        # Economy Plan
        self.next_purchase = self._pick_next_purchase()
    
    def _pick_next_purchase(self):
        """Decides the next unit to buy based on simple weights."""
        options = ['rifle', 'shotgun', 'sniper', 'minigun', 'rocket', 'flame', 'railgun']
        # Weights favor cheap units early, expensive late (simple logic based on money could be better but random is ok for variety)
        # Let's favor variety.
        choice = random.choice(options)
        cost = config.SOLDIER_STATS[choice]['cost']
        return {'type': choice, 'cost': cost}

    def _spawn_initial_soldiers(self):
        # Start with a solid defense line: 3 Rifles + 1 Shotgun
        self.soldiers.append(Soldier(120, config.VIDEO_HEIGHT//2 - 100, 'rifle'))
        self.soldiers.append(Soldier(120, config.VIDEO_HEIGHT//2, 'shotgun'))
        self.soldiers.append(Soldier(120, config.VIDEO_HEIGHT//2 + 100, 'rifle'))

    def update(self):
        if self.game_result != "PLAYING":
            return

        self.frame_count += 1
        self.recent_events.clear()
        
        # 0. Handle Events (Grace period first 10s)
        if self.frame_count > 600:
            self._handle_events()

        # 1. Spawner Logic 
        self._handle_spawning()

        # 2. Update Entities
        for s in self.soldiers:
            projs = s.update(self.zombies) 
            self.projectiles.extend(projs)
        
        # Zombies move 
        move_mult = 1.0
        if self.active_event and self.active_event[0] == "ZOMBIE FRENZY":
            move_mult = 2.0
            
        for z in self.zombies:
            old_speed = z.speed
            z.speed *= move_mult
            z.update()
            z.speed = old_speed # Reset for next frame calc logic if needed, actually safer to just mod pos
            
            # Check Base Collision
            if z.pos.x <= config.BASE_X_LIMIT:
                self.base_health -= z.damage_to_base
                z.alive = False 
                self.recent_events.append((z.pos.x, z.pos.y, "base_hit"))
                
                if self.base_health <= 0:
                    self.base_health = 0
                    self.game_over = True
                    self.game_result = "LOSE"
            
        for p in self.projectiles:
            p.update()

        # 3. Collision Detection
        self._handle_collisions()

        # 4. Cleanup
        self.zombies = [z for z in self.zombies if z.alive]
        self.projectiles = [p for p in self.projectiles if p.alive]
        
        # 5. Check WIN Condition
        if self.frame_count > config.SPAWN_END_FRAME and len(self.zombies) == 0:
            self.game_result = "WIN"
            self.game_over = True
        
        # 6. Economy/Upgrade Logic
        self._handle_auto_buy()

    def _handle_events(self):
        # Decrement active event
        if self.active_event:
            self.event_timer -= 1
            if self.event_timer <= 0:
                self.active_event = None
        
        # Random trigger
        elif random.random() < 0.002: # Low chance per frame
            ev_type = random.choice(["ZOMBIE FRENZY", "AIR SUPPORT", "BOSS WARNING"])
            duration = 180 # 3 seconds default
            
            if ev_type == "AIR SUPPORT":
                self.money += 1000
                self.recent_events.append((config.VIDEO_WIDTH/2, config.VIDEO_HEIGHT/2, "airdrop"))
                duration = 60
                
            elif ev_type == "BOSS WARNING":
                # Spawn boss
                y = config.VIDEO_HEIGHT / 2
                boss = Zombie(config.SPAWN_OFFSET_X, y, 'tank')
                boss.max_health = 500 # Huge
                boss.health = 500
                boss.radius = 60
                boss.damage_to_base = 100 # Instakill base almost
                self.zombies.append(boss)
            
            self.active_event = (ev_type, duration)
            self.event_timer = duration

    def _handle_spawning(self):
        if self.frame_count > config.SPAWN_END_FRAME: return

        spawn_rate = max(2, 50 - self.frame_count // 50) 
        if self.active_event and self.active_event[0] == "ZOMBIE FRENZY":
            spawn_rate = max(1, spawn_rate // 2)

        if self.frame_count % spawn_rate == 0:
            count = 1 + self.frame_count // 400 
            weights = [100, 0, 0] # Normal, Fast, Tank
            if self.frame_count > 300: weights = [70, 30, 0]
            if self.frame_count > 600: weights = [50, 40, 10]
            if self.frame_count > 1200: weights = [30, 40, 30]

            base_y = random.randint(200, config.VIDEO_HEIGHT - 400)
            
            for _ in range(count):
                y = base_y + random.uniform(-100, 100)
                y = max(200, min(y, config.VIDEO_HEIGHT - 300))
                z_type = random.choices(['normal', 'fast', 'tank'], weights=weights, k=1)[0]
                self.zombies.append(Zombie(config.SPAWN_OFFSET_X + random.uniform(0, 100), y, z_type))

    def _handle_collisions(self):
        for p in self.projectiles:
            if not p.alive: continue
            
            for z in self.zombies:
                if not z.alive: continue
                
                dx = p.pos.x - z.pos.x
                dy = p.pos.y - z.pos.y
                if abs(dx) < 35 and abs(dy) < 35:
                    dist_sq = dx*dx + dy*dy
                    if dist_sq < (p.radius + z.radius)**2:
                        p.alive = False
                        
                        if p.type == 'rocket':
                            # AoE Explosion
                            self.recent_events.append((z.pos.x, z.pos.y, "explosion"))
                            for sub_z in self.zombies:
                                if not sub_z.alive: continue
                                d_expl = sub_z.pos.distance_to(z.pos)
                                if d_expl < 150: # Explosion Radius
                                    sub_z.hit(p.damage)
                                    if not sub_z.alive:
                                        self.money += config.MONEY_PER_KILL
                                        self.zombies_defeated += 1
                        else:
                            z.hit(p.damage) 
                            if not z.alive:
                                self.money += config.MONEY_PER_KILL
                                self.zombies_defeated += 1
                                self.recent_events.append((z.pos.x, z.pos.y, "kill"))
                        break 
            
    def _handle_auto_buy(self):
        # Check if we can afford the PLANNED purchase
        target = self.next_purchase
        
        if self.money >= target['cost']:
            self.money -= target['cost']
            
            # Placement logic
            col = random.randint(0, 4)
            x = 180 - (col * 35)
            # Avoid placing exactly on top of another (simple check)
            attempts = 0
            while True:
                y = random.uniform(200, config.VIDEO_HEIGHT - 300)
                overlap = False
                for s in self.soldiers:
                    if abs(s.pos.y - y) < 20 and abs(s.pos.x - x) < 20:
                        overlap = True
                        break
                if not overlap or attempts > 10:
                    break
                attempts += 1
            
            self.soldiers.append(Soldier(x, y, target['type']))
            
            # Pick NEW target
            self.next_purchase = self._pick_next_purchase()
