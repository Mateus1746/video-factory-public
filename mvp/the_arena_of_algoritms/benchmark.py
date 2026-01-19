import pygame
import time
from src.config import *
from src.systems.battle import ALGORITHMS, BattleManager
from src.audio import SoundManager

class MockLogger:
    def info(self, msg): pass
    def error(self, msg): pass

def run_benchmark():
    pygame.init()
    # Use a small hidden window
    pygame.display.set_mode((1, 1), pygame.HIDDEN)
    
    sound_manager = SoundManager()
    logger = MockLogger()
    
    results = []
    
    print(f"{'ALGORITHM':<25} | {'TIME TO CLEAR (s)':<15}")
    print("-" * 45)

    for algo_tuple in ALGORITHMS:
        algo_class, algo_name, algo_color = algo_tuple
        
        # Setup a controlled battle manager
        # We'll override the random selection to test THIS specific algorithm
        bm = BattleManager(sound_manager, logger)
        bm.top_class = algo_class
        bm.top_name = algo_name
        # Re-init algo with correct rings
        bm.algo_top = algo_class(bm.center_top, bm.rings_top)
        
        start_time = time.time()
        sim_time = 0.0
        dt = 1.0 / 60.0 # Standard FPS
        
        # Run until TOP (the one we are testing) clears ALL its rings
        timeout = 180.0 # 3 minutes max
        while not all(not r.alive for r in bm.rings_top) and sim_time < timeout:
            bm.algo_top.update(dt)
            for r in bm.rings_top:
                r.update_visuals(dt)
            sim_time += dt
            
        if sim_time >= timeout:
            status = "TIMEOUT"
        else:
            status = f"{sim_time:.2f}s"
            
        print(f"{algo_name:<25} | {status:<15}")
        results.append((algo_name, sim_time))

    pygame.quit()
    return results

if __name__ == "__main__":
    run_benchmark()
