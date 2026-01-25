import pygame
import math
import random
from .base import Entity
from ..config import WHITE
from ..audio import generate_note_sound
from ..effects import spawn_particles

class QuantumSwarm(Entity):
    """
    Quantum Swarm uses the concept of Superposition.
    Drones exist in multiple potential states (ghosts) and 
    'collapse' their wave function upon collision/attack.
    """
    NAME = "QUANTUM SWARM"
    COLOR = (180, 0, 255)

    def __init__(self, center, rings, projectile_manager=None):
        super().__init__(center, rings, projectile_manager)
        self.drones = []
        self.num_drones = 6 # Increased from 4
        self.color = self.COLOR # Purple
        
        for _ in range(self.num_drones):
            self.drones.append({
                'pos': pygame.Vector2(center),
                'ghosts': [pygame.Vector2(center) for _ in range(5)],
                'probability_cloud': 1.0,
                'target_ring': None,
                'state': 'SUPERPOSITION' # SUPERPOSITION or COLLAPSED
            })
            
    def update(self, dt):
        alive_rings = [r for r in self.rings if r.alive]
        if not alive_rings: return

        for drone in self.drones:
            if drone['state'] == 'SUPERPOSITION':
                # Move ghosts randomly around the center/rings
                for i, ghost in enumerate(drone['ghosts']):
                    angle = random.uniform(0, 2 * math.pi)
                    dist = random.uniform(50, 350)
                    target = pygame.Vector2(
                        self.center[0] + math.cos(angle) * dist,
                        self.center[1] + math.sin(angle) * dist
                    )
                    # Lerp ghost to target
                    drone['ghosts'][i] += (target - ghost) * 0.1
                
                # Chance to collapse onto a ring
                if random.random() < 0.02:
                    drone['state'] = 'COLLAPSED'
                    drone['target_ring'] = random.choice(alive_rings)
                    # Collapse to a random ghost's position that is near the ring
                    drone['pos'] = pygame.Vector2(random.choice(drone['ghosts']))
                    spawn_particles(drone['pos'].x, drone['pos'].y, self.color, 15)

            elif drone['state'] == 'COLLAPSED':
                # Deal massive "uncertainty" damage
                if drone['target_ring'].alive:
                    damage = 28000 * dt # Adjusted for 45s target
                    drone['target_ring'].take_damage(damage)
                    
                    # Beam effect
                    angle = math.atan2(drone['pos'].y - self.center[1], drone['pos'].x - self.center[0])
                    ring_point = pygame.Vector2(
                        self.center[0] + math.cos(angle) * drone['target_ring'].radius,
                        self.center[1] + math.sin(angle) * drone['target_ring'].radius
                    )
                    drone['pos'] += (ring_point - drone['pos']) * 0.2
                
                # Decay collapse
                drone['probability_cloud'] -= dt * 2
                if drone['probability_cloud'] <= 0:
                    drone['state'] = 'SUPERPOSITION'
                    drone['probability_cloud'] = 1.0
                    drone['pos'] = pygame.Vector2(self.center)

    def draw(self, surface):
        for drone in self.drones:
            if drone['state'] == 'SUPERPOSITION':
                for ghost in drone['ghosts']:
                    pygame.draw.circle(surface, (100, 0, 150), (int(ghost.x), int(ghost.y)), 4, 1)
            else:
                # Collapsed state is bright and solid
                alpha_color = (255, 255, 255)
                pygame.draw.circle(surface, self.color, (int(drone['pos'].x), int(drone['pos'].y)), 8)
                pygame.draw.circle(surface, WHITE, (int(drone['pos'].x), int(drone['pos'].y)), 4)
                
                if drone['target_ring'] and drone['target_ring'].alive:
                    pygame.draw.line(surface, self.color, (int(drone['pos'].x), int(drone['pos'].y)), self.center, 1)