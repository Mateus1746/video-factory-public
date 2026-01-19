import pygame
import random
from ..config import *
from ..audio import PIANO_FREQUENCIES
from ..effects import update_particles
from ..entities import (
    Ring, FibonacciSpiral, Spawner, OrbitStriker, ChaosJumper, 
    LaserSweeper, QuantumSwarm, TeslaStorm, SnakeEater, RadarSweep, 
    VolcanoEruption, BinaryGlitch, SonicWave, NaniteCloud
)

ALGORITHMS = [
    (FibonacciSpiral, "FIBONACCI SPIRAL", YELLOW),
    (Spawner, "SWARM SPAWNER", PINK),
    (OrbitStriker, "ORBIT STRIKER", NEON_GREEN),
    (ChaosJumper, "CHAOS JUMPER", (255, 50, 50)),
    (LaserSweeper, "LASER SWEEPER", (50, 255, 255)),
    (QuantumSwarm, "QUANTUM SWARM", (180, 0, 255)),
    (TeslaStorm, "TESLA STORM", (200, 200, 255)),
    (SnakeEater, "SNAKE EATER", (50, 255, 100)),
    (RadarSweep, "RADAR SWEEP", (255, 50, 50)),
    (VolcanoEruption, "VOLCANO ERUPTION", (255, 120, 0)),
    (BinaryGlitch, "BINARY GLITCH", (0, 255, 0)),
    (SonicWave, "SONIC WAVE", (200, 200, 200)),
    (NaniteCloud, "NANITE CLOUD", (180, 180, 180))
]

class BattleManager:
    # Reference times from Benchmark (approximate seconds to clear)
    ALGO_PERFORMANCE = {
        "BINARY GLITCH": 38,
        "TESLA STORM": 38,
        "CHAOS JUMPER": 35,
        "QUANTUM SWARM": 40,
        "SWARM SPAWNER": 45,
        "SNAKE EATER": 45,
        "NANITE CLOUD": 47,
        "ORBIT STRIKER": 48,
        "RADAR SWEEP": 48,
        "SONIC WAVE": 51,
        "FIBONACCI SPIRAL": 52,
        "VOLCANO ERUPTION": 58,
        "LASER SWEEPER": 62
    }

    def __init__(self, sound_manager, logger):
        self.sound_manager = sound_manager
        self.logger = logger
        self.shake_intensity = 0.0
        self.victory_timer = 0.0
        self.game_over = False
        self.winner_text = None
        self.winner_color = WHITE
        
        # Select Random Algorithms
        self.algo_selection = random.sample(ALGORITHMS, 2)
        self.top_class, self.top_name, self.top_color = self.algo_selection[0]
        self.bot_class, self.bot_name, self.bot_color = self.algo_selection[1]
        
        self.logger.info(f"MATCHUP: [TOP] {self.top_name} vs [BOT] {self.bot_name}")

        # Setup Entities
        self.center_top = (SCREEN_WIDTH // 2, HALF_HEIGHT // 2)
        self.rings_top = []
        for i, (r, hp) in enumerate(zip(RING_RADII, RING_HP)):
            is_core = (i == len(RING_RADII) - 1)
            self.rings_top.append(Ring(r, hp, self.center_top, RING_COLORS[i], PIANO_FREQUENCIES[i % len(PIANO_FREQUENCIES)], is_core=is_core))
        
        self.center_bot = (SCREEN_WIDTH // 2, HALF_HEIGHT + HALF_HEIGHT // 2)
        self.rings_bot = []
        for i, (r, hp) in enumerate(zip(RING_RADII, RING_HP)):
            is_core = (i == len(RING_RADII) - 1)
            self.rings_bot.append(Ring(r, hp, self.center_bot, RING_COLORS[i], PIANO_FREQUENCIES[i % len(PIANO_FREQUENCIES)], is_core=is_core))

        # --- ADAPTIVE BUFF LOGIC ---
        time_top = self.ALGO_PERFORMANCE.get(self.top_name, 45)
        time_bot = self.ALGO_PERFORMANCE.get(self.bot_name, 45)
        
        diff = time_top - time_bot
        if abs(diff) > 8: # Threshold for buff
            if diff > 0: # Top is slower
                buff = time_top / time_bot
                for r in self.rings_top: r.damage_multiplier = buff
                self.logger.info(f"ADAPTIVE BUFF: [TOP] {self.top_name} gets {buff:.2f}x damage multiplier")
            else: # Bot is slower
                buff = time_bot / time_top
                for r in self.rings_bot: r.damage_multiplier = buff
                self.logger.info(f"ADAPTIVE BUFF: [BOT] {self.bot_name} gets {buff:.2f}x damage multiplier")

        # Initialize Algorithms
        self.algo_top = self.top_class(self.center_top, self.rings_top)
        self.algo_bot = self.bot_class(self.center_bot, self.rings_bot)
        
    def update(self, dt):
        self.sound_manager.update(dt)
        
        self.algo_top.update(dt)
        self.algo_bot.update(dt)
        
        for r in self.rings_top: r.update_visuals(dt)
        for r in self.rings_bot: r.update_visuals(dt)
        
        update_particles()
        
        # Screen Shake Logic
        if self.shake_intensity > 0:
            self.shake_intensity -= dt * 10
            if self.shake_intensity < 0: self.shake_intensity = 0
            
        # Trigger shake check based on damage flash
        for r in self.rings_top + self.rings_bot:
            if r.flash_timer > 0.08:
                self.shake_intensity = 5.0 if r in self.rings_top else 3.0
                
        # Check Victory
        self.check_victory_condition(dt)

    def check_victory_condition(self, dt):
        if self.game_over:
            self.victory_timer += dt
            return

        # NEW VICTORY: All rings of a side must be destroyed
        top_all_dead = all(not r.alive for r in self.rings_top)
        bot_all_dead = all(not r.alive for r in self.rings_bot)

        if top_all_dead or bot_all_dead:
            if self.victory_timer == 0:
                self.sound_manager.play_sfx(440, 0.5, 'square')
                self.sound_manager.play_sfx(554.37, 0.5, 'square')
                self.sound_manager.play_sfx(659.25, 0.8, 'square')
            
            if top_all_dead and not bot_all_dead:
                # Top cleared all its rings -> Top Wins
                self.winner_text = f"{self.top_name} WINS!"
                self.winner_color = self.top_color
                print(f"DEBUG: Top cleared all rings. {self.top_name} wins.")
            elif bot_all_dead and not top_all_dead:
                # Bot cleared all its rings -> Bot Wins
                self.winner_text = f"{self.bot_name} WINS!"
                self.winner_color = self.bot_color
                print(f"DEBUG: Bot cleared all rings. {self.bot_name} wins.")
            else:
                self.winner_text = "IT'S A TIE!"
                self.winner_color = WHITE
                print("DEBUG: Both sides cleared simultaneously.")
            
            print(f"SIMULATION ENDED: {self.winner_text}")
            self.game_over = True