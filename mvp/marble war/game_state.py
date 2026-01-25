"""
Game State for Marble War.
Manages entities, timers, and high-level logic.
"""

import math
import random
from typing import List, Set, Optional

import pymunk
import config
from entities import Marble, Projectile
from effects import PowerUp
import gamemodes

class GameState:
    def __init__(self, space, physics_engine, particles, floating_texts, explosions, kill_feed):
        self.space = space
        self.physics = physics_engine
        self.particles = particles
        self.floating_texts = floating_texts
        self.explosions = explosions
        self.kill_feed = kill_feed
        
        self.game_mode = gamemodes.get_random_mode()
        self.physics.game_mode = self.game_mode # Link for collisions
        
        self.marbles: List[Marble] = self.game_mode.setup_marbles(self.space)
        self.powerups: List[PowerUp] = []
        self.projectiles: List[Projectile] = []
        self.portals = gamemodes.generate_portals()
        
        self.frame_count = 0
        self.powerup_spawn_timer = 0.0
        
        self.bomb_active = False
        self.bomb_holder = None
        self.bomb_timer = 0.0
        self.last_tick = 0
        
        self.winner_team = None
        self.celebration_timer = 0
        
        # Zone
        self.zone_radius = math.hypot(config.WIDTH, config.HEIGHT) / 1.5
        self.zone_active = False
        
        # Shake
        self.shake_intensity = 0.0
        self.shake_offset = (0, 0)

    def update(self):
        self.frame_count += 1
        
        # Update Chaos
        self._update_chaos()
        self._update_shake()
        
        # Update Effects
        self.particles.update()
        self.floating_texts[:] = [ft for ft in self.floating_texts if ft.update()]
        self.explosions[:] = [exp for exp in self.explosions if exp.update()]
        
        self._handle_portals()

        # Update Marbles
        civilians = [m for m in self.marbles if m.team == "civilian"]
        zombies = [m for m in self.marbles if m.team == "zombie"]
        
        # ADRENALINE LOGIC: Fewer humans = Faster humans
        adrenaline = 1.0
        if 0 < len(civilians) <= 5:
            adrenaline = 2.0 # Last 5 are super fast
        elif 0 < len(civilians) <= 15:
            adrenaline = 1.5

        for m in self.marbles:
            # Trap logic
            trapped_t = getattr(m, 'trapped_timer', 0)
            if trapped_t > 0:
                m.trapped_timer -= config.TIMESTEP
                m.body.position = getattr(m, 'initial_pos', m.body.position)
                m.body.velocity = (0, 0)
                continue

            # NEW: Predator AI for Zombies
            if m.team == "zombie" and civilians:
                # Find nearest human
                target = min(civilians, key=lambda c: (m.body.position - c.body.position).length)
                hunt_dir = (target.body.position - m.body.position).normalized()
                # Apply pursuit force SCALED by speed_boost (0.25)
                m.body.apply_force_at_local_point(hunt_dir * 3000 * m.speed_boost)

            # MOD: Smarter Evasion AI for Civilians
            if m.team == "civilian":
                m.speed_boost = adrenaline
                
                # 1. SEPARATION FORCE (Avoid Ping-Pong with other humans)
                for other_civ in civilians:
                    if other_civ == m: continue
                    diff_civ = m.body.position - other_civ.body.position
                    dist_civ = diff_civ.length
                    if 0 < dist_civ < 120: # If too close to another human
                        # Gentle push away to maintain spacing
                        repel = diff_civ.normalized() * (3000 * (1.0 - dist_civ/120.0))
                        m.body.apply_force_at_local_point(repel)

                # 2. ZOMBIE EVASION
                if zombies:
                    # Filter active (non-trapped) zombies
                    active_zombies = [z for z in zombies if getattr(z, 'trapped_timer', 0) <= 0]
                    if active_zombies:
                        nearest_zombie = min(active_zombies, key=lambda z: (m.body.position - z.body.position).length)
                        diff = m.body.position - nearest_zombie.body.position
                        dist = diff.length
                        if dist < 500:
                            m.current_face = "assustado"
                            # Exponential escape force (the closer, the more panic)
                            escape_mag = 12000 * (1.0 - (dist / 500.0))
                            m.body.apply_force_at_local_point(diff.normalized() * (4000 + escape_mag))

            if m.apply_ai_force():
                self._fire_projectile(m)
                
            # Magnet logic
            if m.magnet_active:
                for other in self.marbles:
                    if other != m and other not in self.physics.to_remove:
                        dx = m.body.position.x - other.body.position.x
                        dy = m.body.position.y - other.body.position.y
                        dist_sq = dx*dx + dy*dy
                        if 0 < dist_sq < 400*400:
                            dist = math.sqrt(dist_sq)
                            force = 60000 / (dist + 1)
                            angle = math.atan2(dy, dx)
                            other.body.apply_force_at_local_point((math.cos(angle)*force, math.sin(angle)*force))

        # Increase power-up spawn rate slightly for more chaos
        self.powerup_spawn_timer += config.TIMESTEP * 1.2 
        self._handle_powerups()
        
        self._update_bomb()
        self._remove_dead()
        
        # Check Win
        if not self.winner_team:
            w = self.game_mode.check_victory(self.marbles, self.frame_count)
            if w:
                self.winner_team = w
                self.celebration_timer = 120 # 2 seconds of glory

    def _handle_portals(self):
        """Handle teleportation logic."""
        for m in self.marbles:
            if getattr(m, 'portal_cooldown', 0) > 0:
                m.portal_cooldown -= config.TIMESTEP
                continue

            for p in self.portals:
                dist = (m.body.position - pymunk.Vec2d(*p.entry)).length
                if dist < p.radius:
                    # Teleport!
                    m.body.position = p.exit
                    m.portal_cooldown = 1.0 # 1s cooldown
                    self.physics.audio.play_sound("powerup", 0.5, pos=m.body.position)
                    self.particles.emit(p.entry, (255, 255, 255))
                    self.particles.emit(p.exit, (255, 255, 255))
                    break

    def _fire_projectile(self, shooter):
        # Find target
        target = None
        min_dist = float('inf')
        for m in self.marbles:
            if m.team != shooter.team and m not in self.physics.to_remove:
                d = (m.body.position - shooter.body.position).length_squared
                if d < min_dist:
                    min_dist = d
                    target = m
        
        angle = random.uniform(0, 6.28)
        if target:
            diff = target.body.position - shooter.body.position
            angle = math.atan2(diff.y, diff.x)
            
        p = Projectile(shooter.body.position.x, shooter.body.position.y, angle, shooter.team, shooter.color, self.space)
        self.projectiles.append(p)

    def _handle_powerups(self):
        self.powerup_spawn_timer += config.TIMESTEP
        if self.powerup_spawn_timer >= config.POWERUP_SPAWN_INTERVAL:
            self.powerup_spawn_timer = 0
            x = random.randint(50, config.WIDTH-50)
            y = random.randint(50, config.HEIGHT-50)
            t = random.choice(config.POWERUP_TYPES)
            self.powerups.append(PowerUp(x, y, t))
            
        for p in self.powerups[:]:
            for m in self.marbles:
                if (m.body.position - p.position).length < config.MARBLE_RADIUS + p.radius:
                    self._activate_powerup(m, p.type)
                    self.powerups.remove(p)
                    self.physics.audio.play_sound("powerup")
                    break

    def _activate_powerup(self, m, t):
        m.powerup_timer = config.POWERUP_DURATION
        if t == "speed": m.speed_boost = config.SPEED_MULTIPLIER
        elif t == "size": m.brush_multiplier = config.BRUSH_MULTIPLIER
        elif t == "clone":
            clone = Marble(m.body.position.x, m.body.position.y, m.team, m.color, self.space)
            self.marbles.append(clone)
        elif t == "assassin": m.assassin_mode = True; m.ammo = config.ASSASSIN_SHOTS
        elif t == "magnet": m.magnet_active = True
        elif t == "freeze": m.freeze_active = True

    def _update_bomb(self):
        # Sync with Physics engine state if needed
        self.physics.bomb_active = self.bomb_active
        self.physics.bomb_holder = self.bomb_holder
        
        if self.frame_count >= config.BOMB_START_FRAME and not self.bomb_active and self.marbles:
            self.bomb_active = True
            self.bomb_holder = random.choice(self.marbles)
            self.bomb_timer = config.BOMB_DURATION
            self.last_tick = int(self.bomb_timer)
            
        if self.bomb_active:
            self.bomb_timer -= config.TIMESTEP
            curr = int(self.bomb_timer)
            if curr != self.last_tick:
                self.physics.audio.play_sound("tictoc")
                self.last_tick = curr
            
            if self.bomb_timer <= 0:
                if self.bomb_holder in self.marbles:
                    self.physics._trigger_elimination(self.bomb_holder)
                
                valid = [m for m in self.marbles if m != self.bomb_holder and m not in self.physics.to_remove]
                if valid:
                    self.bomb_holder = random.choice(valid)
                    self.bomb_timer = config.BOMB_DURATION
                    self.last_tick = int(self.bomb_timer)
                else:
                    self.bomb_active = False

    def _update_chaos(self):
        if self.frame_count > config.CHAOS_START_FRAME:
            self.zone_active = True
            
        if self.zone_active:
            sudden_death = self.frame_count > 60 * config.FPS
            speed = config.ZONE_SHRINK_SPEED * (5.0 if sudden_death else 1.0)
            limit = 0 if sudden_death else config.ZONE_MIN_RADIUS
            
            if self.zone_radius > limit:
                self.zone_radius -= speed
                
            cx, cy = config.WIDTH/2, config.HEIGHT/2
            for m in self.marbles:
                dx = m.body.position.x - cx
                dy = m.body.position.y - cy
                dist_sq = dx*dx + dy*dy
                if dist_sq > self.zone_radius**2:
                    if sudden_death:
                        self.physics._trigger_elimination(m)
                        continue
                    
                    dist = math.sqrt(dist_sq)
                    if dist == 0: continue
                    
                    nx, ny = dx/dist, dy/dist
                    overlap = dist - self.zone_radius
                    m.body.position = (m.body.position.x - nx*overlap, m.body.position.y - ny*overlap)
                    
                    vx, vy = m.body.velocity
                    if vx*nx + vy*ny > 0:
                        bounce = config.ZONE_BOUNCE_FACTOR
                        dot = vx*nx + vy*ny
                        m.body.velocity = (vx - (1+bounce)*dot*nx, vy - (1+bounce)*dot*ny)
                        m.body.apply_impulse_at_local_point((random.uniform(-100,100), random.uniform(-100,100)))

    def _update_shake(self):
        if self.physics.shake_intensity > 0: # Access from physics triggers
            self.shake_intensity = self.physics.shake_intensity
            self.physics.shake_intensity *= 0.9 # Decay in physics
            
            self.shake_offset = (random.uniform(-self.shake_intensity, self.shake_intensity), 
                                 random.uniform(-self.shake_intensity, self.shake_intensity))
            if self.shake_intensity < 0.5:
                self.shake_intensity = 0
                self.shake_offset = (0, 0)

    def _remove_dead(self):
        for p in self.physics.to_remove_projectiles:
            if p in self.projectiles:
                self.space.remove(p.shape, p.body)
                self.projectiles.remove(p)
        self.physics.to_remove_projectiles.clear()
        
        for m in self.physics.to_remove:
            if m in self.marbles:
                self.space.remove(m.shape, m.body)
                self.marbles.remove(m)
        self.physics.to_remove.clear()
