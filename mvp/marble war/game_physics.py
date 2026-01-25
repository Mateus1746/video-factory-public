"""
Physics Engine for Marble War.
Handles Pymunk space, collisions, and movement.
"""

import math
import random
from typing import List, Set, Optional

import pymunk

import config
from entities import Marble, Projectile
from effects import ParticleSystem, Explosion, FloatingText, PowerUp

class PhysicsEngine:
    def __init__(self, space: pymunk.Space, audio_manager, particles: ParticleSystem, floating_texts: List[FloatingText], explosions: List[Explosion], assets, kill_feed: List[str]):
        self.space = space
        self.audio = audio_manager
        self.particles = particles
        self.floating_texts = floating_texts
        self.explosions = explosions
        self.assets = assets # Reference for explosion images
        self.kill_feed = kill_feed
        
        # State references (will be updated by GameState)
        self.game_mode = None
        self.bomb_active = False
        self.bomb_holder = None
        self.to_remove: Set[Marble] = set()
        self.to_remove_projectiles: Set[Projectile] = set()
        
        # Chaos State
        self.shake_intensity = 0.0
        
        self._create_walls()
        self._setup_collision_handlers()

    def _create_walls(self) -> None:
        """Create boundary walls."""
        w, h = config.WIDTH, config.HEIGHT
        t = config.WALL_THICKNESS
        
        walls = [
            [(-t, -t), (w + t, -t)],              # Top
            [(w + t, -t), (w + t, h + t)],        # Right
            [(w + t, h + t), (-t, h + t)],        # Bottom
            [(-t, h + t), (-t, -t)]               # Left
        ]
        
        for start, end in walls:
            seg = pymunk.Segment(self.space.static_body, start, end, t)
            seg.elasticity = config.WALL_ELASTICITY
            seg.friction = config.WALL_FRICTION
            seg.collision_type = config.COLLISION_WALL
            self.space.add(seg)

    def _setup_collision_handlers(self) -> None:
        """Setup physics collision callbacks."""
        # Marble vs Marble
        self.space.on_collision(
            config.COLLISION_MARBLE, 
            config.COLLISION_MARBLE, 
            post_solve=self._handle_marble_marble_collision,
            pre_solve=self._pre_solve_marble_collision # Pass as kwarg
        )
        
        # Marble vs Wall
        self.space.on_collision(
            config.COLLISION_MARBLE, 
            config.COLLISION_WALL, 
            post_solve=self._handle_marble_wall_collision
        )
        
        # Projectile vs Marble
        self.space.on_collision(
            config.COLLISION_PROJECTILE, 
            config.COLLISION_MARBLE, 
            begin=self._handle_projectile_marble_collision
        )

    def _pre_solve_marble_collision(self, arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict) -> bool:
        """Dynamically adjust physics during collision."""
        m1: Marble = arbiter.shapes[0].data
        m2: Marble = arbiter.shapes[1].data
        
        # DAMPING: If two humans collide, reduce bounce to stop ping-pong
        if m1.team == "civilian" and m2.team == "civilian":
            arbiter.elasticity = 0.2 # Very low bounce
        else:
            arbiter.elasticity = 0.9 # Normal bounce
            
        return True

    def _handle_marble_marble_collision(self, arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict) -> None:
        m1: Marble = arbiter.shapes[0].data
        m2: Marble = arbiter.shapes[1].data
        
        impulse = arbiter.total_impulse.length
        if impulse > config.IMPULSE_THRESHOLD:
            vol = min(1.0, impulse / config.IMPULSE_TO_VOLUME)
            pos = arbiter.contact_point_set.points[0].point_a
            self.audio.play_sound("collision", vol, pos=pos)
            self.particles.emit(pos, m1.color)
            self.particles.emit(pos, m2.color)
            
        # 2. FREEZE LOGIC (Chaos Pack)
        # Infection-style freeze, but respecting immunity
        if m1.freeze_active and not m2.freeze_active and m1.team != m2.team:
            if getattr(m2, 'freeze_immunity_timer', 0) <= 0:
                m2.freeze_active = True; m2.powerup_timer = config.POWERUP_DURATION
        elif m2.freeze_active and not m1.freeze_active and m1.team != m2.team:
            if getattr(m1, 'freeze_immunity_timer', 0) <= 0:
                m1.freeze_active = True; m1.powerup_timer = config.POWERUP_DURATION
            
        # Game Mode Logic
        if self.game_mode:
            sound, msg = self.game_mode.handle_collision(m1, m2)
            if msg:
                self.floating_texts.append(FloatingText(m1.body.position.x, m1.body.position.y - 40, msg, (0, 255, 0)))

        # Bomb Logic
        if self.bomb_active and self.bomb_holder:
            new_holder = None
            if m1 == self.bomb_holder: new_holder = m2
            elif m2 == self.bomb_holder: new_holder = m1
            
            if new_holder:
                self.bomb_holder = new_holder
                self.audio.play_sound("powerup", 0.3, pos=new_holder.body.position)
                self.floating_texts.append(FloatingText(new_holder.body.position.x, new_holder.body.position.y - 40, "HOT POTATO!", (255, 50, 50)))

        # Face Trigger
        if not m1.freeze_active: m1.face_timer = 1.0; m1.current_face = "bravo"
        if not m2.freeze_active: m2.face_timer = 1.0; m2.current_face = "bravo"

    def _handle_marble_wall_collision(self, arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict) -> None:
        impulse = arbiter.total_impulse.length
        if impulse > config.IMPULSE_THRESHOLD:
            vol = min(0.6, impulse / config.IMPULSE_TO_VOLUME)
            pos = arbiter.contact_point_set.points[0].point_a
            self.audio.play_sound("collision", vol, pos=pos)
            marble: Marble = arbiter.shapes[0].data
            self.particles.emit(pos, marble.color)
            
            if not marble.freeze_active:
                marble.face_timer = 1.0
                marble.current_face = "bravo"

    def _handle_projectile_marble_collision(self, arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict) -> bool:
        projectile: Projectile = arbiter.shapes[0].data
        marble: Marble = arbiter.shapes[1].data
        
        # Friendly Fire OFF.
        if projectile.team != marble.team:
            # NEW: Zombies are immune to damage (they are already dead!)
            if marble.team == "zombie":
                # Projectile just vanishes on hit
                self.to_remove_projectiles.add(projectile)
                return False

            self._trigger_elimination(marble, projectile)
            return False
        return True

    def _trigger_elimination(self, marble: Marble, killer: Optional[Projectile] = None):
        if marble in self.to_remove: return

        if marble.hp > 1:
            marble.hp -= 1
            self.audio.play_sound("collision", 0.5, pos=marble.body.position)
            marble.current_face = "assustado"
            marble.face_timer = 0.5
            self.particles.emit(marble.body.position, marble.color)
            return

        self.to_remove.add(marble)
        if killer: self.to_remove_projectiles.add(killer)
        
        self.audio.play_sound("elimination", 0.8, pos=marble.body.position)
        self.particles.emit(marble.body.position, marble.color)
        
        # Shake screen
        self.shake_intensity = 15.0 if marble.max_hp > 10 else 10.0
        
        if marble.max_hp > 10:
            self.floating_texts.append(FloatingText(marble.body.position.x, marble.body.position.y - 100, "BOSS DEFEATED!", (255, 50, 50), size=80))
        else:
            self.floating_texts.append(FloatingText(marble.body.position.x, marble.body.position.y - 50, "ELIMINATED", (255, 255, 255)))
            
        # Kill Feed Entry
        killer_team = killer.team.upper() if killer else "THE ZONE"
        self.kill_feed.append(f"{killer_team} -> {marble.team.upper()}")
        if len(self.kill_feed) > 5:
            self.kill_feed.pop(0)

        # Add Explosion effect
        if self.assets.explosion_img:
            # Use dead face if available, otherwise explosion
            face = self.assets.face_assets.get("morto", self.assets.explosion_img)
            self.explosions.append(Explosion(marble.body.position.x, marble.body.position.y, face))
