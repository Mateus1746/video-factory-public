"""
Game Mode Logic for Marble War.
Handles rules, setup, and victory conditions for different modes.
"""

import random
from typing import List, Tuple, Optional
import pymunk
import pygame

import config
from entities import Marble

class GameMode:
    """Base class for game modes."""
    name = "Base"
    
    def setup_marbles(self, space: pymunk.Space) -> List[Marble]:
        return []
    
    def handle_collision(self, m1: Marble, m2: Marble) -> Tuple[bool, Optional[str]]:
        """
        Returns: (should_play_sound, floating_text_message)
        """
        return False, None
    
    def check_victory(self, marbles: List[Marble], frame_count: int) -> Optional[str]:
        return None

class BattleRoyale(GameMode):
    """Classic 4-team deathmatch."""
    name = "Battle Royale"
    
    def setup_marbles(self, space: pymunk.Space) -> List[Marble]:
        marbles = []
        margin = 100
        positions = [
            (margin, margin, "red", config.COLOR_RED),
            (config.WIDTH - margin, margin, "blue", config.COLOR_BLUE),
            (margin, config.HEIGHT - margin, "yellow", config.COLOR_YELLOW),
            (config.WIDTH - margin, config.HEIGHT - margin, "green", config.COLOR_GREEN)
        ]
        
        # 12 marbles per team
        count_per_team = 12
        for start_x, start_y, team, color in positions:
            for _ in range(count_per_team):
                x = start_x + random.uniform(-40, 40)
                y = start_y + random.uniform(-40, 40)
                marbles.append(Marble(x, y, team, color, space))
        return marbles

    def check_victory(self, marbles: List[Marble], frame_count: int) -> Optional[str]:
        if frame_count < 100: return None
        active_teams = list(set(m.team for m in marbles))
        if len(active_teams) == 1:
            return active_teams[0].upper()
        if len(active_teams) == 0:
            return "DRAW"
        return None

