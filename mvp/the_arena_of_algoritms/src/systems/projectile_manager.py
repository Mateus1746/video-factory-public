import pygame
import math
import random
from ..effects import spawn_particles
from ..audio import generate_note_sound

class ProjectileManager:
    def __init__(self):
        self.projectiles = []

    def add_projectile(self, pos, target, speed, damage, color, collision_mode='destination'):
        """
        collision_mode: 
          'destination' - Hits only when reaching target coordinates (Artillery/Arc).
          'continuous'  - Hits anything in its path (Bullet/Line).
        """
        self.projectiles.append({
            'pos': list(pos),
            'target': list(target),
            'speed': speed,
            'damage': damage,
            'color': color,
            'mode': collision_mode,
            'active': True
        })

    def update(self, dt, rings):
        for p in self.projectiles:
            if not p['active']: continue
            
            # Movement
            dx = p['target'][0] - p['pos'][0]
            dy = p['target'][1] - p['pos'][1]
            dist_to_target = math.hypot(dx, dy)
            
            move_dist = p['speed'] * dt
            
            # Logic based on Mode
            hit = False
            
            if p['mode'] == 'continuous':
                # Move first
                if dist_to_target > 0:
                    step = min(move_dist, dist_to_target)
                    p['pos'][0] += (dx / dist_to_target) * step
                    p['pos'][1] += (dy / dist_to_target) * step
                
                # Check collision with ANY ring
                for ring in rings:
                    if ring.alive:
                        d_ring = math.hypot(p['pos'][0] - ring.center[0], p['pos'][1] - ring.center[1])
                        # Hitbox check (Projectile vs Ring border)
                        if abs(d_ring - ring.radius) < 20:
                            self._apply_hit(p, ring)
                            hit = True
                            p['active'] = False # Bullet destroys on impact
                            break
                            
                if not hit and dist_to_target < 5:
                    p['active'] = False # Reached center without hitting anything

            elif p['mode'] == 'destination':
                if dist_to_target < 20:
                    # Reached target -> Explode AOE
                    # Apply damage to rings near impact
                    spawn_particles(p['pos'][0], p['pos'][1], p['color'], 15)
                    for ring in rings:
                        if ring.alive:
                            d_ring = math.hypot(p['pos'][0] - ring.center[0], p['pos'][1] - ring.center[1])
                            if abs(d_ring - ring.radius) < 80:
                                self._apply_hit(p, ring)
                    p['active'] = False
                else:
                    # Move
                    p['pos'][0] += (dx / dist_to_target) * move_dist
                    p['pos'][1] += (dy / dist_to_target) * move_dist
                
        self.projectiles = [p for p in self.projectiles if p['active']]

    def _apply_hit(self, p, ring):
        ring.take_damage(p['damage'])
        if random.random() < 0.3 and ring.note_frequency:
            generate_note_sound(ring.note_frequency, 0.2).play()
        if p['mode'] == 'continuous':
             spawn_particles(p['pos'][0], p['pos'][1], p['color'], 5)

    def draw(self, surface):
        for p in self.projectiles:
             pygame.draw.circle(surface, p['color'], (int(p['pos'][0]), int(p['pos'][1])), 6)
