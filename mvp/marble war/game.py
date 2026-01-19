"""
Main game logic for Marble War.
"""

import json
import math
import random
from pathlib import Path
from typing import List, Optional, Set

import pygame
import pymunk

import config
from assets import AssetManager
from effects import Explosion, ParticleSystem, PowerUp
from entities import Marble, Projectile
from game_types import AudioEvent



# ============================================================================
# MAIN GAME
# ============================================================================

class MarbleWar:
    """Main game controller."""
    
    # Physics constants
    WALL_THICKNESS = 100
    WALL_ELASTICITY = 1.0
    SPACE_DAMPING = 0.98
    
    # Collision types
    COLLISION_MARBLE = 1
    COLLISION_PROJECTILE = 2
    COLLISION_WALL = 3
    
    # Audio thresholds
    IMPULSE_THRESHOLD = 50
    IMPULSE_TO_VOLUME = 2000.0
    
    def __init__(self) -> None:
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        pygame.display.set_caption("Marble War - Modular")
        
        # Physics space
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)
        self.space.damping = self.SPACE_DAMPING
        
        # Grid system (pre-rendered surface)
        self.grid_size = config.GRID_SIZE
        self.cols = config.WIDTH // self.grid_size
        self.rows = config.HEIGHT // self.grid_size
        self.grid_surface = pygame.Surface((config.WIDTH, config.HEIGHT))
        self.grid_surface.fill((20, 20, 20))
        
        # Game state
        self.marbles: List[Marble] = []
        self.to_remove: Set[Marble] = set()
        self.powerups: List[PowerUp] = []
        self.projectiles: List[Projectile] = []
        self.to_remove_projectiles: Set[Projectile] = set()
        self.explosions: List[Explosion] = []
        
        # Timers
        self.powerup_spawn_timer: float = 0.0
        self.frame_count: int = 0
        
        # Bomb state
        self.bomb_active: bool = False
        self.bomb_holder: Optional[Marble] = None
        self.bomb_timer: float = 0.0
        self.last_tick_second: int = 0
        
        # Victory state
        self.celebration_timer: int = 0
        self.winner_team: Optional[str] = None
        
        # Effects
        self.particles = ParticleSystem()
        
        # Audio logging
        self.audio_events: List[AudioEvent] = []
        
        # Assets
        self.assets = AssetManager()
        self.assets.load_all()
        
        # Initialize game objects
        self._create_walls()
        self._setup_collision_handlers()
        self._setup_marbles()
        
        # Frame output
        frames_dir = Path("frames")
        if frames_dir.exists():
            for file in frames_dir.glob("*.png"):
                file.unlink()
        frames_dir.mkdir(exist_ok=True)
    
    def _create_walls(self) -> None:
        """Create boundary walls."""
        w, h = config.WIDTH, config.HEIGHT
        t = self.WALL_THICKNESS
        
        walls = [
            [(-t, -t), (w + t, -t)],              # Top
            [(w + t, -t), (w + t, h + t)],        # Right
            [(w + t, h + t), (-t, h + t)],        # Bottom
            [(-t, h + t), (-t, -t)]               # Left
        ]
        
        for start, end in walls:
            seg = pymunk.Segment(self.space.static_body, start, end, t)
            seg.elasticity = self.WALL_ELASTICITY
            seg.friction = 0.2
            seg.collision_type = self.COLLISION_WALL
            self.space.add(seg)
    
    def _setup_collision_handlers(self) -> None:
        """Setup physics collision callbacks."""
        # Marble vs Marble
        self.space.on_collision(
            self.COLLISION_MARBLE, 
            self.COLLISION_MARBLE, 
            post_solve=self._handle_marble_marble_collision
        )
        
        # Marble vs Wall
        self.space.on_collision(
            self.COLLISION_MARBLE, 
            self.COLLISION_WALL, 
            post_solve=self._handle_marble_wall_collision
        )
        
        # Projectile vs Marble
        self.space.on_collision(
            self.COLLISION_PROJECTILE, 
            self.COLLISION_MARBLE, 
            begin=self._handle_projectile_marble_collision
        )
    
    def _handle_marble_marble_collision(self, arbiter: pymunk.Arbiter, 
                                       space: pymunk.Space, data: dict) -> bool:
        """Handle marble-to-marble collision."""
        m1: Marble = arbiter.shapes[0].data
        m2: Marble = arbiter.shapes[1].data
        
        # Sound based on impulse
        impulse = arbiter.total_impulse.length
        if impulse > self.IMPULSE_THRESHOLD:
            vol = min(1.0, impulse / self.IMPULSE_TO_VOLUME)
            self._play_sound("collision", vol)
            
            # Particle splash
            pos = arbiter.contact_point_set.points[0].point_a
            self.particles.emit(pos, m1.color)
            self.particles.emit(pos, m2.color)
        
        # Bomb passing logic
        if self.bomb_active and self.bomb_holder:
            if m1 == self.bomb_holder:
                self.bomb_holder = m2
                self._play_sound("powerup", 0.3)
            elif m2 == self.bomb_holder:
                self.bomb_holder = m1
                self._play_sound("powerup", 0.3)
        
        # Trigger face
        m1.face_timer = 1.0
        m1.current_face = "bravo"
        m2.face_timer = 1.0
        m2.current_face = "bravo"
        
        return True
    
    def _handle_marble_wall_collision(self, arbiter: pymunk.Arbiter, 
                                     space: pymunk.Space, data: dict) -> bool:
        """Handle marble-to-wall collision."""
        impulse = arbiter.total_impulse.length
        if impulse > self.IMPULSE_THRESHOLD:
            vol = min(0.6, impulse / self.IMPULSE_TO_VOLUME)
            self._play_sound("collision", vol)
            
            # Particle splash
            pos = arbiter.contact_point_set.points[0].point_a
            marble: Marble = arbiter.shapes[0].data
            self.particles.emit(pos, marble.color)
            
            # Trigger face
            marble.face_timer = 1.0
            marble.current_face = "bravo"
        
        return True
    
    def _handle_projectile_marble_collision(self, arbiter: pymunk.Arbiter, 
                                           space: pymunk.Space, data: dict) -> bool:
        """Handle projectile hitting marble."""
        projectile: Projectile = arbiter.shapes[0].data
        marble: Marble = arbiter.shapes[1].data
        
        # Only hit enemies
        if projectile.team != marble.team:
            self.to_remove.add(marble)
            self.to_remove_projectiles.add(projectile)
            self._play_sound("elimination", 0.8)
            
            self.particles.emit(marble.body.position, marble.color)
            
            # Show dead face briefly before removal
            if self.assets.explosion_img:
                self.explosions.append(
                    Explosion(marble.body.position.x, marble.body.position.y, 
                             self.assets.face_assets.get("morto", self.assets.explosion_img))
                )
            
            self.particles.emit(marble.body.position, marble.color)
            return False  # Consume collision
        
        return True
    
    def _setup_marbles(self) -> None:
        """Initialize starting marbles."""
        margin = 80
        positions = [
            (margin, margin, "red", (255, 50, 50)),
            (config.WIDTH - margin, margin, "blue", (50, 50, 255)),
            (margin, config.HEIGHT - margin, "yellow", (255, 255, 50)),
            (config.WIDTH - margin, config.HEIGHT - margin, "green", (50, 255, 50))
        ]
        
        for x, y, team, color in positions:
            self.marbles.append(Marble(x, y, team, color, self.space))
    
    def _play_sound(self, name: str, volume: float = 1.0) -> None:
        """Play sound and log for video compilation."""
        # Play in real-time
        if name in self.assets.sounds:
            sound = self.assets.sounds[name]
            sound.set_volume(volume)
            sound.play()
        
        # Log for post-processing
        self.audio_events.append(AudioEvent(
            t=self.frame_count * config.TIMESTEP,
            name=name,
            vol=volume
        ))
    
    def _update_grid(self) -> None:
        """Update territory grid (optimized bounding box)."""
        for marble in self.marbles:
            # Brush area
            r = config.MARBLE_RADIUS * marble.brush_multiplier
            
            # Grid bounds
            min_gx = max(0, int((marble.body.position.x - r) // self.grid_size))
            max_gx = min(self.cols - 1, int((marble.body.position.x + r) // self.grid_size))
            min_gy = max(0, int((marble.body.position.y - r) // self.grid_size))
            max_gy = min(self.rows - 1, int((marble.body.position.y + r) // self.grid_size))
            
            # Paint cells
            for nx in range(min_gx, max_gx + 1):
                for ny in range(min_gy, max_gy + 1):
                    rect = (nx * self.grid_size, ny * self.grid_size, 
                           self.grid_size, self.grid_size)
                    pygame.draw.rect(self.grid_surface, marble.color, rect)
                    pygame.draw.rect(self.grid_surface, (0, 0, 0), rect, 1)
    
    def _handle_powerups(self) -> None:
        """Spawn and collect power-ups."""
        # Spawn timer
        self.powerup_spawn_timer += config.TIMESTEP
        if self.powerup_spawn_timer >= config.POWERUP_SPAWN_INTERVAL:
            self.powerup_spawn_timer = 0
            px = random.randint(50, config.WIDTH - 50)
            py = random.randint(50, config.HEIGHT - 50)
            ptype = random.choice(config.POWERUP_TYPES)
            self.powerups.append(PowerUp(px, py, ptype))
        
        # Collection (guard clause to avoid nested logic)
        for powerup in self.powerups[:]:
            collected = False
            for marble in self.marbles:
                dist = math.hypot(
                    marble.body.position.x - powerup.position.x,
                    marble.body.position.y - powerup.position.y
                )
                if dist < config.MARBLE_RADIUS + powerup.radius:
                    self._activate_powerup(marble, powerup.type)
                    self.powerups.remove(powerup)
                    self._play_sound("powerup")
                    collected = True
                    break
            
            if collected:
                break
    
    def _activate_powerup(self, marble: Marble, ptype: str) -> None:
        """Activate power-up effect on marble."""
        marble.powerup_timer = config.POWERUP_DURATION
        
        # Thug life face on power-up grab
        if ptype in ["assassin", "speed"]:
            marble.face_timer = 2.0
            marble.current_face = "thug-life"
        else:
            marble.face_timer = 1.0
            marble.current_face = "bobo"

        if ptype == "speed":
            marble.speed_boost = config.SPEED_MULTIPLIER
        elif ptype == "size":
            marble.brush_multiplier = config.BRUSH_MULTIPLIER
        elif ptype == "clone":
            # Spawn clone
            new_marble = Marble(
                marble.body.position.x, 
                marble.body.position.y, 
                marble.team, 
                marble.color, 
                self.space
            )
            self.marbles.append(new_marble)
        elif ptype == "assassin":
            marble.assassin_mode = True
            marble.ammo = config.ASSASSIN_SHOTS
            marble.shoot_timer = 0
    
    def _update_marbles(self) -> None:
        """Update marble AI and handle shooting."""
        for marble in self.marbles:
            should_shoot = marble.apply_ai_force()
            
            if should_shoot:
                self._fire_projectile(marble)
    
    def _fire_projectile(self, marble: Marble) -> None:
        """Fire projectile from marble with smart targeting."""
        # Find closest enemy
        closest_enemy: Optional[Marble] = None
        min_dist_sq = float('inf')
        
        for enemy in self.marbles:
            if enemy.team != marble.team and enemy not in self.to_remove:
                dx = enemy.body.position.x - marble.body.position.x
                dy = enemy.body.position.y - marble.body.position.y
                dist_sq = dx * dx + dy * dy
                
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    closest_enemy = enemy
        
        # Calculate angle
        if closest_enemy:
            target_angle = math.atan2(
                closest_enemy.body.position.y - marble.body.position.y,
                closest_enemy.body.position.x - marble.body.position.x
            )
        else:
            # Fallback random direction
            target_angle = random.uniform(0, math.tau)
        
        # Create projectile
        proj = Projectile(
            marble.body.position.x, 
            marble.body.position.y, 
            target_angle, 
            marble.team, 
            marble.color, 
            self.space
        )
        self.projectiles.append(proj)
    
    def _update_projectiles(self) -> None:
        """Update and remove dead projectiles."""
        for proj in self.projectiles[:]:
            if not proj.update():
                self.to_remove_projectiles.add(proj)
    
    def _remove_entities(self) -> None:
        """Remove dead projectiles and marbles from physics space."""
        # Remove projectiles
        for proj in self.to_remove_projectiles:
            if proj in self.projectiles:
                self.space.remove(proj.shape, proj.body)
                self.projectiles.remove(proj)
        self.to_remove_projectiles.clear()
        
        # Remove marbles
        for marble in self.to_remove:
            if marble in self.marbles:
                self.space.remove(marble.shape, marble.body)
                self.marbles.remove(marble)
        self.to_remove.clear()
    
    def _update_bomb(self) -> None:
        """Handle bomb mechanics."""
        # Activate bomb after delay
        if self.frame_count >= config.BOMB_START_FRAME and not self.bomb_active:
            if self.marbles:
                self.bomb_active = True
                self.bomb_holder = random.choice(self.marbles)
                self.bomb_timer = config.BOMB_DURATION
                self.last_tick_second = int(self.bomb_timer)
        
        # Update bomb timer
        if self.bomb_active:
            self.bomb_timer -= config.TIMESTEP
            
            # Tick sound
            current_sec = int(self.bomb_timer)
            if current_sec != self.last_tick_second:
                self._play_sound("tictoc")
                self.last_tick_second = current_sec
            
            # Explosion
            if self.bomb_timer <= 0:
                if self.bomb_holder and self.bomb_holder in self.marbles:
                    self.to_remove.add(self.bomb_holder)
                    self._play_sound("elimination")
                    
                    if self.assets.explosion_img:
                        self.explosions.append(Explosion(
                            self.bomb_holder.body.position.x,
                            self.bomb_holder.body.position.y,
                            self.assets.face_assets.get("morto", self.assets.explosion_img)
                        ))
                
                # Reset bomb for next round
                active_marbles = [m for m in self.marbles if m != self.bomb_holder]
                if active_marbles:
                    self.bomb_holder = random.choice(active_marbles)
                    self.bomb_timer = config.BOMB_DURATION
                    self.last_tick_second = int(self.bomb_timer)
                else:
                    self.bomb_active = False
    
    def _check_victory(self) -> bool:
        """Check for victory condition. Returns True if game should end."""
        active_teams = list(set(m.team for m in self.marbles))
        
        # Victory condition
        if len(active_teams) <= 1 and self.frame_count > 100:
            if not self.winner_team:
                self.winner_team = active_teams[0] if active_teams else "None"
                self.celebration_timer = config.FPS * 2  # 2 seconds
                print(f"\n--- VICTORY ---")
                print(f"Team {self.winner_team.upper()} conquered the arena in {self.frame_count} frames!")
                print(f"---------------")
            
            if self.celebration_timer > 0:
                self.celebration_timer -= 1
                if self.celebration_timer <= 0:
                    return True
        
        return False
    
    def _draw(self) -> None:
        """Render all game elements."""
        # 1. Grid (pre-rendered)
        self.screen.blit(self.grid_surface, (0, 0))
        
        # 2. Power-ups
        for powerup in self.powerups:
            powerup.draw(self.screen, self.assets.powerup_images)
        
        # 3. Projectiles
        for proj in self.projectiles:
            proj.draw(self.screen, self.assets.projectile_img)
        
        # 4. Particles
        self.particles.draw(self.screen)
        
        # 5. Explosions
        for exp in self.explosions:
            exp.draw(self.screen)
        
        # 6. Marbles
        for marble in self.marbles:
            pos = (int(marble.body.position.x), int(marble.body.position.y))
            pygame.draw.circle(self.screen, marble.color, pos, config.MARBLE_RADIUS)
            
            # Assassin indicator
            if marble.assassin_mode:
                pygame.draw.circle(self.screen, (255, 255, 255), pos, 
                                 config.MARBLE_RADIUS + 5, 2)
            
            pygame.draw.circle(self.screen, (0, 0, 0), pos, config.MARBLE_RADIUS, 2)
            
            # 6.1 Draw face (Always)
            self._draw_marble_face(marble)
        
        # 7. Bomb indicator
        if self.bomb_active and self.bomb_holder:
            self._draw_bomb_indicator()
        
        # 8. UI (Timer)
        if self.bomb_active:
            self._draw_timer()
        
        # 9. Victory overlay
        if self.winner_team:
            self._draw_victory_screen()
    
    def _draw_bomb_indicator(self) -> None:
        """Draw bomb on holder."""
        if not self.bomb_holder:
            return
        
        b_pos = (int(self.bomb_holder.body.position.x), 
                int(self.bomb_holder.body.position.y))
        
        if self.assets.bomb_img:
            # Pulsing animation
            t = pygame.time.get_ticks() / 300.0
            scale = 1.0 + math.sin(t) * 0.15
            size = int(config.MARBLE_RADIUS * 2 * scale)
            scaled_bomb = pygame.transform.smoothscale(self.assets.bomb_img, (size, size))
            rect = scaled_bomb.get_rect(center=b_pos)
            self.screen.blit(scaled_bomb, rect)
        else:
            # Fallback pulsing ring
            t = pygame.time.get_ticks() / 200.0
            r_ind = config.MARBLE_RADIUS + 10 + math.sin(t) * 5
            pygame.draw.circle(self.screen, (255, 0, 0), b_pos, int(r_ind), 3)
    
    def _draw_timer(self) -> None:
        """Draw bomb timer UI."""
        font = pygame.font.SysFont("Arial", config.BOMB_TIMER_SIZE, bold=True)
        timer_text = f"{max(0, self.bomb_timer):.1f}s"
        
        # Shadow for contrast
        shadow = font.render(timer_text, True, (0, 0, 0))
        txt = font.render(timer_text, True, (255, 50, 50))
        self.screen.blit(shadow, (22, 22))
        self.screen.blit(txt, (20, 20))
    
    def _draw_marble_face(self, marble: Marble) -> None:
        """Draw the animated 'Sliding Face' and optional weapon."""
        FACE_OFFSET_LIMIT = 5
        
        # 1. Update emotion (if timer active, it overrides defaults)
        self._update_marble_emotion(marble)

        # 2. Determine look target and angle
        target_pos = self._get_best_look_target(marble)
        
        face_x = marble.body.position.x
        face_y = marble.body.position.y
        look_angle = 0.0 # Default look right
        
        if target_pos:
            dx = target_pos[0] - marble.body.position.x
            dy = target_pos[1] - marble.body.position.y
            look_angle = math.atan2(dy, dx)
            
            face_x += math.cos(look_angle) * FACE_OFFSET_LIMIT
            face_y += math.sin(look_angle) * FACE_OFFSET_LIMIT
            
        # 3. Render face
        face_img = self.assets.face_assets.get(marble.current_face)
        if face_img:
            face_rect = face_img.get_rect(center=(int(face_x), int(face_y)))
            self.screen.blit(face_img, face_rect)

        # 4. Render weapon if in Assassin Mode
        if marble.assassin_mode and self.assets.weapon_img:
            self._draw_marble_weapon(marble, look_angle)

    def _draw_marble_weapon(self, marble: Marble, angle: float) -> None:
        """Draw the gun pointing at target."""
        # Offset position (to the 'side' of the marble)
        gun_dist = config.MARBLE_RADIUS * 1.2
        # Offset angle so it looks like it's held on the right/left hip
        # We can alternate or pick one side
        side_offset = 0.6 # radians (~34 deg)
        
        gun_x = marble.body.position.x + math.cos(angle + side_offset) * gun_dist
        gun_y = marble.body.position.y + math.sin(angle + side_offset) * gun_dist
        
        # Rotate weapon to point at target
        # Pygame rotate is counter-clockwise and uses degrees
        # Also, original weapon asset usually points right (0 deg)
        rot_deg = -math.degrees(angle) 
        
        rotated_gun = pygame.transform.rotate(self.assets.weapon_img, rot_deg)
        
        # Flip vertically if pointing left to keep gun right-side up
        if math.cos(angle) < 0:
            rotated_gun = pygame.transform.flip(rotated_gun, False, True)
            
        gun_rect = rotated_gun.get_rect(center=(int(gun_x), int(gun_y)))
        self.screen.blit(rotated_gun, gun_rect)

    def _update_marble_emotion(self, marble: Marble) -> None:
        """Update the marble's current_face based on its surroundings."""
        # If timer is high, stick with existing special emotion
        if marble.face_timer > 0.5:
            return

        # Check for cobiça (near powerup)
        for p in self.powerups:
            dist = math.hypot(p.position.x - marble.body.position.x, 
                              p.position.y - marble.body.position.y)
            if dist < 150:
                marble.current_face = "bobo"
                return

        # Check for assustado (surrounded by enemies)
        enemy_count = 0
        for other in self.marbles:
            if other.team != marble.team:
                dist = math.hypot(other.body.position.x - marble.body.position.x, 
                                 other.body.position.y - marble.body.position.y)
                if dist < 100:
                    enemy_count += 1
        
        if enemy_count >= 2:
            marble.current_face = "assustado"
            return
            
        # Default: bravo
        marble.current_face = "bravo"


    def _get_best_look_target(self, marble: Marble) -> Optional[tuple]:
        """Behavior logic to find what the marble should look at."""
        # Priority 1: Power-up within 200px (Cobiça)
        for p in self.powerups:
            dist = math.hypot(p.position.x - marble.body.position.x, 
                              p.position.y - marble.body.position.y)
            if dist < 200:
                return (p.position.x, p.position.y)
        
        # Priority 2: Nearest Enemy (Agressividade)
        nearest_enemy = None
        min_dist = float('inf')
        for other in self.marbles:
            if other.team == marble.team:
                continue
            dist = math.hypot(other.body.position.x - marble.body.position.x, 
                             other.body.position.y - marble.body.position.y)
            if dist < min_dist:
                min_dist = dist
                nearest_enemy = other
        
        if nearest_enemy:
            return (nearest_enemy.body.position.x, nearest_enemy.body.position.y)
            
        # Priority 3: Nearest Ally (Medo/Buscando ajuda)
        nearest_ally = None
        min_dist = float('inf')
        for other in self.marbles:
            if other == marble or other.team != marble.team:
                continue
            dist = math.hypot(other.body.position.x - marble.body.position.x, 
                             other.body.position.y - marble.body.position.y)
            if dist < min_dist:
                min_dist = dist
                nearest_ally = other
                
        if nearest_ally:
            return (nearest_ally.body.position.x, nearest_ally.body.position.y)
            
        return None

    def _draw_victory_screen(self) -> None:
        """Draw victory overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Victory text
        font_big = pygame.font.SysFont("Arial", 80, bold=True)
        win_text = f"TEAM {self.winner_team.upper()}"
        sub_text = "CONQUERED THE ARENA!"
        
        # Team color (with fallback)
        team_color = config.TEAM_COLORS.get(f"team_{self.winner_team}", (255, 255, 255))
        
        # Render text
        txt_win = font_big.render(win_text, True, team_color)
        font_small = pygame.font.SysFont("Arial", 40, bold=True)
        txt_sub = font_small.render(sub_text, True, (255, 255, 255))
        
        # Center text
        cx, cy = config.WIDTH // 2, config.HEIGHT // 2
        self.screen.blit(txt_win, (cx - txt_win.get_width() // 2, cy - 60))
        self.screen.blit(txt_sub, (cx - txt_sub.get_width() // 2, cy + 30))
    
    def run(self) -> None:
        """Main game loop."""
        running = True
        
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Physics step
            self.space.step(config.TIMESTEP)
            
            # Update game state
            self._update_marbles()
            self._update_projectiles()
            self._handle_powerups()
            self._update_grid()
            self.particles.update()
            self.explosions = [e for e in self.explosions if e.update()]
            self._update_bomb()
            
            # Remove dead entities
            self._remove_entities()
            
            # Render
            self._draw()
            pygame.display.flip()
            
            # Save frame
            pygame.image.save(self.screen, f"frames/frame_{self.frame_count:04d}.png")
            
            # Check victory
            if self._check_victory():
                running = False
            
            # Progress logging
            if self.frame_count % 100 == 0:
                active_teams = list(set(m.team for m in self.marbles))
                print(f"Progress: {self.frame_count} frames. "
                     f"Active teams: {len(active_teams)} ({', '.join(active_teams)})")
            
            self.frame_count += 1
        
        print("Simulation complete!")
        pygame.quit()
        
        # Save audio log
        self._save_audio_log()
    
    def _save_audio_log(self) -> None:
        """Save audio events for post-processing."""
        audio_data = [
            {"t": evt.t, "name": evt.name, "vol": evt.vol}
            for evt in self.audio_events
        ]
        
        with open("audio_log.json", "w") as f:
            json.dump(audio_data, f, indent=2)
        
        print(f"Audio log saved: {len(self.audio_events)} events.")
