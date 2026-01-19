import pygame
import math
import random
from config import *
from items import PowerUp
from player import Player

class Simulation:
    def __init__(self):
        # Create Players
        self.players = [
            Player(TEAM_A),
            Player(TEAM_B)
        ]
        self.reset()

    def reset(self):
        for p in self.players:
            p.reset()
        
        # Game State
        self.game_over = False
        self.winner_player = None
        
        # Rings
        self.ring_angles = [random.uniform(0, 360) for _ in RINGS_CONFIG]
        self.original_ring_speeds = [r["speed"] for r in RINGS_CONFIG]
        
        # Chaos & Items
        self.last_event = None # ('type', 'player_index')
        self.current_chaos = None 
        self.chaos_duration = 0
        self.active_gravity = GRAVITY
        
        self.spawn_items()

    def spawn_items(self):
        self.items = []
        possible_types = ['INVERT', 'MOON', 'TURBO', 'GLITCH']
        prev_radius = 20
        
        for i, ring in enumerate(RINGS_CONFIG):
            outer_radius = ring["radius"]
            if random.random() < 0.85:
                r = random.uniform(prev_radius + 20, outer_radius - 20)
                theta = random.uniform(0, 2 * math.pi)
                x = r * math.cos(theta)
                y = r * math.sin(theta)
                t = random.choice(possible_types)
                self.items.append(PowerUp(x, y, t))
            prev_radius = outer_radius

    def trigger_chaos(self, type_name):
        self.current_chaos = type_name
        self.chaos_duration = EVENT_DURATION
        self.last_event = ("chaos_trigger", -1) 
        if self.current_chaos == 'GLITCH':
            self.temp_ring_speeds = [random.uniform(-5.0, 5.0) for _ in RINGS_CONFIG]

    def update(self, dt):
        # Chaos Timer
        if self.current_chaos:
            self.chaos_duration -= dt
            if self.chaos_duration <= 0:
                self.current_chaos = None
                self.active_gravity = GRAVITY

        # Update Rings
        current_speeds = self.original_ring_speeds
        if self.current_chaos == 'GLITCH': current_speeds = self.temp_ring_speeds
        
        for i in range(len(RINGS_CONFIG)):
            speed = current_speeds[i]
            modifier = 2.0 if self.current_chaos == 'TURBO' else 1.0
            self.ring_angles[i] += speed * modifier
            self.ring_angles[i] %= 360

        # Update Players
        active_count = 0
        for idx, p in enumerate(self.players):
            if p.finished: continue
            active_count += 1
            
            p.update_physics(dt, self.active_gravity, self.current_chaos, self.ring_angles, current_speeds)
            
            # Item Collision
            for item in self.items:
                if item.active and item.check_collision(p.pos_x, p.pos_y, BALL_RADIUS):
                    item.active = False
                    self.trigger_chaos(item.type)
                    self.last_event = ("item_collect", idx)
                    p.set_emotion("gain", 2.0) # Happy about item

            # Wall Collision logic (Local to player)
            self.check_player_collision(p, idx)
        
        if active_count == 0 and not self.game_over:
            self.game_over = True
            
        # PvP Collision Check
        if len(self.players) >= 2:
            self.check_pvp_collision()

    def check_pvp_collision(self):
        p1 = self.players[0]
        p2 = self.players[1]
        
        if p1.finished or p2.finished: return
        
        dx = p1.pos_x - p2.pos_x
        dy = p1.pos_y - p2.pos_y
        dist = math.hypot(dx, dy)
        
        min_dist = BALL_RADIUS * 2
        
        if dist < min_dist:
            # COLLISION DETECTED
            
            # 1. Resolve Overlap (Static)
            overlap = min_dist - dist
            if dist == 0: dist = 0.01 # Prevent zero division
            
            nx = dx / dist
            ny = dy / dist
            
            # Push apart equally
            p1.pos_x += nx * (overlap / 2)
            p1.pos_y += ny * (overlap / 2)
            p2.pos_x -= nx * (overlap / 2)
            p2.pos_y -= ny * (overlap / 2)
            
            # 2. Bounce (Dynamic - Elastic)
            # Relative velocity
            dvx = p1.vel_x - p2.vel_x
            dvy = p1.vel_y - p2.vel_y
            
            # Dot product along normal
            dot = dvx * nx + dvy * ny
            
            # Conservation of momentum (equal mass)
            # Swap velocity components along normal
            p1.vel_x -= dot * nx
            p1.vel_y -= dot * ny
            p2.vel_x += dot * nx
            p2.vel_y += dot * ny
            
            # Feedback Event
            self.last_event = ("pvp_collision", -1)
            
            # Emotional Reaction: Shock/Cry
            p1.set_emotion("cry", 0.5)
            p2.set_emotion("cry", 0.5)

    def check_player_collision(self, p, p_idx):
        if p.current_ring_index >= len(RINGS_CONFIG):
            if not p.finished:
                p.finished = True
                p.money += 5000 # Escaping bonus
                self.last_event = ("win", p_idx)
                p.set_emotion("gain", 5.0) # Very happy
                if self.winner_player is None:
                    self.winner_player = p
                    p.winner = True
            return

        ring = RINGS_CONFIG[p.current_ring_index]
        radius = ring["radius"]
        dist = math.hypot(p.pos_x, p.pos_y)
        
        if dist + BALL_RADIUS >= radius:
            angle_rad = math.atan2(p.pos_y, p.pos_x)
            angle_deg = math.degrees(angle_rad)
            if angle_deg < 0: angle_deg += 360
            
            hole_center = self.ring_angles[p.current_ring_index]
            half_gap = ring["gap"] / 2
            
            diff = abs(angle_deg - hole_center)
            if diff > 180: diff = 360 - diff
            
            if diff < half_gap:
                # Pass through
                p.current_ring_index += 1
                self.last_event = ("levelup", p_idx)
                p.set_emotion("gain", 1.0) # Progress is good
            else:
                # Bounce
                overlap = (dist + BALL_RADIUS) - radius
                if dist > 0:
                    norm_x = p.pos_x / dist
                    norm_y = p.pos_y / dist
                    p.pos_x -= norm_x * overlap
                    p.pos_y -= norm_y * overlap
                    
                    nx, ny = -norm_x, -norm_y
                    dot = p.vel_x * nx + p.vel_y * ny
                    
                    p.vel_x = p.vel_x - 2 * dot * nx
                    p.vel_y = p.vel_y - 2 * dot * ny
                    
                    p.vel_x *= BOUNCE_FACTOR
                    p.vel_y *= BOUNCE_FACTOR
                    
                    if ring["type"] == "green":
                        p.money += GAIN_PER_BOUNCE
                        self.last_event = ("bounce_gain", p_idx)
                        p.set_emotion("gain", 0.5)
                    else:
                        p.money -= LOSS_PER_BOUNCE
                        self.last_event = ("bounce_loss", p_idx)
                        p.set_emotion("loss", 0.8)
