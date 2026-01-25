"""
Video Generator Module.
Runs the game simulation and pipes video frames to FFmpeg.
"""

import os
import sys
import subprocess
import pygame
from pathlib import Path
from typing import List, Dict

# Set headless before anything else
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from game import MarbleWar
import config

class VideoGenerator:
    def __init__(self):
        print("🎥 Initializing Video Generator...")
        self.root_dir = Path(__file__).parent
        
    def render(self, output_path: Path) -> List[Dict]:
        """
        Runs the simulation and generates the video file.
        Returns: List of audio events.
        """
        print(f"🎬 Generating Video: {output_path.name}")
        
        # 1. Setup FFmpeg Pipe
        command = [
            'ffmpeg', '-y', '-v', 'error', # Less verbosity
            '-f', 'rawvideo', '-vcodec', 'rawvideo',
            '-s', f'{config.WIDTH}x{config.HEIGHT}',
            '-pix_fmt', 'rgb24', '-r', str(config.FPS),
            '-i', '-',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-pix_fmt', 'yuv420p',
            str(output_path)
        ]
        
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        
        # 2. Init Game (Headless)
        # We re-init for every video to ensure clean state (Chaos RNG)
        game = MarbleWar(headless=True)
        
        # 3. Main Loop
        max_frames = config.TOTAL_FRAMES
        
        try:
            while game.frame_count < max_frames:
                # Step logic
                running = game.step()
                if not running:
                    break
                
                # Render
                game._draw()
                
                # Capture frame
                frame_data = pygame.image.tostring(game.screen, 'RGB')
                process.stdin.write(frame_data)
                
                # Progress
                if game.frame_count % 120 == 0:
                    pct = (game.frame_count / max_frames) * 100
                    # Print in place to avoid log spam
                    sys.stdout.write(f"\r⏳ Progress: {pct:.1f}% ({game.frame_count}/{max_frames}) | Mode: {game.state.game_mode.name}")
                    sys.stdout.flush()
                    
        except BrokenPipeError:
            print("\n❌ FFmpeg pipe broken!")
        finally:
            print("") # Newline
            if process.stdin:
                process.stdin.close()
            process.wait()
            
            # Important: Quit pygame to free resources, 
            # but usually MarbleWar.run() handles it. Here we handle it.
            pygame.quit()
            
        print(f"✅ Video Generation Complete: {len(game.audio_events)} audio events captured.")
        
        # Convert internal AudioEvents to list of dicts for renderer
        return [{"t": e.t, "name": e.name, "vol": e.vol, "x": e.x} for e in game.audio_events]
