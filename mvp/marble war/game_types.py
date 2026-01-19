"""
Type definitions and data structures for Marble War.
"""

from dataclasses import dataclass
from typing import Tuple

import pygame


# ============================================================================
# TYPE ALIASES
# ============================================================================

Position = Tuple[int, int]
Color = Tuple[int, int, int]
ColorAlpha = Tuple[int, int, int, int]


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class AudioEvent:
    """Audio event for post-processing."""
    t: float
    name: str
    vol: float


@dataclass
class Particle:
    """Single particle for visual effects."""
    pos: pygame.Vector2
    vel: pygame.Vector2
    color: Color
    life: float = 1.0
