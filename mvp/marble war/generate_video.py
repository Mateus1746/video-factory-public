"""
Marble War - Streaming Video Generator
Replaces the slow frame/*.png approach with direct FFmpeg piping.
"""
import os
import sys
import subprocess
import json
from pathlib import Path

# Force headless BEFORE pygame import
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

# Now import game (modular version)
from game import MarbleWar
import config
import pygame

def main():
    print("🎬 Marble War: Streaming HD Generator")
    
    # Setup output
    script_dir = Path(__file__).parent
    output_video = script_dir / "output_render.mp4"
    audio_log = script_dir / "audio_events.json"
    
    # FFmpeg pipe command
    command = [
        'ffmpeg', '-y',
        '-f', 'rawvideo', '-vcodec', 'rawvideo',
        '-s', f'{config.WIDTH}x{config.HEIGHT}',
        '-pix_fmt', 'rgb24', '-r', str(config.FPS),
        '-i', '-',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
        '-pix_fmt', 'yuv420p',
        str(output_video)
    ]
    
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    
    # Create game instance
    game = MarbleWar(headless=True)
    
    print(f"⚔️ Simulating battle...")
    max_frames = config.TOTAL_FRAMES
    
    # Main render loop
    running = True
    while running and game.frame_count < max_frames:
        # Step logic (returns False if game ends)
        running = game.step()
        
        # Render frame (to internal surface)
        game._draw()
        
        # Capture frame
        frame_data = pygame.image.tostring(game.screen, 'RGB')
        try:
            process.stdin.write(frame_data)
        except BrokenPipeError:
            print("❌ FFmpeg pipe broken!")
            break
        
        if game.frame_count % 120 == 0:
            print(f"Frame {game.frame_count}/{max_frames} | Teams alive: {len(set(m.team for m in game.marbles))}")
    
    # Save audio events
    # The game class now has a helper for this, but it saves to 'audio_log.json' by default in original code
    # We want 'audio_events.json' as per this script's convention.
    # game._save_audio_log() saves to "audio_log.json" in the original code.
    # Let's override or just manually save to ensure filename match.
    
    audio_data = [{"t": e.t, "name": e.name, "vol": e.vol} for e in game.audio_events]
    with open(audio_log, 'w') as f:
        json.dump(audio_data, f, indent=2)
    
    # Close pipe
    process.stdin.close()
    process.wait()
    
    print(f"✅ Video rendered: {output_video}")
    print(f"🔊 Audio events logged: {len(audio_data)} events")
    
if __name__ == "__main__":
    main()