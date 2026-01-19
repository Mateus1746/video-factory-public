import pygame
import math
import random
from ..audio import generate_note_sound
from ..effects import spawn_particles

class VolcanoEruption:
    """
    Volcano Eruption simulates Ejecta Dynamics.
    Particles follow parabolic trajectories with initial velocities 
    sampled from a specific distribution.
    """
    def __init__(self, center, rings):
        self.center = center
        self.rings = rings
        self.rocks = []
        self.timer = 0.0
        self.interval = 0.04
        self.color = (255, 120, 0) # Magma
        self.gravity = 500.0
        
    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.timer = self.interval
            # Erupt rock with a distribution favoring high vertical velocity
            angle = random.uniform(-math.pi/4, math.pi/4) - math.pi/2 # Upwards cone
            speed = random.uniform(400, 800)
            
            # Rotate cone based on time for "spinning" eruption
            t_rot = pygame.time.get_ticks() / 1000.0
            angle += math.sin(t_rot) * 0.5
            
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            self.rocks.append({
                'pos': [self.center[0], self.center[1]],
                'vel': [vx, vy],
                'life': 2.0
            })
            
        # Update rocks
        for rock in self.rocks:
            rock['life'] -= dt
            
            # Apply Gravity
            rock['vel'][1] += self.gravity * dt
            
            # Apply position update
            rock['pos'][0] += rock['vel'][0] * dt
            rock['pos'][1] += rock['vel'][1] * dt

            # Boundary Check (Top vs Bot)
            from ..config import HALF_HEIGHT
            if self.center[1] < HALF_HEIGHT: # Top Algo
                if rock['pos'][1] > HALF_HEIGHT:
                    rock['life'] = 0 # Die if crossing down
            else: # Bot Algo
                if rock['pos'][1] < HALF_HEIGHT:
                    rock['life'] = 0 # Die if crossing up
            
            # Collision with rings
            rx, ry = rock['pos']
            dist = math.hypot(rx - self.center[0], ry - self.center[1])
            
            if rock['life'] > 0:
                for ring in self.rings:
                    if ring.alive:
                        # Check if rock is passing through the ring radius
                        if abs(dist - ring.radius) < 15:
                            # Kinetic energy based damage
                            ke = 0.5 * (math.hypot(rock['vel'][0], rock['vel'][1])**2)
                            ring.take_damage(ke * 0.0225) # Increased multiplier (+25%)
                            
                            spawn_particles(rx, ry, self.color, 3)
                            # Partial energy loss on hit instead of immediate death
                            rock['vel'][0] *= 0.5
                            rock['vel'][1] *= 0.5
                            rock['life'] -= 0.5 
                            
                            if ring.note_frequency and random.random() < 0.1:
                                generate_note_sound(ring.note_frequency, 0.05).play()
                            break
        
        self.rocks = [r for r in self.rocks if r['life'] > 0 and r['pos'][1] < 2000]

    def draw(self, surface):
        for rock in self.rocks:
            # Size based on velocity or "heat"
            size = max(2, int(rock['life'] * 3))
            pygame.draw.circle(surface, self.color, (int(rock['pos'][0]), int(rock['pos'][1])), size)
            # Add a small glow to "hot" rocks
            if rock['life'] > 1.5:
                pygame.draw.circle(surface, (255, 255, 200), (int(rock['pos'][0]), int(rock['pos'][1])), size // 2)