import os

# --- Sistema ---
DEBUG = True # Ativa logs e overlay visual
HEADLESS = os.environ.get("HEADLESS", "false").lower() == "true"
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "output")
WIDTH = int(os.environ.get("WIDTH", 1080))
HEIGHT = int(os.environ.get("HEIGHT", 1920))
FPS = int(os.environ.get("FPS", 30))
DURATION = int(os.environ.get("DURATION", 60))

# --- Cores (Paleta Cyberpunk) ---
COLORS = {
    "BG": (10, 12, 20),
    "GRID": (25, 30, 45),
    "CYAN": (0, 255, 240),
    "MAGENTA": (255, 0, 150),
    "GOLD": (255, 200, 0),
    "RED": (255, 50, 50),
    "GREEN": (50, 255, 50),
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "HP_BG": (50, 0, 0),
    "HP_FG": (0, 255, 100)
}

# --- Balanceamento ---
# Ajuste fino para garantir que o dano seja visível
BALANCE = {
    "BASE_HP": 100,
    "GOLD_START": 500, # Buff: Começa rico
    "TOWER_COST": 45,  # Buff: Torres mais baratas
    "TOWER_COST_SCALE": 1.12, # Buff: Inflação menor
    "ENEMY_HP_SCALING": 0.5, 
    "ENEMY_SPEED_SCALING": 0.006, 
    "TOWER_RANGE_BASE": 0.65, 
    "TOWER_DAMAGE_BASE": 20, 
}
