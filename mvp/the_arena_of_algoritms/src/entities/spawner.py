import pygame
import math
import random
from .base import Entity
from ..config import BALL_SPEED, GRAVITY, FRICTION, BALL_RADIUS, RING_THICKNESS, WALL_BOUNCE, BALL_DAMAGE, BALL_SPAWN_COOLDOWN, WHITE, MAX_BALLS, PINK
from ..audio import generate_note_sound
from ..effects import TrailEffect, spawn_particles

class Ball:
    def __init__(self, center, color=None, speed_mult=1.0):
        self.x = float(center[0])
        self.y = float(center[1])
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(BALL_SPEED * 0.5, BALL_SPEED * 1.5) * speed_mult
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.active = True
        self.spawn_cooldown = 0.0
        self.trail = TrailEffect(10)
        if color:
            self.color = color
        else:
            self.color = (random.randint(150, 255), random.randint(50, 150), random.randint(200, 255))
        
    def update(self, dt, rings, center):
        # Sub-stepping for physics stability
        steps = 3
        dt_step = dt / steps
        collided_any_step = False
        
        for _ in range(steps):
            if self._physics_step(dt_step, rings, center):
                collided_any_step = True
                
        self.trail.add((int(self.x), int(self.y)))
        
        if self.spawn_cooldown > 0:
            self.spawn_cooldown -= dt
            
        return collided_any_step

    def _physics_step(self, dt, rings, center):
        self.vy += GRAVITY * dt
        self.vx *= FRICTION
        self.vy *= FRICTION
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        collided = False
        dx = self.x - center[0]
        dy = self.y - center[1]
        dist = math.hypot(dx, dy)
        
        target_ring = None
        for ring in rings:
            if ring.alive:
                target_ring = ring
                break
                
        if target_ring:
            effective_radius = target_ring.radius - (RING_THICKNESS / 2)
            if dist + BALL_RADIUS >= effective_radius:
                if dist == 0: dist = 1
                nx, ny = dx / dist, dy / dist
                dot = self.vx * nx + self.vy * ny
                
                if dot > 0:
                    self.vx -= 2 * dot * nx
                    self.vy -= 2 * dot * ny
                    self.vx *= WALL_BOUNCE
                    self.vy *= WALL_BOUNCE
                    
                    # Random jitter to prevent perfect loops (algorithmic entropy)
                    jitter = random.uniform(-0.1, 0.1)
                    self.vx += jitter * self.vy
                    self.vy -= jitter * self.vx

                # Constraint
                overlap = (dist + BALL_RADIUS) - effective_radius
                if overlap > 0:
                    self.x -= nx * (overlap + 0.1)
                    self.y -= ny * (overlap + 0.1)
                
                if self.spawn_cooldown <= 0:
                    target_ring.take_damage(BALL_DAMAGE)
                    if target_ring.note_frequency:
                        generate_note_sound(target_ring.note_frequency, 0.05).play()
                    
                    spawn_particles(self.x + nx*BALL_RADIUS, self.y + ny*BALL_RADIUS, self.color, 2)
                    collided = True
                    self.spawn_cooldown = BALL_SPAWN_COOLDOWN

        return collided
                
    def draw(self, surface):
        pos = (int(self.x), int(self.y))
        self.trail.draw(surface, self.color, radius=BALL_RADIUS*0.8)
        pygame.draw.circle(surface, self.color, pos, BALL_RADIUS)

class Spawner(Entity):
    """
    Swarm Spawner implements Population Growth.
    The population grows exponentially upon collision with environment boundaries,
    simulating a self-replicating algorithm.
    """
    NAME = "SWARM SPAWNER"
    COLOR = PINK

    def __init__(self, center, rings, projectile_manager=None):
        super().__init__(center, rings, projectile_manager)
        self.balls = [Ball(self.center)]
        self.generation = 0
        
    def update(self, dt):
        new_balls = []
        for ball in self.balls:
            if ball.update(dt, self.rings, self.center):
                # Chance to replicate
                if len(self.balls) + len(new_balls) < MAX_BALLS:
                    # New ball inherits color but with a mutation
                    new_color = list(ball.color)
                    new_color[random.randint(0, 2)] = max(0, min(255, new_color[random.randint(0, 2)] + random.randint(-20, 20)))
                    new_balls.append(Ball(self.center, color=tuple(new_color)))
                    
        self.balls.extend(new_balls)
        
        # Periodic culling if over-populated (Malthusian limit)
        if len(self.balls) > MAX_BALLS * 0.9:
            # Remove 10% of the oldest balls
            num_to_remove = int(len(self.balls) * 0.1)
            self.balls = self.balls[num_to_remove:]
            
    def draw(self, surface):
        for ball in self.balls:
            ball.draw(surface)