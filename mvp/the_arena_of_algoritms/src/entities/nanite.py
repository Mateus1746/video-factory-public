import pygame
import math
import random
from ..effects import spawn_particles
from ..audio import generate_note_sound

class NaniteCloud:
    """
    Nanite Cloud implements the Boids Algorithm for collective behavior:
    1. Separation: Avoid crowding neighbors
    2. Alignment: Steer towards average heading of neighbors
    3. Cohesion: Steer towards average position of neighbors
    """
    def __init__(self, center, rings):
        self.center = center
        self.rings = rings
        self.particles = []
        self.num_particles = 100
        self.color = (180, 180, 180) # Silver
        
        for _ in range(self.num_particles):
            self.particles.append({
                'pos': pygame.Vector2(center[0] + random.uniform(-50, 50), 
                                     center[1] + random.uniform(-50, 50)),
                'vel': pygame.Vector2(random.uniform(-2, 2), random.uniform(-2, 2)),
                'acc': pygame.Vector2(0, 0)
            })
            
        self.max_speed = 4.0
        self.max_force = 0.2
        self.perception = 50.0

    def update(self, dt):
        alive_rings = [r for r in self.rings if r.alive]
        if not alive_rings: return

        for p in self.particles:
            # Reset acceleration
            p['acc'] *= 0
            
            # 1. Boids Forces
            sep = self.separation(p)
            ali = self.alignment(p)
            coh = self.cohesion(p)
            
            # Weighting
            p['acc'] += sep * 1.5
            p['acc'] += ali * 1.0
            p['acc'] += coh * 1.0
            
            # 2. Target Force (Steer towards the smallest alive ring)
            target_ring = alive_rings[0]
            # Pick a target point on the ring
            angle = math.atan2(p['pos'].y - self.center[1], p['pos'].x - self.center[0])
            target_pos = pygame.Vector2(
                self.center[0] + math.cos(angle) * target_ring.radius,
                self.center[1] + math.sin(angle) * target_ring.radius
            )
            
            desired = target_pos - p['pos']
            if desired.length() > 0:
                desired = desired.normalize() * self.max_speed
                steer = desired - p['vel']
                if steer.length() > self.max_force:
                    steer = steer.normalize() * self.max_force
                p['acc'] += steer * 2.0 # Strong pull to ring

            # Physics update
            p['vel'] += p['acc']
            if p['vel'].length() > self.max_speed:
                p['vel'] = p['vel'].normalize() * self.max_speed
            
            p['pos'] += p['vel']
            
            # Damage
            dist = math.hypot(p['pos'].x - self.center[0], p['pos'].y - self.center[1])
            for ring in alive_rings:
                if abs(dist - ring.radius) < 10:
                    ring.take_damage(690 * dt) # Increased damage (+25%)
                    if ring.note_frequency and random.random() < 0.05:
                         generate_note_sound(ring.note_frequency, 0.05).play()
                    
                    if random.random() < 0.1:
                        spawn_particles(p['pos'].x, p['pos'].y, self.color, 1)

    def separation(self, boid):
        steering = pygame.Vector2(0, 0)
        total = 0
        for other in self.particles:
            d = boid['pos'].distance_to(other['pos'])
            if other is not boid and d < self.perception / 2:
                diff = boid['pos'] - other['pos']
                diff /= (d * d + 0.1) # Weight by distance
                steering += diff
                total += 1
        if total > 0:
            steering /= total
            if steering.length() > 0:
                steering = steering.normalize() * self.max_speed
                steering -= boid['vel']
                if steering.length() > self.max_force:
                    steering = steering.normalize() * self.max_force
        return steering

    def alignment(self, boid):
        steering = pygame.Vector2(0, 0)
        total = 0
        for other in self.particles:
            d = boid['pos'].distance_to(other['pos'])
            if other is not boid and d < self.perception:
                steering += other['vel']
                total += 1
        if total > 0:
            steering /= total
            steering = steering.normalize() * self.max_speed
            steering -= boid['vel']
            if steering.length() > self.max_force:
                steering = steering.normalize() * self.max_force
        return steering

    def cohesion(self, boid):
        steering = pygame.Vector2(0, 0)
        total = 0
        for other in self.particles:
            d = boid['pos'].distance_to(other['pos'])
            if other is not boid and d < self.perception:
                steering += other['pos']
                total += 1
        if total > 0:
            steering /= total
            steering -= boid['pos']
            if steering.length() > 0:
                steering = steering.normalize() * self.max_speed
                steering -= boid['vel']
                if steering.length() > self.max_force:
                    steering = steering.normalize() * self.max_force
        return steering

    def draw(self, surface):
        for p in self.particles:
            pygame.draw.circle(surface, self.color, (int(p['pos'].x), int(p['pos'].y)), 2)