import pygame
import sys
import time
import traceback
from typing import Optional
from .config import *
from .recorder import VideoRecorder
from .systems.battle import BattleManager
from .systems.renderer import RenderSystem
from .audio import SoundManager, RECORDING_MANAGER
from .utils import DIAGNOSTICS, logger

class SimulationEngine:
    def __init__(self, output_filename: Optional[str] = None):
        pygame.init()
        self.telemetry = DIAGNOSTICS
        self.logger = logger
        self.logger.info("SimulationEngine initializing...")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Algorithm Battle: Random Duel")
        self.clock = pygame.time.Clock()
        
        self.sound_manager = SoundManager()
        
        if EXPORT_MODE:
            recorder_filename = output_filename if output_filename else "simulation.mp4"
            self.recorder = VideoRecorder(output_file=recorder_filename)
            self.recorder.start()
        else:
            self.recorder = None

        # --- REFACTORED SYSTEMS ---
        self.battle_manager = BattleManager(self.sound_manager, self.logger)
        self.renderer = RenderSystem(self.screen)
        
        self.running = True

    def run(self) -> None:
        try:
            while self.running:
                t_start = time.perf_counter()
                
                if EXPORT_MODE:
                    dt = 1.0 / FPS
                else:
                    dt = self.clock.tick(FPS) / 1000.0
                if dt > 0.05: dt = 0.05
                
                self.handle_events()
                
                # Update
                t_upd_start = time.perf_counter()
                self.renderer.update_visuals()
                self.battle_manager.update(dt)
                t_upd_end = time.perf_counter()
                
                # Draw
                t_drw_start = time.perf_counter()
                self.renderer.draw(self.battle_manager, self.recorder, DEBUG_MODE, self.telemetry)
                t_drw_end = time.perf_counter()
                
                # Logic to close
                if self.battle_manager.game_over and self.battle_manager.victory_timer >= 5.0:
                    self.save_and_exit()

                t_end = time.perf_counter()
                self.telemetry.record_performance(
                    (t_upd_end - t_upd_start) * 1000.0,
                    (t_drw_end - t_drw_start) * 1000.0,
                    (t_end - t_start) * 1000.0
                )
        except Exception as e:
            self.telemetry.log_error(f"FATAL ERROR in main loop: {e}", fatal=True)
            traceback.print_exc()
            self.save_and_exit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_and_exit()

    def save_and_exit(self) -> None:
        self.logger.info("Exiting simulation...")
        if EXPORT_MODE:
            print("Saving audio before exit...")
            RECORDING_MANAGER.save("simulation_audio.wav")
            
        if self.recorder:
            self.recorder.stop()
        self.running = False