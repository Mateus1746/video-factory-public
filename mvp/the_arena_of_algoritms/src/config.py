# Screen
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 1920
HALF_HEIGHT = SCREEN_HEIGHT // 2
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (10, 10, 15)
YELLOW = (255, 230, 50)
PINK = (255, 80, 150)
GRAY = (60, 60, 70)
NEON_BLUE = (0, 255, 255)
NEON_GREEN = (50, 255, 50)
PURPLE = (180, 50, 255)

# Rings
RING_RADII = [100, 180, 260, 340]
RING_HP = [22500, 112500, 450000, 2070000] # Increased CORE HP (+15%)
RING_THICKNESS = 12
RING_COLORS = [NEON_BLUE, NEON_GREEN, PURPLE, (255, 100, 0)] # Specific colors for each layer

# Fibonacci
GOLDEN_RATIO = 1.61803398875
GOLDEN_ANGLE = 2.39996 # Radians (137.5 degrees)
FIB_SPEED = 1000       # Slightly faster
SPIRAL_RADIUS = 25
FIB_DAMAGE = 6000       # Adjusted (Buffed to ~45s target)

# Spawner
SPAWN_RATE = 0.03        # Faster spawns
BALL_SPEED = 700         # Faster burst
BALL_RADIUS = 10         
BALL_DAMAGE = 180        # Nerfed (was too fast)
MAX_BALLS = 400          # More chaos
BALL_SPAWN_COOLDOWN = 0.08

# Physics
GRAVITY = 900.0          # Strong gravity for weight
FRICTION = 0.999         # Air resistance
WALL_BOUNCE = 0.9        # Energy loss on bounce

# Chaos Jumper
CHAOS_JUMP_INTERVAL = 0.4
CHAOS_PROJECTILE_SPEED = 800
CHAOS_BASE_DAMAGE = 18000
CHAOS_COLOR = (255, 50, 50)

# Snake Eater
SNAKE_SPEED = 600
SNAKE_DAMAGE = 60000
SNAKE_COLOR = (50, 255, 100)

# Orbit Striker
STRIKER_RADIUS = 360
STRIKER_SPEED = 2.0
STRIKER_FIRE_RATE = 0.035
STRIKER_PROJ_SPEED = 1200
STRIKER_DAMAGE = 2800
STRIKER_COLOR = (0, 255, 128)

# Laser Sweeper
LASER_SPEED = 300
LASER_DPS = 35000
LASER_SCAN_RANGE = 350
LASER_COLOR = (50, 255, 255)


# Audio Settings
SAMPLE_RATE = 44100
PIANO_SCALE = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25] # C4 to C5
FIB_PITCH = 440.0
SPAWN_PITCH_BASE = 261.63

# Export Settings
EXPORT_MODE = True
DEBUG_MODE = True # Enable comprehensive telemetry and debug overlays
FRAMES_DIR = "frames"
PREVIEW_RES = (720, 1280)
FINAL_RES = (1080, 1920)
