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
    game = MarbleWar()
    
    print(f"⚔️ Simulating battle...")
    frame_count = 0
    max_frames = config.TOTAL_FRAMES
    
    # Main render loop
    while frame_count < max_frames and not game.winner_team:
        # Update game
        game._update_marbles()
        game._handle_powerups()
        game._update_projectiles()
        game._update_bomb()
        game._remove_entities()
        game._update_grid()
        game._check_victory()
        
        # Update physics
        game.space.step(config.TIMESTEP)
        
        # Update effects
        game.particles.update()
        for exp in game.explosions[:]:
            if not exp.update():
                game.explosions.remove(exp)
        
        # Render frame
        game._draw()
        
        # Capture frame
        import pygame
        frame_data = pygame.image.tostring(game.screen, 'RGB')
        process.stdin.write(frame_data)
        
        frame_count += 1
        game.frame_count = frame_count
        
        if frame_count % 120 == 0:
            print(f"Frame {frame_count}/{max_frames} | Teams alive: {len(set(m.team for m in game.marbles))}")
    
    # Save audio events
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
