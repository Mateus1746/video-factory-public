"""
Arena Generator for Marble War.
Creates procedural map layouts to ensure every video is unique.
"""
import random
import math
import pymunk
import pygame
from typing import List, Tuple

import config

class ArenaGenerator:
    def __init__(self, space: pymunk.Space):
        self.space = space
        self.obstacles: List[pymunk.Shape] = []
        self.moving_bodies: List[pymunk.Body] = []
        
    def generate(self, difficulty: int = 1) -> str:
        """
        Generates a random layout.
        Returns the name of the layout type.
        """
        # Clear previous (if any)
        self.clear()
        
        layout_types = [
            "empty", "columns", "central_block", "x_cross", 
            "grid_pegs", "spinners", "funnel"
        ]
        
        # Weighted choice: less likely to get "empty"
        weights = [5, 20, 20, 20, 20, 10, 5]
        layout = random.choices(layout_types, weights=weights, k=1)[0]
        
        print(f"🏟️ Generating Arena: {layout.upper()}")
        
        if layout == "columns":
            self._create_columns()
        elif layout == "central_block":
            self._create_central_block()
        elif layout == "x_cross":
            self._create_x_cross()
        elif layout == "grid_pegs":
            self._create_pegs()
        elif layout == "spinners":
            self._create_spinners()
        elif layout == "funnel":
            self._create_funnel()
            
        return layout

    def update(self) -> None:
        """Update logic for moving obstacles (spinners, etc)."""
        # Physics engine handles rotation, but we can enforce constant velocity here if needed
        for body in self.moving_bodies:
            # Keep spinners spinning despite friction
            if hasattr(body, "angular_velocity_target"):
                body.angular_velocity = body.angular_velocity_target

    def draw(self, screen: pygame.Surface) -> None:
        """Draw obstacles."""
        for shape in self.obstacles:
            color = (80, 80, 90) # Dark concrete color
            if hasattr(shape, "color"):
                color = shape.color

            if isinstance(shape, pymunk.Poly):
                # Convert physics coordinates to screen coordinates
                points = []
                for v in shape.get_vertices():
                    p = shape.body.local_to_world(v)
                    points.append((int(p.x), int(p.y)))
                pygame.draw.polygon(screen, color, points)
                pygame.draw.polygon(screen, (200, 200, 200), points, 2) # Highlight edge
            
            elif isinstance(shape, pymunk.Circle):
                pos = shape.body.position
                p = (int(pos.x), int(pos.y))
                r = int(shape.radius)
                pygame.draw.circle(screen, color, p, r)
                pygame.draw.circle(screen, (200, 200, 200), p, r, 2)

    def clear(self) -> None:
        """Remove all obstacles from space."""
        for shape in self.obstacles:
            self.space.remove(shape, shape.body)
        self.obstacles.clear()
        self.moving_bodies.clear()

    # --- Layout Algorithms ---

    def _create_box(self, x: float, y: float, w: float, h: float, angle: float = 0.0, dynamic: bool = False) -> pymunk.Body:
        """Helper to create a box obstacle."""
        mass = 1000 if dynamic else 0
        moment = pymunk.moment_for_box(mass, (w, h)) if dynamic else float('inf')
        body_type = pymunk.Body.KINEMATIC if dynamic else pymunk.Body.STATIC
        
        body = pymunk.Body(mass, moment, body_type)
        body.position = (x, y)
        body.angle = angle
        
        shape = pymunk.Poly.create_box(body, (w, h))
        shape.elasticity = 0.8
        shape.friction = 0.5
        shape.collision_type = 3 # Wall type (so marbles bounce)
        
        self.space.add(body, shape)
        self.obstacles.append(shape)
        return body

    def _create_circle(self, x: float, y: float, r: float) -> None:
        """Helper to create a static circle peg."""
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = (x, y)
        
        shape = pymunk.Circle(body, r)
        shape.elasticity = 0.8
        shape.friction = 0.5
        shape.collision_type = 3
        
        self.space.add(body, shape)
        self.obstacles.append(shape)

    def _create_columns(self) -> None:
        """Random pillars."""
        for _ in range(random.randint(4, 8)):
            x = random.randint(100, config.WIDTH - 100)
            y = random.randint(100, config.HEIGHT - 100)
            w = random.randint(50, 150)
            h = random.randint(50, 150)
            self._create_box(x, y, w, h)

    def _create_central_block(self) -> None:
        """A massive block in the middle forcing flank play."""
        cx, cy = config.WIDTH // 2, config.HEIGHT // 2
        size = 300
        self._create_box(cx, cy, size, size, angle=math.pi/4) # Diamond shape

    def _create_x_cross(self) -> None:
        """An X shape dividing the map."""
        cx, cy = config.WIDTH // 2, config.HEIGHT // 2
        length = 800
        thickness = 40
        self._create_box(cx, cy, length, thickness, angle=math.pi/4)
        self._create_box(cx, cy, length, thickness, angle=-math.pi/4)

    def _create_pegs(self) -> None:
        """Pachinko style grid."""
        cols = 5
        rows = 8
        spacing_x = config.WIDTH // (cols + 1)
        spacing_y = config.HEIGHT // (rows + 1)
        
        for i in range(cols):
            for j in range(rows):
                if (i + j) % 2 == 0: # Checker pattern
                    x = spacing_x * (i + 1)
                    y = spacing_y * (j + 1)
                    self._create_circle(x, y, 20)

    def _create_spinners(self) -> None:
        """Rotating bars of death."""
        cx, cy = config.WIDTH // 2, config.HEIGHT // 2
        
        # Top Spinner
        b1 = self._create_box(cx, cy - 300, 400, 30, dynamic=True)
        b1.angular_velocity_target = 2.0
        self.moving_bodies.append(b1)
        
        # Bottom Spinner
        b2 = self._create_box(cx, cy + 300, 400, 30, dynamic=True)
        b2.angular_velocity_target = -2.0
        self.moving_bodies.append(b2)

    def _create_funnel(self) -> None:
        """V shape."""
        cx, cy = config.WIDTH // 2, config.HEIGHT // 2
        
        # Left slant
        self._create_box(cx - 200, cy, 500, 30, angle=math.pi/3)
        # Right slant
        self._create_box(cx + 200, cy, 500, 30, angle=-math.pi/3)
