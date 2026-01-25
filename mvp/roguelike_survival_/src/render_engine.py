import pygame
import random
import numpy as np
import os
from typing import List, Optional
from src.config import *
from src.entities.player import Player
from src.entities.weapon import Weapon
from src.entities.enemy import Enemy
from src.entities.orb import XPOrb
from src.systems.particles import ParticleSystem
from src.systems.camera import Camera
from src.systems.gamemanager import GameManager
from src.systems.sound import SoundManager
from src.systems.hud import HUD
from src.systems.physics import SpatialHash
from src.systems.effects import EffectsManager
from src.systems.background import BackgroundSystem

class GameWorld:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.player = Player()
        self.weapon = Weapon(self.player)
        self.gm = GameManager()
        self.camera = Camera()
        self.particles = ParticleSystem()
        self.effects = EffectsManager(width, height)
        self.background = BackgroundSystem(width, height)
        self.spatial_hash = SpatialHash(cell_size=250)
        self.enemies: List[Enemy] = []
        self.xp_orbs: List[XPOrb] = []
        
        self.game_over = False
        self.victory = False
        self.corner_time = 0.0
        self.in_corner = False
        self.slow_mo_factor = 1.0
        self.target_slow_mo = 1.0
        
        self._setup_initial_state()

    def _setup_initial_state(self):
        for _ in range(35):
            self.xp_orbs.append(XPOrb(random.uniform(200, WORLD_W-200), random.uniform(200, WORLD_H-200)))

    def update(self, dt: float, sound_manager: Optional[SoundManager] = None):
        self.slow_mo_factor += (self.target_slow_mo - self.slow_mo_factor) * 5.0 * dt
        effective_dt = dt * self.slow_mo_factor
        
        if self.game_over or self.victory: 
            self.target_slow_mo = 0.2
            self.camera.update(dt)
            self.particles.update(dt)
            self.effects.update(dt)
            return
        
        if not self.player.is_alive():
            self.game_over = True
            self.effects.screen_flash((255, 0, 0), 0.5)
            if sound_manager:
                sound_manager.stop_music()
                sound_manager.play_sfx("game_over")
            return

        # 1. Spatial Partitioning
        self.spatial_hash.clear()
        for e in self.enemies:
            self.spatial_hash.insert(e)

        # 2. Leveling & Upgrades
        if self.gm.upgrade_pending:
            up = self.gm.get_random_upgrades()[0]
            self.gm.apply_upgrade(up, self.player, self.weapon)
            self.effects.add_floating_text(self.player.x, self.player.y - 50, f"UPGRADE: {up.upper()}", COLOR_XP, size=50)
            self.effects.screen_flash(COLOR_XP, 0.2)
            if sound_manager: sound_manager.play_sfx("level_up")
        
        # 3. Movement & AI
        nearby_enemies = self.spatial_hash.get_nearby(self.player.x, self.player.y, 600)
        old_hp = self.player.health
        self.player.update(effective_dt, nearby_enemies, self.xp_orbs)
        
        if self.player.health < old_hp:
            self.effects.screen_flash((255, 0, 0), 0.1)
            self.target_slow_mo = 0.5 
        else:
            self.target_slow_mo = 1.0

        self.weapon.update(effective_dt, self.enemies, self.particles, self.camera, sound_manager, self.spatial_hash)
        
        old_boss_spawned = self.gm.boss_spawned
        self.gm.update_spawn(effective_dt, self.enemies, self.xp_orbs)
        if self.gm.boss_spawned and not old_boss_spawned:
             self.effects.add_floating_text(WORLD_W/2, WORLD_H/2 - 400, "BOSS INCOMING!", (255, 0, 0), size=80)
             self.effects.screen_flash((255, 0, 0), 0.5)
             self.camera.add_shake(25)

        # 4. Corner Logic
        if self.player.pos.x < CORNER_MARGIN or self.player.pos.x > WORLD_W - CORNER_MARGIN or \
           self.player.pos.y < CORNER_MARGIN or self.player.pos.y > WORLD_H - CORNER_MARGIN:
            self.corner_time += effective_dt
            self.in_corner = True
        else:
            self.corner_time = 0; self.in_corner = False

        # 5. Entity Lifecycles
        self._update_enemies(effective_dt, sound_manager)
        self._update_orbs(effective_dt, sound_manager)

        # 6. Effects & Feedback
        if self.gm.boss_spawned:
            self.camera.set_zoom(0.8)
        elif self.player.health < 30:
            self.camera.set_zoom(1.3)
        else:
            self.camera.set_zoom(1.0)

        self.camera.follow(self.player.pos.x, self.player.pos.y, self.width, self.height)
        self.camera.update(dt)
        self.particles.update(effective_dt)
        self.effects.update(dt)

    def _update_enemies(self, dt: float, sound_manager: Optional[SoundManager]):
        alive = []
        for e in self.enemies:
            e.update(dt, self.player, self.camera)
            if e.is_dead():
                if e.type == "boss": 
                    self.victory = True
                    self.effects.screen_flash((0, 255, 255), 0.8)
                    if sound_manager: sound_manager.play_sfx("level_up")
                self.gm.kills += 1
                if sound_manager: sound_manager.play_sfx("kill")
                self.xp_orbs.append(XPOrb(e.pos.x, e.pos.y))
                self.particles.emit(e.pos.x, e.pos.y, e.color, count=20)
            else: alive.append(e)
        self.enemies = alive

    def _update_orbs(self, dt: float, sound_manager: Optional[SoundManager]):
        keep = []
        for o in self.xp_orbs:
            if o.update(dt, self.player):
                self.gm.add_xp(o.value)
                if sound_manager: sound_manager.play_sfx("exp")
            else: keep.append(o)
        self.xp_orbs = keep


