import os

# Render Settings
WIDTH = 1080
HEIGHT = 1920
FPS = 60 # UNIFIED FPS SOURCE
DURATION = 180

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

# Environment
HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'