class ZombieOutbreak(GameMode):
    """Infection mode: 30s Trap, 20s Escape."""
    name = "Zombie Outbreak"
    
    def setup_marbles(self, space: pymunk.Space) -> List[Marble]:
        marbles = []
        margin = 100
        corners = [
            (margin, margin),
            (config.WIDTH - margin, margin),
            (margin, config.HEIGHT - margin),
            (config.WIDTH - margin, config.HEIGHT - margin)
        ]
        
        num_civilians = 60
        for i in range(num_civilians):
            cx, cy = corners[i % 4]
            x = cx + random.uniform(-50, 50)
            y = cy + random.uniform(-50, 50)
            
            civ = Marble(x, y, "civilian", (0, 100, 255), space)
            civ.trapped_timer = 30.0 # 30s countdown
            civ.initial_pos = (x, y)
            marbles.append(civ)
            
        zombie = Marble(config.WIDTH//2, config.HEIGHT//2, "zombie", (50, 255, 50), space)
        zombie.infect() 
        zombie.brush_multiplier = 2 
        zombie.trapped_timer = 30.0 # 30s countdown
        zombie.initial_pos = (config.WIDTH//2, config.HEIGHT//2)
        marbles.append(zombie)
        
        return marbles

    def handle_collision(self, m1: Marble, m2: Marble) -> Tuple[bool, Optional[str]]:
        msg = None
        sound = False
        
        if getattr(m1, 'trapped_timer', 0) > 0 or getattr(m2, 'trapped_timer', 0) > 0:
            return False, None

        z1 = m1.team == "zombie"
        z2 = m2.team == "zombie"
        
        if z1 and not z2 and m2.team == "civilian":
            m2.infect()
            msg = "INFECTED!"
            sound = True
        elif z2 and not z1 and m1.team == "civilian":
            m1.infect()
            msg = "INFECTED!"
            sound = True
            
        return sound, msg

    def check_victory(self, marbles: List[Marble], frame_count: int) -> Optional[str]:
        # During 30s setup, no victory possible
        if frame_count < 30 * config.FPS: return None
        
        counts = {"zombie": 0, "civilian": 0}
        for m in marbles:
            if m.team in counts:
                counts[m.team] += 1
        
        # 1. Zombies win if all are infected before 50s
        if counts["civilian"] == 0:
            return "THE HORDE" 
        
        # 2. Humans win if they survive 20s of pursuit (30s setup + 20s escape = 50s)
        if frame_count >= 50 * config.FPS:
            return "HUMAN SURVIVORS"
            
        return None

# NEW: Global Portal Manager
class Portal:
    def __init__(self, entry_pos: Tuple[float, float], exit_pos: Tuple[float, float], color: Tuple[int, int, int]):
        self.entry = entry_pos
        self.exit = exit_pos
        self.color = color
        self.radius = 60

def generate_portals() -> List[Portal]:
    """Occasionally generate portal pairs."""
    if random.random() > 0.7: # 30% chance of portals
        p1 = Portal((200, config.HEIGHT//2), (config.WIDTH-200, config.HEIGHT//2), (255, 165, 0)) # Orange
        p2 = Portal((config.WIDTH-200, config.HEIGHT//2), (200, config.HEIGHT//2), (0, 191, 255)) # Blue
        return [p1, p2]
    return []

class Domination(GameMode):
    """4 Teams. Touching converts enemy to your team."""
    name = "Color Domination"
    
    def setup_marbles(self, space: pymunk.Space) -> List[Marble]:
        # Same setup as Battle Royale
        return BattleRoyale().setup_marbles(space)

    def handle_collision(self, m1: Marble, m2: Marble) -> Tuple[bool, Optional[str]]:
        # Stronger impulse wins (attacker logic) or random?
        # Let's say: Faster marble converts slower marble.
        if m1.team == m2.team: return False, None
        
        v1 = m1.body.velocity.length
        v2 = m2.body.velocity.length
        
        # Threshold for conversion
        if abs(v1 - v2) < 50: return False, None 
        
        winner = m1 if v1 > v2 else m2
        loser = m2 if v1 > v2 else m1
        
        # Convert loser
        loser.team = winner.team
        loser.color = winner.color
        loser.face_timer = 1.0
        loser.current_face = "assustado"
        
        return True, None # No text, too chaotic

    def check_victory(self, marbles: List[Marble], frame_count: int) -> Optional[str]:
        return BattleRoyale().check_victory(marbles, frame_count)

class Juggernaut(GameMode):
    """1 Giant Boss vs Many Small Attackers."""
    name = "Juggernaut Boss"
    
    def setup_marbles(self, space: pymunk.Space) -> List[Marble]:
        marbles = []
        
        # 50 Attackers
        for _ in range(50):
            x = random.randint(100, config.WIDTH - 100)
            y = random.randint(100, config.HEIGHT - 100)
            # Ensure not spawning on boss (center)
            if abs(x - config.WIDTH//2) < 150 and abs(y - config.HEIGHT//2) < 150:
                continue
            
            attacker = Marble(x, y, "attacker", (0, 200, 255), space)
            attacker.assassin_mode = True # Now they have guns!
            attacker.ammo = 9999 # Infinite ammo
            marbles.append(attacker)
            
        # The Boss
        boss = Marble(config.WIDTH//2, config.HEIGHT//2, "boss", (255, 0, 0), space)
        # Physics hacking for Boss Size
        space.remove(boss.shape, boss.body)
        
        boss.body = pymunk.Body(100, pymunk.moment_for_circle(100, 0, 100)) # Heavy mass
        boss.body.position = (config.WIDTH//2, config.HEIGHT//2)
        boss.shape = pymunk.Circle(boss.body, 100) # Huge radius
        boss.shape.elasticity = 1.2 # Bouncy!
        boss.shape.friction = 0.5
        boss.shape.collision_type = 1
        boss.shape.data = boss
        
        # Boss Stats
        boss.hp = 1000 # High health since Friendly Fire is OFF
        boss.max_hp = 1000
        boss.current_face = "bravo"
        boss.face_timer = 9999
        
        # Boss Aggression
        boss.assassin_mode = True # Boss shoots back!
        boss.ammo = 9999 # Infinite ammo
        
        space.add(boss.body, boss.shape)
        marbles.append(boss)
        
        return marbles

    def check_victory(self, marbles: List[Marble], frame_count: int) -> Optional[str]:
        boss_alive = any(m.team == "boss" for m in marbles)
        attackers_alive = any(m.team == "attacker" for m in marbles)
        
        if not boss_alive: return "ATTACKERS"
        if not attackers_alive: return "THE JUGGERNAUT"
        return None

def get_random_mode() -> GameMode:
    """Select a random game mode."""
    options = [BattleRoyale, ZombieOutbreak, Domination, Juggernaut]
    mode = random.choice(options)
    print(f"🎲 Selected Mode: {mode.name}")
    return mode()