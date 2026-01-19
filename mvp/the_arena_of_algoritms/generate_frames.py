import pygame
import os
import sys

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine import SimulationEngine
from src.config import FRAMES_DIR, EXPORT_MODE

def generate_frames():
    """
    Runs the simulation and saves each frame as an image.
    This is optimized for later video encoding.
    """
    print("--- Starting Frame Generation ---")
    
    # Force export mode
    if not os.path.exists(FRAMES_DIR):
        os.makedirs(FRAMES_DIR)
        
    # Initialize engine
    # Note: We modified engine to use VideoRecorder if EXPORT_MODE is True.
    # But for frame-by-frame manual control if needed, we can toggle behavior.
    # However, the user asked for a script to generate frames.
    
    sim = SimulationEngine()
    
    # We will override the recorder for this specific script to save PNGs 
    # as it's often more reliable for high-quality sequence generation 
    # when performance during generation is less critical than final quality.
    
    sim.recorder = None # Disable pipe recorder
    
    frame_count = 0
    running = True
    clock = pygame.time.Clock()
    
    try:
        while sim.running:
            # Fixed dt for deterministic frame generation at 60fps
            dt = 1.0 / 60.0 
            
            sim.handle_events()
            sim.update(dt)
            sim.draw() # This draws to sim.screen
            
            # Save frame
            frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_count:05d}.png")
            pygame.image.save(sim.screen, frame_path)
            
            if frame_count % 60 == 0:
                print(f"Generated {frame_count} frames (approx {frame_count//60}s)...")
                
            frame_count += 1
            
            # check_victory is called inside sim.run normally, 
            # here we need to call it manually if we are driving the loop.
            if sim.check_victory(dt):
                # check_victory handles victory_timer and sets running=False
                pass

    except KeyboardInterrupt:
        print("Generation interrupted by user.")
    finally:
        pygame.quit()
        print(f"--- Finished! Total frames: {frame_count} ---")

if __name__ == "__main__":
    generate_frames()
