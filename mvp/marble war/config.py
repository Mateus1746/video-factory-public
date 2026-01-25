
# Configurações Gerais
WIDTH, HEIGHT = 1080, 1920
FPS = 60
TIMESTEP = 1.0 / FPS
TOTAL_FRAMES = 4800 # 80 segundos limite. A Morte Súbita garante o fim antes disso.
GRID_SIZE = 40 

# Configurações de Física
GRAVITY = (0, 0)
SPACE_DAMPING = 1.0 # 1.0 = Sem resistência do ar (Vácuo). Bolinhas não param.
MARBLE_RADIUS = 35
MARBLE_ELASTICITY = 0.95 # Muito elástico (quase 1.0)
MARBLE_FRICTION = 0.0 # Sem atrito
WALL_ELASTICITY = 1.0 # Paredes perfeitamente elásticas
WALL_FRICTION = 0.0
WALL_THICKNESS = 100

# Collision types
COLLISION_MARBLE = 1
COLLISION_PROJECTILE = 2
COLLISION_WALL = 3

# Audio thresholds
IMPULSE_THRESHOLD = 50
IMPULSE_TO_VOLUME = 2000.0

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
POWERUP_TYPES = ["speed", "size", "clone", "assassin", "magnet", "freeze"]
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

# Configurações Visual (Glow/Brush)
BRUSH_SIZE = 180 
BRUSH_ALPHA = 12  
MARBLE_GLOW_SIZE = 80 

# Configurações de Caos e Eventos
CHAOS_START_FRAME = 15 * FPS # Começa após 15s
ZONE_SHRINK_SPEED = 0.3 # Mais lento para dar tempo de brigar
ZONE_MIN_RADIUS = 300 # Espaço mínimo para não "esmagar" a física (aprox 20% da tela)
ZONE_BOUNCE_FACTOR = 1.2 # Força do "rebote" na borda do círculo (1.0 = elástico perfeito)

# Centralized Audio Paths
AUDIO_PATHS = {
    "collision": "assets/music/collision_48.wav",
    "powerup": "assets/music/powerup_48.wav",
    "elimination": "assets/music/elimination_48.wav",
    "tictoc": "assets/music/tictoc_48.wav",
    "bg": "assets/music/bg_48.wav"
} 
