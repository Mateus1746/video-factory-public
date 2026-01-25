import pygame

# --- WINDOW & WORLD ---
SCREEN_W = 1080
SCREEN_H = 1920
WORLD_W = 4000
WORLD_H = 4000

# --- PERFORMANCE ---
TARGET_FPS = 60

# --- PLAYER ---
PLAYER_RADIUS = 40  # Duplicated from 20
PLAYER_SPEED = 300.0
PLAYER_MAX_HEALTH = 100
PLAYER_AI_DANGER_RADIUS = 400
PLAYER_AI_DANGER_CLOSE = 120
PLAYER_AI_INTEREST_WEIGHT = 2000

# --- WEAPON ---
WEAPON_ROTATION_SPEED = 4.2
WEAPON_DAMAGE = 12
WEAPON_ORBIT_RADIUS = 180 # Duplicated to match larger player
WEAPON_HIT_RADIUS = 40    # Duplicated from 20
WEAPON_INITIAL_ORBS = 2

# --- ENEMIES ---
# (Radius, Speed, Health, Damage) - Radii duplicated
ENEMY_STATS = {
    "common": {"radius": 36, "speed": 110, "health": 35,  "damage": 12},
    "fast":   {"radius": 28, "speed": 210, "health": 20,  "damage": 8},
    "tank":   {"radius": 70, "speed": 80,  "health": 200, "damage": 25},
    "swarm":  {"radius": 20, "speed": 160, "health": 10,  "damage": 5},
    "elite":  {"radius": 52, "speed": 100, "health": 500, "damage": 20},
    "boss":   {"radius": 180, "speed": 70,  "health": 10000, "damage": 50}
}

# --- COLORS (Neon Palette) ---
COLOR_BG = (5, 5, 15)
COLOR_GRID = (20, 20, 40)
COLOR_PLAYER = (0, 255, 255)
COLOR_WEAPON = (255, 0, 255)
COLOR_XP = (50, 255, 50)
COLOR_TEXT = (255, 255, 255)

COLOR_ENEMY_COMMON = (255, 50, 50)
COLOR_ENEMY_FAST = (255, 255, 100)
COLOR_ENEMY_TANK = (150, 50, 255)
COLOR_ENEMY_SWARM = (200, 200, 200)
COLOR_ENEMY_ELITE = (255, 140, 0)
COLOR_ENEMY_BOSS = (255, 0, 50)

# Map enemy types to colors
ENEMY_COLORS = {
    "common": COLOR_ENEMY_COMMON,
    "fast": COLOR_ENEMY_FAST,
    "tank": COLOR_ENEMY_TANK,
    "swarm": COLOR_ENEMY_SWARM,
    "elite": COLOR_ENEMY_ELITE,
    "boss": COLOR_ENEMY_BOSS
}

# --- BALANCE & GAMEPLAY ---
DIFFICULTY_RAMP_SEC = 40.0 
SPAWN_INTERVAL_INITIAL = 0.8
SPAWN_INTERVAL_MIN = 0.08
XP_MAX_INITIAL = 100
XP_SCALE_FACTOR = 1.4

# Events
EVENT_HORDE_TIMES = [12.0, 25.0, 38.0]
EVENT_BOSS_TIME = 45.0

# Corner Logic
CORNER_MARGIN = 600
CORNER_TIMEOUT = 5.0

# --- AUDIO ---
VOL_MUSIC = 0.04
VOL_SFX = 0.40

# --- ASSETS PATHS ---
PATH_MUSIC = [
    "assets/audio/music/dark-cyberpunk-aggressive-electro-235651.mp3",
    "assets/audio/music/aggressive-electronic-energetic-sport-177461.mp3"
]
SFX_MAP = {
    "hit": "assets/audio/sfx/thud-impact-sound-sfx-379990.mp3",
    "impact": "assets/audio/sfx/punch-04-383965.mp3",
    "kill": "assets/audio/sfx/slime-splat-2-219249.mp3",
    "level_up": "assets/audio/sfx/level-up-06-370051.mp3",
    "game_over": "assets/audio/sfx/negative_beeps-6008.mp3",
    "exp": "assets/audio/sfx/level-up-06-370051.mp3"
}
