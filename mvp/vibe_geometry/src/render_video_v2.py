import pygame
import argparse
import subprocess
import sys
import os

# Add the new module path to sys.path so we can import it
sys.path.append(os.path.join(os.path.dirname(__file__), 'engines', 'pygame'))

from bouncing_ball import Player, WIDTH, HEIGHT, FPS

def render_video(audio_path, json_path, output_path, theme="neon"):
    print(f"🎬 Initializing Renderer: {WIDTH}x{HEIGHT} @ {FPS}fps | Theme: {theme.upper()}")
    
    # Initialize Pygame without a window
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    player = Player(json_path, audio_path, theme_name=theme, preview_mode=False)
    
    # Get duration from JSON
    try:
        duration = player.data['metadata']['duration']
    except:
        duration = 60 # fallback
        
    print(f"⏱️ Duration: {duration}s ({int(duration*FPS)} frames)")

    # FFmpeg Process for Video
    cmd = [
        'ffmpeg',
        '-y', # Overwrite
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', f'{WIDTH}x{HEIGHT}',
        '-pix_fmt', 'rgb24',
        '-r', str(FPS),
        '-i', '-', # Input from pipe
        '-i', audio_path, # Input audio
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '18',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        output_path
    ]
    
    print(f"🔧 FFmpeg Command: {' '.join(cmd)}")
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    
    total_frames = int(duration * FPS)
    
    for frame in range(total_frames):
        t = frame / FPS
        
        player.update(manual_time=t)
        player.draw(screen)
        
        # Capture frame
        data = pygame.image.tostring(screen, 'RGB')
        
        try:
            proc.stdin.write(data)
        except BrokenPipeError:
            print("Error: FFmpeg pipe broken")
            break
            
        if frame % 100 == 0:
            print(f"Rendering: {frame}/{total_frames} ({(frame/total_frames)*100:.1f}%)", end='\r')

    print("\n✅ Rendering finished. Closing FFmpeg...")
    proc.stdin.close()
    proc.wait()
    pygame.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio")
    parser.add_argument("json")
    parser.add_argument("-o", "--output", default="output.mp4")
    parser.add_argument("--theme", default="neon", help="Theme: neon, zen, glitch")
    parser.add_argument("--subdiv", type=int, default=1) # Ignored
    args = parser.parse_args()
    
    render_video(args.audio, args.json, args.output, theme=args.theme)
