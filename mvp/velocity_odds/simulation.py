import pygame
import math
import random
from config import *
from items import PowerUp
from player import Player

class Simulation:
    def __init__(self):
        self.players = [Player(TEAM_A), Player(TEAM_B)]
        self.audio_events = [] 
        self.elapsed_time = 0.0
        self.reset()

    def reset(self):
        for p in self.players: p.reset()
        self.game_over = False
        self.winner_player = None
        self.audio_events = []
        self.elapsed_time = 0.0
        self.ring_angles = [random.uniform(0, 360) for _ in RINGS_CONFIG]
        self.original_ring_speeds = [r["speed"] for r in RINGS_CONFIG]
        self.current_chaos = None 
        self.chaos_duration = 0
        self.spawn_items()

    def _record_event(self, event_type, player_idx):
        self.last_event = (event_type, player_idx)
        self.audio_events.append({"time": self.elapsed_time, "type": event_type, "player": player_idx})

    def spawn_items(self):
        self.items = []
        types = ['INVERT', 'MOON', 'TURBO', 'GLITCH']
        prev_r = SPAWN_OFFSET_START
        for ring in RINGS_CONFIG:
            if random.random() < SPAWN_RATE_ITEMS:
                r = (prev_r + ring["radius"]) / 2
                theta = random.uniform(0, 2 * math.pi)
                self.items.append(PowerUp(r * math.cos(theta), r * math.sin(theta), random.choice(types)))
            prev_r = ring["radius"]

    def trigger_chaos(self, type_name):
        self.current_chaos = type_name
        self.chaos_duration = EVENT_DURATION
        self._record_event("chaos_trigger", -1) 
        if self.current_chaos == 'GLITCH':
            self.temp_ring_speeds = [random.uniform(*GLITCH_SPEED_RANGE) for _ in RINGS_CONFIG]

    def _apply_rubber_banding(self, dt):
        if self.game_over or len(self.players) < 2: return
        p1, p2 = self.players[0], self.players[1]
        diff = p1.current_ring_index - p2.current_ring_index
        if abs(diff) >= 2:
            trailer = p2 if diff > 0 else p1
            assist = 0.12
            trailer.vel_y += assist if self.current_chaos != 'INVERT' else -assist

    def update(self, dt):
        self.elapsed_time += dt
        self._apply_rubber_banding(dt)
        if self.current_chaos:
            self.chaos_duration -= dt
            if self.chaos_duration <= 0:
                self.current_chaos = None
        
        speeds = self.temp_ring_speeds if self.current_chaos == 'GLITCH' else self.original_ring_speeds
        for i in range(len(RINGS_CONFIG)):
            mod = TURBO_MODIFIER_RINGS if self.current_chaos == 'TURBO' else 1.0
            self.ring_angles[i] = (self.ring_angles[i] + speeds[i] * mod) % 360

        active_count = 0
        for idx, p in enumerate(self.players):
            if p.finished: continue
            active_count += 1
            p.update_physics(dt, GRAVITY, self.current_chaos, self.ring_angles, speeds)
            
            for item in self.items:
                if item.active and item.check_collision(p.pos_x, p.pos_y, BALL_RADIUS):
                    item.active = False
                    self.trigger_chaos(item.type)
                    self._record_event("item_collect", idx)
                    p.set_emotion("gain", EMOTION_GAIN_HAPPY_DURATION)

            self.check_player_collision(p, idx)
        
        if active_count == 0 and not self.game_over:
            self.game_over = True
            # DETERMINAR VENCEDOR POR DINHEIRO NO FINAL
            self.winner_player = max(self.players, key=lambda x: x.money)
            self.winner_player.winner = True
            
        if len(self.players) >= 2: self.check_pvp_collision()

    def check_pvp_collision(self):
        p1, p2 = self.players[0], self.players[1]
        if p1.finished or p2.finished: return
        dx, dy = p1.pos_x - p2.pos_x, p1.pos_y - p2.pos_y
        d2 = dx*dx + dy*dy
        min_d = BALL_RADIUS * 2
        if d2 < min_d * min_d:
            dist = math.sqrt(d2) or 0.01
            nx, ny = dx/dist, dy/dist
            overlap = min_d - dist
            p1.pos_x += nx * overlap/2
            p1.pos_y += ny * overlap/2
            p2.pos_x -= nx * overlap/2
            p2.pos_y -= ny * overlap/2
            dot = (p1.vel_x - p2.vel_x) * nx + (p1.vel_y - p2.vel_y) * ny
            p1.vel_x -= dot * nx
            p1.vel_y -= dot * ny
            p2.vel_x += dot * nx
            p2.vel_y += dot * ny
            self._record_event("pvp_collision", -1)
            p1.set_emotion("cry", EMOTION_CRY_DURATION); p2.set_emotion("cry", EMOTION_CRY_DURATION)

    def check_player_collision(self, p, p_idx):
        if p.current_ring_index >= len(RINGS_CONFIG):
            if not p.finished:
                p.finished = True
                p.money += WIN_MONEY_BONUS # Bônus por terminar (ainda relevante)
                self._record_event("win", p_idx)
                p.set_emotion("gain", EMOTION_GAIN_WIN_DURATION)
            return

        ring = RINGS_CONFIG[p.current_ring_index]
        radius = ring["radius"]
        dist = math.hypot(p.pos_x, p.pos_y)
        
        if dist + BALL_RADIUS >= radius:
            angle = math.degrees(math.atan2(p.pos_y, p.pos_x)) % 360
            angular_radius = math.degrees(math.asin(min(1.0, BALL_RADIUS / radius)))
            time_factor = min(1.0, self.elapsed_time / 50.0)
            cur_gap = ring["gap"] + (time_factor * 40)
            gap_center = self.ring_angles[p.current_ring_index]
            
            diff = abs(angle - gap_center)
            if diff > 180: diff = 360 - diff
            
            if diff + (angular_radius * 0.8) < cur_gap / 2:
                if dist > radius:
                    p.current_ring_index += 1
                    self._record_event("levelup", p_idx)
                    p.set_emotion("gain", EMOTION_GAIN_PROGRESS_DURATION)
            else:
                overlap = (dist + BALL_RADIUS) - radius
                if dist > 0:
                    nx, ny = p.pos_x/dist, p.pos_y/dist
                    p.pos_x -= nx * overlap
                    p.pos_y -= ny * overlap
                    dot = p.vel_x * (-nx) + p.vel_y * (-ny)
                    p.vel_x = (p.vel_x - 2 * dot * (-nx)) * BOUNCE_FACTOR
                    p.vel_y = (p.vel_y - 2 * dot * (-ny)) * BOUNCE_FACTOR
                    
                    if ring["type"] == "green":
                        p.money += GAIN_PER_BOUNCE
                        self._record_event("bounce_gain", p_idx)
                    else:
                        p.money -= LOSS_PER_BOUNCE
                        self._record_event("bounce_loss", p_idx)
                        p.set_emotion("loss", EMOTION_LOSS_DURATION)