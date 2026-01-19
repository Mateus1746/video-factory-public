import pygame
import random
import numpy as np
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

class RenderEngine:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.surface = pygame.Surface((width, height))
        self.sound = SoundManager()
        self.hud = HUD(width, height)
        self.reset()

    def reset(self):
        self.player = Player()
        self.weapon = Weapon(self.player)
        self.gm = GameManager()
        self.camera = Camera()
        self.particles = ParticleSystem()
        self.enemies, self.xp_orbs = [], []
        
        self.game_over = self.victory = False
        self.corner_time = 0.0
        self.in_corner = False
        
        # Initial Orbs
        for _ in range(35):
            self.xp_orbs.append(XPOrb(random.uniform(200, WORLD_W-200), random.uniform(200, WORLD_H-200)))
        
        self.sound.play_music()

    def step(self, dt):
        if self.game_over or self.victory: return
        if not self.player.is_alive():
            self.game_over = True
            self.sound.stop_music()
            self.sound.play_sfx("game_over")
            return

        # 1. Upgrades
        if self.gm.upgrade_pending:
            up = self.gm.get_random_upgrades()[0]
            self.gm.apply_upgrade(up, self.player, self.weapon)
            self.sound.play_sfx("level_up")
        
        # 2. Player & Systems
        self.player.update(dt, self.enemies, self.xp_orbs)
        self.weapon.update(dt, self.enemies, self.particles, self.camera, self.sound)
        self.gm.update_spawn(dt, self.enemies, self.xp_orbs)
        
        # 3. Corner Logic
        if self.player.pos.x < CORNER_MARGIN or self.player.pos.x > WORLD_W - CORNER_MARGIN or \
           self.player.pos.y < CORNER_MARGIN or self.player.pos.y > WORLD_H - CORNER_MARGIN:
            self.corner_time += dt
            self.in_corner = True
        else:
            self.corner_time = 0; self.in_corner = False

        # 4. Enemies Update
        self._update_enemies(dt)
        self._update_orbs(dt)

        # 5. Camera & Particles
        self.camera.follow(self.player.pos.x, self.player.pos.y, self.width, self.height)
        self.camera.update(dt)
        self.particles.update(dt)

    def _update_enemies(self, dt):
        alive = []
        for e in self.enemies:
            e.update(dt, self.player, self.camera)
            if e.is_dead():
                if e.type == "boss": self.victory = True; self.sound.play_sfx("level_up")
                self.gm.kills += 1
                self.sound.play_sfx("kill")
                self.xp_orbs.append(XPOrb(e.pos.x, e.pos.y))
                self.particles.emit(e.pos.x, e.pos.y, e.color, count=20)
            else: alive.append(e)
        self.enemies = alive

    def _update_orbs(self, dt):
        keep = []
        for o in self.xp_orbs:
            if o.update(dt, self.player):
                self.gm.add_xp(o.value)
                self.sound.play_sfx("exp")
            else: keep.append(o)
        self.xp_orbs = keep

    def render(self):
        self.draw_to_surface()
        return pygame.surfarray.array3d(self.surface).transpose([1, 0, 2])

    def draw_to_surface(self):
        self.surface.fill(COLOR_BG)
        ox, oy = self.camera.offset

        # Grid
        step = 150
        for x in range(int(ox % step) - step, self.width + step, step):
            pygame.draw.line(self.surface, COLOR_GRID, (x, 0), (x, self.height), 1)
        for y in range(int(oy % step) - step, self.height + step, step):
            pygame.draw.line(self.surface, COLOR_GRID, (0, y), (self.width, y), 1)

        # Draw Layers
        for o in self.xp_orbs: o.draw(self.surface, (ox, oy))
        self.particles.draw(self.surface, (ox, oy))
        for e in self.enemies: e.draw(self.surface, (ox, oy))
        
        if self.player.is_alive():
            self.weapon.draw(self.surface, (ox, oy))
            self.player.draw(self.surface, (ox, oy))

        self.hud.draw(self.surface, self.gm, self.player, self.corner_time, self.victory, self.game_over)