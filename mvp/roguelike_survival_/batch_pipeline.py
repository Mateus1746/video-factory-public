import os
import sys

# --- HEADLESS CONFIGURATION ---
# Must be set before importing pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import random
import numpy as np
import pygame  # Import pygame after setting env vars
import imageio # Efficient video writing

# Initialize Pygame explicitly
pygame.init()
pygame.font.init()
try:
    pygame.mixer.init()
except Exception as e:
    print(f"Warning: Audio mixer init failed (expected in headless): {e}")

from moviepy import AudioFileClip, VideoFileClip
from src.render_engine import RenderEngine
from src.config import *

def generate_simulation(index, output_dir):
    print(f"\n>>> Starting Simulation {index+1}...")
    
    # Internal resolution 1080x1920
    width, height = SCREEN_W, SCREEN_H
    engine = RenderEngine(width, height)
    
    fps = 60
    duration_limit = 60 # Maximum seconds for Shorts
    dt = 1.0 / fps
    
    # Temporary video path to save frames as they are generated
    temp_video_path = os.path.join(output_dir, f"temp-neon-survivor-{index+1}.mp4")
    
    # Initialize ImageIO writer (streams to disk, saving RAM)
    writer = imageio.get_writer(
        temp_video_path, 
        fps=fps, 
        codec='libx264', 
        quality=None, 
        bitrate='8000k', 
        pixelformat='yuv420p'
    )
    
    # Simulation Loop
    step = 0
    max_steps = duration_limit * fps
    
    try:
        while step < max_steps:
            engine.step(dt)
            
            # Capture frame
            frame = engine.render()
            writer.append_data(frame)
            
            step += 1
            if step % 300 == 0:
                print(f"   Simulated {step//60}s...")
                
            if engine.game_over or engine.victory:
                # FIXED ENDING: Always exactly 2 seconds (120 frames) of final screen
                print(f"   End condition met. Capturing 2s finale...")
                final_frame = engine.render()
                for _ in range(fps * 2):
                    writer.append_data(final_frame)
                break
    finally:
        writer.close()

    print(f"   Encoding Audio & Finalizing...")
    
    # Load the temp video to add audio
    clip = VideoFileClip(temp_video_path)
    
    # Add Audio
    music_path = random.choice(PATH_MUSIC)
    if os.path.exists(music_path):
        try:
            audio = AudioFileClip(music_path)
            # Loop audio if it's shorter than the video
            if audio.duration < clip.duration:
                audio = audio.loop(duration=clip.duration)
            else:
                audio = audio.subclip(0, clip.duration)
                
            audio = audio.volumex(0.05) # Subtle as requested
            clip = clip.set_audio(audio)
        except Exception as e:
            print(f"   Warning: Could not process audio: {e}")

    # Save Output to specific directory
    output_filename = os.path.join(output_dir, f"neon-survivor-roguelike-survival-gameplay-{index+1}.mp4")
    
    # Write final video (re-encoding needed to mix audio, but input is stream from disk)
    # Using 'fast' preset to speed up the second pass
    clip.write_videofile(output_filename, codec="libx264", fps=fps, audio_codec="aac", bitrate="8000k", preset="fast")
    
    clip.close()
    
    # Cleanup temp file
    if os.path.exists(temp_video_path):
        os.remove(temp_video_path)
    
    print(f">>> Finished! Saved to {output_filename}")

def main():
    if len(sys.argv) < 2:
        print("Usage: uv run batch_generator.py <number_of_simulations>")
        return

    try:
        count = int(sys.argv[1])
    except ValueError:
        print("Error: Argument must be an integer.")
        return

    # Create output directory
    output_dir = "batch_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Neon Survivor Batch Renderer | Task: {count} videos | Output: ./{output_dir}")
    
    for i in range(count):
        generate_simulation(i, output_dir)

if __name__ == "__main__":
    main()