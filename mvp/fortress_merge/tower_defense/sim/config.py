"""
Configuration constants for the Tower Defense simulation.
"""

import random

# Video Settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 60

# --- THEMES ---
THEMES = {
    "NEON_CYBER": {
        "BG": (10, 10, 25), "GRID": (30, 30, 60), "WALL": (0, 255, 255),
        "Z_NORMAL": (255, 0, 100), "Z_FAST": (255, 150, 0), "Z_TANK": (150, 0, 200),
        "SOLDIER_1": (50, 150, 255), "SOLDIER_2": (0, 255, 100), "SOLDIER_3": (255, 255, 0),
        "PROJ": (200, 255, 255), "TEXT": (255, 255, 255)
    },
    "TOXIC_WASTE": {
        "BG": (10, 20, 10), "GRID": (20, 40, 20), "WALL": (100, 255, 50),
        "Z_NORMAL": (200, 100, 255), "Z_FAST": (255, 255, 0), "Z_TANK": (50, 100, 50),
        "SOLDIER_1": (255, 100, 50), "SOLDIER_2": (200, 200, 200), "SOLDIER_3": (100, 255, 255),
        "PROJ": (100, 255, 100), "TEXT": (200, 255, 200)
    },
    "CRIMSON_NIGHT": {
        "BG": (20, 5, 5), "GRID": (50, 10, 10), "WALL": (255, 50, 50),
        "Z_NORMAL": (100, 255, 255), "Z_FAST": (200, 200, 200), "Z_TANK": (50, 0, 0),
        "SOLDIER_1": (255, 200, 0), "SOLDIER_2": (255, 100, 100), "SOLDIER_3": (255, 255, 255),
        "PROJ": (255, 100, 0), "TEXT": (255, 200, 200)
    }
}

CURRENT_THEME_NAME = random.choice(list(THEMES.keys()))
PALETTE = THEMES[CURRENT_THEME_NAME]
print(f"🎨 [TOWER DEFENSE] Theme: {CURRENT_THEME_NAME}")

# Mapeamento para Variáveis Globais (Backward Compatibility)
COLOR_BG_DARK = PALETTE["BG"]
COLOR_GRID = PALETTE["GRID"]
COLOR_WALL = PALETTE["WALL"]
COLOR_WALL_DAMAGED = (255, 50, 50)
COLOR_HP_BAR_BG = (50, 0, 0)
COLOR_HP_BAR_FG = (255, 0, 0)

# Zombie Colors
COLOR_ZOMBIE_NORMAL = PALETTE["Z_NORMAL"]
COLOR_ZOMBIE_FAST = PALETTE["Z_FAST"]
COLOR_ZOMBIE_TANK = PALETTE["Z_TANK"]
COLOR_ZOMBIE_GLOW = (150, 0, 60)

# Soldier Colors
COLOR_SOLDIER_RIFLE = PALETTE["SOLDIER_1"]
COLOR_SOLDIER_SHOTGUN = PALETTE["SOLDIER_2"]
COLOR_SOLDIER_SNIPER = PALETTE["SOLDIER_3"]

COLOR_PROJECTILE = PALETTE["PROJ"]
COLOR_TEXT_MAIN = PALETTE["TEXT"]
COLOR_GOLD = (255, 215, 0)

# Particle Settings
PARTICLE_COUNT = 15
PARTICLE_LIFESPAN = 20 # Frames
PARTICLE_SIZE = 4

# Simulation Settings
SPAWN_OFFSET_X = VIDEO_WIDTH + 50
BASE_X_LIMIT = 200 
BASE_MAX_HEALTH = 600 # Reduced from 1000

# Spawning Logic
SPAWN_DURATION_SEC = 25 
SPAWN_END_FRAME = SPAWN_DURATION_SEC * FPS
MAX_SIMULATION_FRAMES = 60 * FPS 

# Economy
STARTING_MONEY = 400 # Nerfed from 800 (Harder start)
MONEY_PER_KILL = 22  # Nerfed from 35

# Entity Stats
# ZOMBIES
ZOMBIE_STATS = {
    'normal': {'speed': (3, 6), 'hp': 4, 'radius': 18, 'damage': 15}, # HP 2->4
    'fast':   {'speed': (8, 12), 'hp': 2, 'radius': 12, 'damage': 8},
    'tank':   {'speed': (1, 2),  'hp': 100, 'radius': 35, 'damage': 50} # HP 30->100 (BOSS)
}

# SOLDIERS
SOLDIER_STATS = {
    'rifle':   {'range': 900,  'rate': 8,  'cost': 100, 'color': COLOR_SOLDIER_RIFLE, 'dmg': 1.5}, 
    'shotgun': {'range': 400,  'rate': 45, 'cost': 225, 'color': COLOR_SOLDIER_SHOTGUN, 'dmg': 4},
    'sniper':  {'range': 1200, 'rate': 55, 'cost': 450, 'color': COLOR_SOLDIER_SNIPER, 'dmg': 30},
    'minigun': {'range': 600,  'rate': 2,  'cost': 650, 'color': (255, 100, 0),       'dmg': 0.8}, 
    'rocket':  {'range': 1000, 'rate': 110,'cost': 800, 'color': (100, 100, 100),     'dmg': 50},
    'flame':   {'range': 300,  'rate': 2,  'cost': 700, 'color': (255, 50, 0),        'dmg': 0.5}, 
    'railgun': {'range': 1200, 'rate': 90, 'cost': 1000, 'color': (0, 255, 255),       'dmg': 20}   
}

# EVENTS
EVENT_CHANCE = 0.005 # Chance per frame (approx every 3-4 sec check)
COLOR_EVENT_MIST = (0, 50, 0, 100) # Green tint
COLOR_EVENT_BOSS = (50, 0, 0, 100) # Red tint
PROJECTILE_SPEED = 35
