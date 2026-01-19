import pygame

# Screen
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 1920
FPS = 60
CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Colors
BLACK = (10, 10, 15)
WHITE = (220, 220, 220)
RED_ZONE = (255, 50, 50)
GREEN_ZONE = (50, 255, 100)
BALL_COLOR = (255, 255, 255)

# Visual Effects
NEON_GREEN = (50, 255, 120)
NEON_RED = (255, 60, 80)
NEON_BLUE = (60, 150, 255)
TRAIL_LENGTH = 15
GLOW_INTENSITY = 3  # Number of layers for glow effect

# Chaos / Events System
CHAOS_INTERVAL_MIN = 4.0  # Seconds
CHAOS_INTERVAL_MAX = 8.0
EVENT_DURATION = 3.5      # How long an anomaly lasts

# Event Colors
COLOR_EVENT_INVERT = (255, 0, 255) # Magenta
COLOR_EVENT_TURBO = (255, 255, 0)  # Yellow
COLOR_EVENT_MOON = (0, 255, 255)   # Cyan
COLOR_EVENT_GLITCH = (150, 150, 150) # Grey

# Physics Constants
GRAVITY = 0.25       # Low gravity = longer airtime
BOUNCE_FACTOR = 1.0  
MAX_SPEED = 15.0
FRICTION = 1.0       

# Battle Configuration
TEAM_A = {
    "name": "FERRARI",
    "color": (255, 0, 0),      # Red
    "sprites": {
        "default": "assets/teams/ferrari_vs_lamborghini/ferrari-feliz.png",
        "gain": "assets/teams/ferrari_vs_lamborghini/ferrari-dinheiro.png",
        "loss": "assets/teams/ferrari_vs_lamborghini/ferrari-triste.png",
        "cry": "assets/teams/ferrari_vs_lamborghini/ferrari-chorando.png"
    },
    "start_pos": (-50, 0)      
}

TEAM_B = {
    "name": "LAMBORGHINI",
    "color": (255, 215, 0),    # Gold/Yellow
    "sprites": {
        "default": "assets/teams/ferrari_vs_lamborghini/lamborghini-feliz.png",
        "gain": "assets/teams/ferrari_vs_lamborghini/lamborghini-dinheiro.png",
        "loss": "assets/teams/ferrari_vs_lamborghini/lamborghini-triste.png",
        "cry": "assets/teams/ferrari_vs_lamborghini/lamborghini-chorando.png"
    },
    "start_pos": (50, 0)       
}

# Economy
GAIN_PER_BOUNCE = 50.0
LOSS_PER_BOUNCE = 100.0
STARTING_MONEY = 1000.0

# Game Design
# Rings: Radius, Type (Green/Red), Rotation Speed (deg/frame), Gap Size (deg)
# Extended to 9 rings with tighter gaps for ~45s duration
RINGS_CONFIG = [
    {"radius": 50,  "type": "green", "speed": 1.2,  "gap": 50}, # Start Easy
    {"radius": 85,  "type": "red",   "speed": -1.0, "gap": 45},
    {"radius": 120, "type": "green", "speed": 0.9,  "gap": 40},
    {"radius": 155, "type": "red",   "speed": -0.8, "gap": 35},
    {"radius": 190, "type": "green", "speed": 0.7,  "gap": 30},
    {"radius": 225, "type": "red",   "speed": -0.6, "gap": 25}, # Getting tight
    {"radius": 260, "type": "green", "speed": 0.5,  "gap": 20},
    {"radius": 295, "type": "red",   "speed": -0.5, "gap": 15}, # Very tight
    {"radius": 330, "type": "green", "speed": 0.4,  "gap": 12}  # Hardcore finish
]

BALL_RADIUS = 15