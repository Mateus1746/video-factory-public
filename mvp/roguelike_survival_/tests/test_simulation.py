import pytest
import os
import pygame
from src.render_engine import RenderEngine, GameWorld
from src.config import *

# Set dummy drivers for headless testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

def test_engine_init():
    pygame.init()
    engine = RenderEngine(1080, 1920)
    assert engine.world.player is not None
    assert engine.world.gm.level == 1
    assert len(engine.world.xp_orbs) > 0

def test_pure_logic_simulation():
    """Verify that GameWorld can run without RenderEngine/Pygame Surface."""
    world = GameWorld(1080, 1920)
    dt = 1.0/60.0
    for _ in range(100):
        world.update(dt)
    
    assert world.gm.time_elapsed > 0
    assert len(world.enemies) >= 0

def test_simulation_step():
    pygame.init()
    engine = RenderEngine(1080, 1920)
    
    # Run 5 seconds of simulation
    dt = 1.0/60.0
    for _ in range(300):
        engine.step(dt)
        
    assert engine.world.gm.time_elapsed > 0
    assert 0 <= engine.world.player.x <= WORLD_W
    assert 0 <= engine.world.player.y <= WORLD_H

def test_render_output():
    pygame.init()
    engine = RenderEngine(200, 400) # Small for test
    frame = engine.render()
    
    assert frame.shape == (400, 200, 3) # (H, W, RGB)
    assert frame.dtype == "uint8"

if __name__ == "__main__":
    pytest.main()
