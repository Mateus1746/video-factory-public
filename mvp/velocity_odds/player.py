import pygame
import math
import random
from config import *

class Player:
    def __init__(self, config_dict):
        self.name = config_dict["name"]
        self.color = config_dict["color"]
        self.start_offset = config_dict["start_pos"]
        
        # Load Sprites
        self.sprites = {}
        if "sprites" in config_dict:
            for key, path in config_dict["sprites"].items():
                try:
                    img = pygame.image.load(path)
                    # Scale to ball size * 2
                    self.sprites[key] = pygame.transform.scale(img, (BALL_RADIUS*2, BALL_RADIUS*2))
                except Exception as e:
                    print(f"Error loading {key} sprite for {self.name}: {e}")
                    self.sprites[key] = None
        elif "image" in config_dict:
             # Legacy support
            try:
                img = pygame.image.load(config_dict["image"])
                self.sprites["default"] = pygame.transform.scale(img, (BALL_RADIUS*2, BALL_RADIUS*2))
            except:
                pass

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
        if emotion in self.sprites and self.sprites[emotion]:
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
            gravity_effect = GRAVITY * 0.2
        elif chaos_mode == 'INVERT':
            gravity_effect = -GRAVITY

        # Integration
        time_scale = 1.0
        if chaos_mode == 'TURBO': time_scale = 1.8
        
        self.vel_y += gravity_effect * time_scale
        
        # Friction/Drag
        self.vel_x *= FRICTION
        self.vel_y *= FRICTION
        
        # Speed Cap
        speed_limit = MAX_SPEED
        if chaos_mode == 'TURBO': speed_limit = MAX_SPEED * 2
        
        curr_speed = math.hypot(self.vel_x, self.vel_y)
        if curr_speed > speed_limit:
            scale = speed_limit / curr_speed
            self.vel_x *= scale
            self.vel_y *= scale

        self.pos_x += self.vel_x * time_scale
        self.pos_y += self.vel_y * time_scale

    def draw(self, surface, center_x, center_y):
        # Calculate draw position
        dx = int(center_x + self.pos_x)
        dy = int(center_y + self.pos_y)
        
        # Select Sprite
        sprite = self.sprites.get(self.emotion)
        if not sprite:
            sprite = self.sprites.get("default")
            
        if sprite:
            # Draw Image centered
            rect = sprite.get_rect(center=(dx, dy))
            surface.blit(sprite, rect)
        else:
            # Fallback: Draw Circle
            pygame.draw.circle(surface, self.color, (dx, dy), BALL_RADIUS)
        
        # Add a subtle border to distinguish teams if colors are similar
        pygame.draw.circle(surface, WHITE, (dx, dy), BALL_RADIUS, 1)