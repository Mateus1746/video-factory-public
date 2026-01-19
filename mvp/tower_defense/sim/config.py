"""
Configuration constants for the Tower Defense simulation.
"""

# Video Settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 60

# Colors (Neon/Cyberpunk Palette)
COLOR_BG_DARK = (10, 10, 25)
COLOR_GRID = (30, 30, 60)
COLOR_WALL = (0, 255, 255) # Cyan neon
COLOR_WALL_DAMAGED = (255, 50, 50)
COLOR_HP_BAR_BG = (50, 0, 0)
COLOR_HP_BAR_FG = (255, 0, 0)

# Zombie Colors
COLOR_ZOMBIE_NORMAL = (255, 0, 100) # Magenta
COLOR_ZOMBIE_FAST = (255, 150, 0)   # Orange
COLOR_ZOMBIE_TANK = (150, 0, 200)   # Deep Purple
COLOR_ZOMBIE_GLOW = (150, 0, 60)

# Soldier Colors
COLOR_SOLDIER_RIFLE = (50, 150, 255)   # Electric Blue
COLOR_SOLDIER_SHOTGUN = (0, 255, 100)  # Neon Green
COLOR_SOLDIER_SNIPER = (255, 255, 0)   # Yellow

COLOR_PROJECTILE = (200, 255, 255)
COLOR_TEXT_MAIN = (255, 255, 255)
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
    'rifle':   {'range': 900,  'rate': 8,  'cost': 200, 'color': COLOR_SOLDIER_RIFLE, 'dmg': 1.5}, 
    'shotgun': {'range': 400,  'rate': 45, 'cost': 450, 'color': COLOR_SOLDIER_SHOTGUN, 'dmg': 4},
    'sniper':  {'range': 1200, 'rate': 55, 'cost': 900, 'color': COLOR_SOLDIER_SNIPER, 'dmg': 30},
    'minigun': {'range': 600,  'rate': 2,  'cost': 1300, 'color': (255, 100, 0),       'dmg': 0.8}, 
    'rocket':  {'range': 1000, 'rate': 110,'cost': 1600, 'color': (100, 100, 100),     'dmg': 50},
    'flame':   {'range': 300,  'rate': 2,  'cost': 1400, 'color': (255, 50, 0),        'dmg': 0.5}, # Short range, rapid fire dot
    'railgun': {'range': 1200, 'rate': 90, 'cost': 2000, 'color': (0, 255, 255),       'dmg': 20}   # Piercing shot
}

# EVENTS
EVENT_CHANCE = 0.005 # Chance per frame (approx every 3-4 sec check)
COLOR_EVENT_MIST = (0, 50, 0, 100) # Green tint
COLOR_EVENT_BOSS = (50, 0, 0, 100) # Red tint
PROJECTILE_SPEED = 35
