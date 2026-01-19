import pygame

# --- WINDOW & WORLD ---
SCREEN_W = 1080
SCREEN_H = 1920
WORLD_W = 4000
WORLD_H = 4000

# --- PERFORMANCE ---
TARGET_FPS = 60

# --- BALANCE & GAMEPLAY ---
DIFFICULTY_RAMP_SEC = 45.0 # Seconds to double enemy stats
BOSS_SPAWN_TIME = 45.0
CORNER_MARGIN = 600
CORNER_TIMEOUT = 5.0

# --- COLORS (Neon Palette) ---
COLOR_BG = (5, 5, 15)
COLOR_GRID = (20, 20, 40)
COLOR_PLAYER = (0, 255, 255)
COLOR_WEAPON = (255, 0, 255)
COLOR_XP = (50, 255, 50)
COLOR_TEXT = (255, 255, 255)

# Enemy Specifics
COLOR_ENEMY_COMMON = (255, 50, 50)
COLOR_ENEMY_FAST = (255, 255, 100)
COLOR_ENEMY_TANK = (150, 50, 255)
COLOR_ENEMY_SWARM = (200, 200, 200)
COLOR_ENEMY_ELITE = (255, 140, 0)
COLOR_ENEMY_BOSS = (255, 0, 50)

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
