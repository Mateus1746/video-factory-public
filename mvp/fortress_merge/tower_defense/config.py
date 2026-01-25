import os
WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION = 60
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
HEADLESS = os.getenv('HEADLESS', 'false').lower() == 'true'
