import os
import sys
import subprocess
import pygame
import numpy as np
from src.config import SCREEN_W, SCREEN_H
from src.render_engine import RenderEngine

# Force Headless
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

def main():
    print("🎬 Roguelike Survival: Factory Recorder")
    
    # Initialize Pygame (Headless)
    pygame.init()
    
    # Setup Output
    output_file = os.path.join(os.path.dirname(__file__), "output_render.mp4")
    fps = 60
    duration = 60 # 60 Seconds cap
    total_frames = fps * duration
    
    # FFmpeg Command
    # Input: Raw RGB24 video, 1080x1920
    # Output: H.264 MP4
    cmd = [
        'ffmpeg', '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', f'{SCREEN_W}x{SCREEN_H}',
        '-pix_fmt', 'rgb24',
        '-r', str(fps),
        '-i', '-',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '18',
        '-pix_fmt', 'yuv420p',
        output_file
    ]
    
    print(f"🎥 Recording to {output_file}...")
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    
    # Initialize Engine
    engine = RenderEngine(SCREEN_W, SCREEN_H)
    dt = 1.0 / fps # Fixed timestep
    
    frame_count = 0
    
    try:
        while frame_count < total_frames and not engine.game_over:
            # 1. Step Logic
            engine.step(dt)
            
            # 2. Draw
            engine.draw_to_surface()
            
            # 3. Capture
            # efficient tostring capture
            data = pygame.image.tostring(engine.surface, 'RGB')
            process.stdin.write(data)
            
            frame_count += 1
            
            if frame_count % 60 == 0:
                print(f"\r⏳ Frame {frame_count}/{total_frames} | Score: {engine.gm.kills}", end="")
                
        print(f"\n✅ Done! Recorded {frame_count} frames.")
        
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted.")
    except BrokenPipeError:
        print("\n❌ FFmpeg pipe broken.")
    finally:
        process.stdin.close()
        process.wait()
        pygame.quit()

if __name__ == "__main__":
    main()