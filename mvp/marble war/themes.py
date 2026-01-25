"""
Visual Theme Engine for Marble War.
Controls colors, fonts, and post-processing styles.
"""

import random
from dataclasses import dataclass
from typing import Tuple

@dataclass
class Theme:
    name: str
    bg_color: Tuple[int, int, int]
    grid_color: Tuple[int, int, int]
    wall_color: Tuple[int, int, int]
    text_color: Tuple[int, int, int]
    bloom_enabled: bool
    font_name: str = "Arial"

class ThemeManager:
    @staticmethod
    def get_random_theme() -> Theme:
        themes = [
            Theme(
                name="Cyberpunk",
                bg_color=(5, 5, 8),
                grid_color=(20, 20, 30),
                wall_color=(0, 255, 255),
                text_color=(255, 255, 255),
                bloom_enabled=True
            ),
            Theme(
                name="Matrix",
                bg_color=(0, 10, 0),
                grid_color=(0, 50, 0),
                wall_color=(0, 255, 0),
                text_color=(0, 255, 0),
                bloom_enabled=True,
                font_name="Courier" # Monospace look
            ),
            Theme(
                name="Candy Land",
                bg_color=(255, 240, 245), # Pinkish White
                grid_color=(255, 200, 210),
                wall_color=(255, 105, 180), # Hot Pink
                text_color=(100, 50, 100),
                bloom_enabled=False # Clean look
            ),
            Theme(
                name="Blueprint",
                bg_color=(0, 50, 150), # Blueprint Blue
                grid_color=(255, 255, 255), # White lines
                wall_color=(255, 255, 255),
                text_color=(255, 255, 255),
                bloom_enabled=False
            ),
            Theme(
                name="Paper Sketch",
                bg_color=(250, 250, 250), # Paper White
                grid_color=(200, 200, 200), # Faint pencil lines
                wall_color=(0, 0, 0), # Sharp ink
                text_color=(0, 0, 0),
                bloom_enabled=False,
                font_name="Comic Sans MS" # Hand-drawn feel (if available, fallback to Arial)
            ),
            Theme(
                name="Midnight",
                bg_color=(10, 10, 10),
                grid_color=(30, 30, 30),
                wall_color=(100, 100, 100),
                text_color=(200, 200, 200),
                bloom_enabled=True
            )
        ]
        
        selected = random.choice(themes)
        print(f"🎨 Selected Theme: {selected.name}")
        return selected