class RenderEngine:
    def __init__(self, width: int, height: int):
        self.width, self.height = width, height
        if not pygame.display.get_init():
            pygame.display.init()
        if pygame.display.get_surface() is None:
            pygame.display.set_mode((1, 1), pygame.NOFRAME)

        self.surface = pygame.Surface((width, height))
        self.sound = SoundManager()
        self.hud = HUD(width, height)
        self.world = GameWorld(width, height)
        self.sound.play_music()

    @property
    def game_over(self): return self.world.game_over
    @property
    def victory(self): return self.world.victory

    def reset(self):
        self.world = GameWorld(self.width, self.height)
        self.sound.play_music()

    def step(self, dt: float):
        self.world.update(dt, self.sound)

    def render(self) -> np.ndarray:
        self.draw_to_surface()
        # Removed problematic chromatic aberration pixels3d call
        return pygame.surfarray.array3d(self.surface).transpose([1, 0, 2])

    def draw_to_surface(self):
        self.surface.fill(COLOR_BG)
        
        # 0. Background System (Parallax stars/dust)
        self.world.background.draw(self.surface, self.world.camera)

        # Grid (with Zoom support)
        cam = self.world.camera
        step = int(150 * cam.zoom)
        ox, oy = cam.offset
        for x in range(int(ox % step) - step, self.width + step, step):
            pygame.draw.line(self.surface, COLOR_GRID, (x, 0), (x, self.height), 1)
        for y in range(int(oy % step) - step, self.height + step, step):
            pygame.draw.line(self.surface, COLOR_GRID, (0, y), (self.width, y), 1)

        # Layers
        for o in self.world.xp_orbs: o.draw(self.surface, cam)
        self.world.particles.draw(self.surface, cam)
        for e in self.world.enemies: e.draw(self.surface, cam)
        
        if self.world.player.is_alive():
            self.world.weapon.draw(self.surface, cam)
            self.world.player.draw(self.surface, cam)

        # World Space Effects (Floating Text)
        self.world.effects.draw_world_effects(self.surface, cam)
        
        # Screen Space Effects (Flashes, Vignette)
        self.world.effects.draw_screen_effects(self.surface)

        self.hud.draw(self.surface, self.world.gm, self.world.player, self.world.corner_time, self.world.victory, self.world.game_over)