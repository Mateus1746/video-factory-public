import pygame
import pymunk
from pathlib import Path
from typing import List
import os

# Mock dependencies
import config
from entities import Marble
from effects import ParticleSystem, Explosion, FloatingText
from game_physics import PhysicsEngine
from game_state import GameState
from game_renderer import GameRenderer
from assets import AssetManager

def test_module_integrity():
    print("🔬 Testing Module Integrity...")
    
    # Dummy display for assets
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    pygame.display.set_mode((1, 1)) 
    
    space = pymunk.Space()
    assets = AssetManager()
    particles = ParticleSystem()
    
    class MockAudio:
        def play_sound(self, name, vol=1.0, pos=None): pass
        @property
        def events(self): return []

    audio = MockAudio()
    floating_texts = []
    explosions = []
    kill_feed = []

    print("\n1. Testing PhysicsEngine...")
    try:
        physics = PhysicsEngine(space, audio, particles, floating_texts, explosions, assets, kill_feed)
        print("✅ PhysicsEngine initialized.")
    except Exception as e:
        print(f"❌ PhysicsEngine failed: {e}")
        return

    print("\n2. Testing GameState & Pymunk Vec2d Compatibility...")
    try:
        state = GameState(space, physics, particles, floating_texts, explosions, kill_feed)
        print("✅ GameState initialized.")
        
        # Test the specific Vec2d logic that failed
        v = pymunk.Vec2d(10, 10)
        if hasattr(v, 'length_squared'):
            print(f"✅ Pymunk Vec2d 'length_squared' found: {v.length_squared}")
        else:
            print("❌ Pymunk Vec2d 'length_squared' MISSING! Checking standard methods...")
            # Fallback check
            print(f"   Available methods on Vec2d: {[m for m in dir(v) if not m.startswith('_')]}")

        # Test a single update
        state.update()
        print("✅ GameState update() successful.")
        
        # Test game_mode accessibility
        print(f"✅ Game Mode verified: {state.game_mode.name}")
        
    except Exception as e:
        print(f"❌ GameState failed: {e}")

    pygame.quit()

if __name__ == "__main__":
    test_module_integrity()
