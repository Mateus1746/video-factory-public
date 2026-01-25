import pygame
import os

# Screen
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 1920
FPS = 60
CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Colors
BLACK = (10, 10, 15)
WHITE = (220, 220, 220)
NEON_GREEN = (50, 255, 120)
NEON_RED = (255, 60, 80)
COLOR_EVENT_INVERT = (255, 0, 255)
COLOR_EVENT_TURBO = (255, 255, 0)
COLOR_EVENT_MOON = (0, 255, 255)
COLOR_EVENT_GLITCH = (150, 150, 150)

# Visual Effects
TRAIL_LENGTH = 15
PARTICLE_CACHE_STEPS = 20
GLOW_INTENSITY = 3

# Chaos / Events System
EVENT_DURATION = 3.5

# Simulation & Balance
SPAWN_RATE_ITEMS = 0.85
SPAWN_OFFSET_START = 30
GLITCH_SPEED_RANGE = (-5.0, 5.0)

TURBO_MODIFIER_RINGS = 2.0
TURBO_TIMESCALE = 1.8
TURBO_SPEED_LIMIT_MULT = 2.0
MOON_GRAVITY_MULT = 0.2
INVERT_GRAVITY_MULT = -1.0

# Physics Constants (Scaled)
GRAVITY = 0.50
BOUNCE_FACTOR = 0.98 
MAX_SPEED = 25.0
FRICTION = 0.999     

# Assets Paths
ASSETS_DIR = "assets"
# Mude esta variável para trocar a rivalidade (Ex: tesla_vs_byd, iphone_vs_android)
ACTIVE_RIVALRY = "ferrari_vs_lamborghini" 
TEAMS_DIR = os.path.join(ASSETS_DIR, "teams", ACTIVE_RIVALRY)

# Battle Configuration
TEAM_A = {
    "name": "TEAM A",
    "color": (255, 50, 50),
    "sprites": {
        "default": os.path.join(TEAMS_DIR, "team1.png"),
        "gain": os.path.join(TEAMS_DIR, "team1-dinheiro.png"),
        "loss": os.path.join(TEAMS_DIR, "team1-triste.png"),
        "cry": os.path.join(TEAMS_DIR, "team1-chorando.png")
    },
    "start_pos": (-40, 0)      
}

TEAM_B = {
    "name": "TEAM B",
    "color": (255, 215, 0),
    "sprites": {
        "default": os.path.join(TEAMS_DIR, "team2.png"),
        "gain": os.path.join(TEAMS_DIR, "team2-dinheiro.png"),
        "loss": os.path.join(TEAMS_DIR, "team2-triste.png"),
        "cry": os.path.join(TEAMS_DIR, "team2-chorando.png")
    },
    "start_pos": (40, 0)       
}

# Economy
WIN_MONEY_BONUS = 5000
GAIN_PER_BOUNCE = 50.0
LOSS_PER_BOUNCE = 100.0
STARTING_MONEY = 1000.0

# Emotion Durations
EMOTION_GAIN_HAPPY_DURATION = 2.0
EMOTION_GAIN_WIN_DURATION = 5.0
EMOTION_GAIN_PROGRESS_DURATION = 1.0
EMOTION_LOSS_DURATION = 0.8
EMOTION_CRY_DURATION = 0.5

# Game Design (Scaled to 510px Max Radius)
RINGS_CONFIG = [
    {"radius": 75,  "type": "green", "speed": 1.5,  "gap": 65},
    {"radius": 130, "type": "red",   "speed": -1.3, "gap": 60},
    {"radius": 185, "type": "green", "speed": 1.1,  "gap": 55},
    {"radius": 240, "type": "red",   "speed": -1.0, "gap": 50},
    {"radius": 295, "type": "green", "speed": 0.9,  "gap": 45},
    {"radius": 350, "type": "red",   "speed": -0.8, "gap": 40},
    {"radius": 405, "type": "green", "speed": 0.7,  "gap": 35},
    {"radius": 460, "type": "red",   "speed": -0.6, "gap": 30},
    {"radius": 510, "type": "green", "speed": 0.5,  "gap": 25}
]

BALL_RADIUS = 23
