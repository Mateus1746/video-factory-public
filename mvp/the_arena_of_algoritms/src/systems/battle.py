import pygame
import random
from ..config import *
from ..audio import PIANO_FREQUENCIES
from ..effects import update_particles
from .projectile_manager import ProjectileManager
from ..utils.loader import load_algorithms
from ..entities import Ring

# Load Algorithms Dynamically
ALGORITHMS = load_algorithms()

# Fallback for entities not yet refactored (if loader returned empty or partial)
# Ideally we rely purely on loader now for the refactored ones.
# But for safety, if list is empty, we might warn.
if not ALGORITHMS:
    print("WARNING: No algorithms loaded via dynamic loader. Check entity refactoring.")

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
        self.winner_team = None # 'top' or 'bot'
        
        # Initialize Systems
        self.projectile_manager = ProjectileManager()
        
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
        self.algo_top = self.instantiate_entity(self.top_class, self.center_top, self.rings_top)
        self.algo_bot = self.instantiate_entity(self.bot_class, self.center_bot, self.rings_bot)
        
        self.time_elapsed = 0.0
        self.time_scale = 1.0
        self.enrage_active = False

    def get_team_hp_pct(self, team="top"):
        rings = self.rings_top if team == "top" else self.rings_bot
        current = sum(r.hp for r in rings)
        max_h = sum(r.max_hp for r in rings)
        return current / max_h if max_h > 0 else 0

    def instantiate_entity(self, cls, center, rings):
        try:
            return cls(center, rings, projectile_manager=self.projectile_manager)
        except TypeError:
            return cls(center, rings)

    def update(self, dt):
        # Time Management
        real_dt = dt
        dt *= self.time_scale
        self.time_elapsed += real_dt
        
        # Enrage Logic (After 45s)
        if self.time_elapsed > 45 and not self.enrage_active:
            self.enrage_active = True
            self.logger.info("ENRAGE MODE ACTIVATED")
            # Speed up everything slightly? Or just visual?
            # Let's keep it simple: Enrage = Red tint (handled in renderer)
        
        # Slow Motion Logic (Last Stand)
        # Check if either side has only 1 ring left with < 20% HP
        top_alive = [r for r in self.rings_top if r.alive]
        bot_alive = [r for r in self.rings_bot if r.alive]
        
        low_hp_drama = False
        if len(top_alive) == 1 and top_alive[0].hp < top_alive[0].max_hp * 0.2:
            low_hp_drama = True
        elif len(bot_alive) == 1 and bot_alive[0].hp < bot_alive[0].max_hp * 0.2:
            low_hp_drama = True
            
        if low_hp_drama and not self.game_over:
            target_scale = 0.3 # 30% speed
            self.time_scale = self.time_scale * 0.9 + target_scale * 0.1 # Smooth transition
        else:
            self.time_scale = self.time_scale * 0.9 + 1.0 * 0.1

        # Use REAL DT for audio so music/sfx don't desync or shorten video
        self.sound_manager.update(real_dt)
        
        self.algo_top.update(dt)
        self.algo_bot.update(dt)
        
        # Update Projectiles
        self.projectile_manager.update(dt, self.rings_top + self.rings_bot)
        
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
                # Top cleared all its rings -> Top Wins? 
                # Wait, "Top cleared all rings" means Top's rings are dead. That means Top LOST.
                # In this game, algorithms destroy OWN rings? 
                # "Algorithm Battle: Entities attack concentric rings."
                # Usually "Top Algo" attacks "Top Rings" to clear the level.
                # Let's assume the goal is to clear YOUR rings faster.
                self.winner_text = f"{self.top_name} WINS!"
                self.winner_color = self.top_color
                self.winner_team = 'top'
                print(f"DEBUG: Top cleared all rings. {self.top_name} wins.")
            elif bot_all_dead and not top_all_dead:
                # Bot cleared all its rings -> Bot Wins
                self.winner_text = f"{self.bot_name} WINS!"
                self.winner_color = self.bot_color
                self.winner_team = 'bot'
                print(f"DEBUG: Bot cleared all rings. {self.bot_name} wins.")
            else:
                self.winner_text = "IT'S A TIE!"
                self.winner_color = WHITE
                print("DEBUG: Both sides cleared simultaneously.")
            
            print(f"SIMULATION ENDED: {self.winner_text}")
            self.game_over = True