import os
import random

# --- Sistema ---
DEBUG = True 
HEADLESS = os.environ.get("HEADLESS", "false").lower() == "true"
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "output")
WIDTH = int(os.environ.get("WIDTH", 1080))
HEIGHT = int(os.environ.get("HEIGHT", 1920))
FPS = int(os.environ.get("FPS", 30))
DURATION = int(os.environ.get("DURATION", 60))

# --- Paletas de Temas ---
THEMES = {
    "CYBERPUNK": {
        "BG": (10, 12, 20), "GRID": (25, 30, 45), "CYAN": (0, 255, 240),
        "MAGENTA": (255, 0, 150), "GOLD": (255, 200, 0), "RED": (255, 50, 50),
        "GREEN": (50, 255, 50), "WHITE": (255, 255, 255), "BLACK": (0, 0, 0),
        "HP_BG": (50, 0, 0), "HP_FG": (0, 255, 100)
    },
    "MAGMA": {
        "BG": (20, 5, 5), "GRID": (40, 10, 10), "CYAN": (255, 150, 0), # Laranja
        "MAGENTA": (255, 50, 0), "GOLD": (255, 255, 100), "RED": (200, 20, 20),
        "GREEN": (100, 255, 0), "WHITE": (255, 220, 200), "BLACK": (10, 0, 0),
        "HP_BG": (50, 10, 10), "HP_FG": (255, 100, 0)
    },
    "FOREST": {
        "BG": (5, 20, 10), "GRID": (10, 40, 20), "CYAN": (100, 255, 150),
        "MAGENTA": (200, 100, 255), "GOLD": (255, 255, 50), "RED": (255, 80, 80),
        "GREEN": (50, 255, 50), "WHITE": (220, 255, 220), "BLACK": (0, 10, 0),
        "HP_BG": (20, 40, 20), "HP_FG": (100, 255, 100)
    },
    "RETRO_CONSOLE": {
        "BG": (155, 188, 15), "GRID": (139, 172, 15), "CYAN": (48, 98, 48),
        "MAGENTA": (15, 56, 15), "GOLD": (15, 56, 15), "RED": (15, 56, 15),
        "GREEN": (48, 98, 48), "WHITE": (15, 56, 15), "BLACK": (139, 172, 15),
        "HP_BG": (139, 172, 15), "HP_FG": (15, 56, 15)
    }
}

# Escolhe um tema aleatório na inicialização do módulo
CURRENT_THEME_NAME = random.choice(list(THEMES.keys()))
COLORS = THEMES[CURRENT_THEME_NAME]
print(f"🎨 [CONFIG] Tema Selecionado: {CURRENT_THEME_NAME}")

# --- Balanceamento ---
# Ajuste fino para garantir que o dano seja visível
BALANCE = {
    "BASE_HP": 100,
    "GOLD_START": 800, # Buff: Começa MUITO rico (era 500) para preencher o grid rápido
    "TOWER_COST": 45,  
    "TOWER_COST_SCALE": 1.12, 
    "ENEMY_HP_SCALING": 0.5, 
    "ENEMY_SPEED_SCALING": 0.006, 
    "TOWER_RANGE_BASE": 0.65, 
    "TOWER_DAMAGE_BASE": 20,
    
    # New Constants (Refactoring)
    "ENEMY_DAMAGE_TO_BASE": 15,
    "SPAWN_RATE_MIN": 5, # Buff: Spawns mais rápidos no late game (era 15)
    "SPAWN_RATE_BASE": 40, # Buff: Começa mais rápido (era 60)
    "SPAWN_RATE_DECAY": 5,
    "GOLD_REWARD_BASE": 25,
    "BOSS_GOLD_MULTIPLIER": 5,
    
    # Physics / Combat
    "EXPLOSION_RADIUS": 150,
    "FIRE_DAMAGE_MULTIPLIER": 0.8,
    
    # Visuals
    "SHAKE_ON_HIT": 20,
    "SHAKE_ON_KILL": 5,
    "SHAKE_ON_MERGE": 5,
    "PARTICLE_COUNT_HIT": 20,
    "PARTICLE_COUNT_KILL": 10,
    "PARTICLE_COUNT_MERGE": 15,
    "PARTICLE_SIZE_HIT": 8,
    "BASE_ROTATION_SPEED": 2,
}
