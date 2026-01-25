"""
Main Entry Point for Marble War.
Orchestrates Physics, Rendering, and Game State.
"""

import json
from pathlib import Path
import pygame
import pymunk

import config
from assets import AssetManager
from arenas import ArenaGenerator
from effects import ParticleSystem
from game_physics import PhysicsEngine
from game_renderer import GameRenderer
from game_state import GameState
from game_types import AudioEvent
from themes import ThemeManager

class AudioProxy:
    def __init__(self, game_ref):
        self.game = game_ref
        self.events = []
    
    def play_sound(self, name, vol=1.0, pos=None):
        # Realtime Playback
        if name in self.game.assets.sounds:
            s = self.game.assets.sounds[name]
            s.set_volume(vol)
            s.play()
        
        # Audio Event Logging with Spatial Data
        # pos is usually a pymunk.Vec2d or Tuple (x, y)
        x_norm = 0.5 # Default Center
        if pos:
            # config.WIDTH is used to normalize x between 0.0 and 1.0
            x_norm = max(0.0, min(1.0, pos[0] / config.WIDTH))

        self.events.append(AudioEvent(
            t=self.game.frame_count * config.TIMESTEP,
            name=name,
            vol=vol,
            x=x_norm # New spatial attribute
        ))

class MarbleWar:
    def __init__(self, headless: bool = False):
        pygame.init()
        self.headless = headless
        
        # Display Setup
        if self.headless:
            self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        else:
            self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
            pygame.display.set_caption("Marble War - Chaos Edition")
            
        # Assets & Core
        self.assets = AssetManager()
        self.assets.load_all()
        
        self.space = pymunk.Space()
        self.space.gravity = config.GRAVITY
        self.space.damping = config.SPACE_DAMPING
        
        self.frame_count = 0
        self.audio_manager = AudioProxy(self)
        
        self.particles = ParticleSystem()
        self.floating_texts = []
        self.explosions = []
        self.kill_feed = [] # Shared list
        
        # Modules
        self.physics = PhysicsEngine(
            self.space, 
            self.audio_manager, 
            self.particles, 
            self.floating_texts, 
            self.explosions,
            self.assets,
            self.kill_feed # Pass shared list
        )
        
        self.state = GameState(
            self.space, 
            self.physics,
            self.particles,
            self.floating_texts,
            self.explosions,
            self.kill_feed # Pass shared list
        )
        
        # Arena
        self.arena_gen = ArenaGenerator(self.space)
        self.current_arena = self.arena_gen.generate()
        
        # Renderer
        self.renderer = GameRenderer(self.screen, self.assets, ThemeManager.get_random_theme())
        
    def step(self) -> bool:
        """Single simulation step."""
        self.space.step(config.TIMESTEP)
        self.arena_gen.update()
        self.state.update()
        
        self.frame_count += 1
        
        # Check for victory celebration
        if self.state.winner_team:
            self.state.celebration_timer -= 1
            if self.state.celebration_timer <= 0:
                return False
                
        return True

    def _draw(self):
        """Render frame."""
        self.renderer.draw(
            marbles=self.state.marbles,
            powerups=self.state.powerups,
            projectiles=self.state.projectiles,
            particles=self.particles,
            explosions=self.explosions,
            floating_texts=self.floating_texts,
            arena_gen=self.arena_gen,
            zone_active=self.state.zone_active,
            zone_radius=self.state.zone_radius,
            shake_offset=self.state.shake_offset,
            bomb_active=self.state.bomb_active,
            bomb_holder=self.state.bomb_holder,
            winner_team=self.state.winner_team,
            kill_feed=self.state.kill_feed,
            portals=self.state.portals,
            frame_count=self.frame_count # Pass frame_count
        )

    def run(self):
        """Standard execution loop."""
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
            
            if not self.step():
                running = False
                
            self._draw()
            if not self.headless:
                pygame.display.flip()
                clock.tick(config.FPS)
                
        self._save_audio_log()
        pygame.quit()

    def _save_audio_log(self) -> None:
        """Save captured audio events."""
        audio_data = [
            {"t": evt.t, "name": evt.name, "vol": evt.vol}
            for evt in self.audio_events
        ]
        with open("audio_log.json", "w") as f:
            json.dump(audio_data, f, indent=2)
        print(f"Audio log saved: {len(self.audio_events)} events.")

    @property
    def audio_events(self):
        return self.audio_manager.events
