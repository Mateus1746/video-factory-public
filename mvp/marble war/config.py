
# Configurações Gerais
WIDTH, HEIGHT = 1080, 1920
FPS = 60
TIMESTEP = 1.0 / FPS
TOTAL_FRAMES = 99999 # Nexus: Modo Batalha Total  # 15 segundos para teste rápido
GRID_SIZE = 40 

# Configurações de Física
GRAVITY = (0, 0)
DAMPING = 0.85 
MARBLE_RADIUS = 35
MARBLE_ELASTICITY = 0.95
MARBLE_FRICTION = 0.1
WALL_ELASTICITY = 0.9
WALL_FRICTION = 0.2

# Configurações de Arena e UI
PLAY_WIDTH = WIDTH

# Configurações de Jogo
SPAWN_INTERVAL = 0.5 
MAX_MARBLES_PER_TEAM = 40
TOTAL_TEAMS = 4

# Cores Neon Aesthetic
COLOR_BG = (5, 5, 8)
COLOR_SIDEBAR_BG = (2, 2, 4)
COLOR_RED = (255, 30, 80)    # Vermelho Neon
COLOR_BLUE = (0, 150, 255)   # Azul Neon
COLOR_YELLOW = (255, 230, 0) # Amarelo Neon
COLOR_GREEN = (0, 255, 120)  # Verde Neon
COLOR_WHITE = (240, 240, 255)

# Mapeamento de Cores por Time
TEAM_COLORS = {
    "team_red": COLOR_RED,
    "team_blue": COLOR_BLUE,
    "team_yellow": COLOR_YELLOW,
    "team_green": COLOR_GREEN
}

# Configurações de Power-Ups
POWERUP_SPAWN_INTERVAL = 5.0 # Segundos
POWERUP_RADIUS = 40
POWERUP_TYPES = ["speed", "size", "clone", "assassin"]
POWERUP_DURATION = 5.0
SPEED_MULTIPLIER = 1.6 # Diminuído conforme pedido (antes era 2.5)
BRUSH_MULTIPLIER = 3

# Configurações de Projéteis
PROJECTILE_SPEED = 700
PROJECTILE_RADIUS = 8
PROJECTILE_LIFETIME = 2.5 
ASSASSIN_SHOTS = 3
ASSASSIN_FIRE_RATE = 0.75

# Configurações da Bomba (Batatinha Quente)
BOMB_START_FRAME = 20 * FPS 
BOMB_DURATION = 5.0
BOMB_TIMER_SIZE = 60

# Configurações de Visual (Glow/Brush)
BRUSH_SIZE = 180 
BRUSH_ALPHA = 12  
MARBLE_GLOW_SIZE = 80 
