import math
import random
from config import *

class Player:
    def __init__(self, config_dict):
        self.name = config_dict["name"]
        self.color = config_dict["color"]
        self.start_offset = config_dict["start_pos"]
        
        # Identity for Renderer
        self.team_id = "TEAM_A" if config_dict == TEAM_A else "TEAM_B"
        
        self.reset()

    def reset(self):
        self.money = STARTING_MONEY
        self.finished = False
        self.winner = False
        
        # Emotion System
        self.emotion = "default"
        self.emotion_timer = 0.0
        
        # Position (Relative to Center)
        self.pos_x = self.start_offset[0]
        self.pos_y = self.start_offset[1]
        
        # Velocity
        self.vel_x = random.uniform(-4, 4)
        self.vel_y = random.uniform(-4, 4)
        
        self.current_ring_index = 0

    def set_emotion(self, emotion, duration=1.0):
        """Set a temporary emotion for the player."""
        self.emotion = emotion
        self.emotion_timer = duration

    def update_physics(self, dt, active_gravity, chaos_mode, ring_angles, ring_speeds):
        if self.finished: return

        # Update Emotion
        if self.emotion_timer > 0:
            self.emotion_timer -= dt
            if self.emotion_timer <= 0:
                self.emotion = "default"

        # Apply Chaos Modifiers
        sim_dt = dt
        gravity_effect = active_gravity
        
        if chaos_mode == 'TURBO':
            sim_dt = dt * 2.0
        elif chaos_mode == 'MOON':
            gravity_effect = GRAVITY * MOON_GRAVITY_MULT
        elif chaos_mode == 'INVERT':
            gravity_effect = GRAVITY * INVERT_GRAVITY_MULT

        # Integration
        time_scale = 1.0
        if chaos_mode == 'TURBO': time_scale = TURBO_TIMESCALE
        
        self.vel_y += gravity_effect * time_scale
        
        # Friction/Drag
        self.vel_x *= FRICTION
        self.vel_y *= FRICTION
        
        # Speed Cap
        speed_limit = MAX_SPEED
        if chaos_mode == 'TURBO': speed_limit = MAX_SPEED * TURBO_SPEED_LIMIT_MULT
        
        curr_speed = math.hypot(self.vel_x, self.vel_y)
        if curr_speed > speed_limit:
            scale = speed_limit / curr_speed
            self.vel_x *= scale
            self.vel_y *= scale

        self.pos_x += self.vel_x * time_scale
        self.pos_y += self.vel_y * time_scale