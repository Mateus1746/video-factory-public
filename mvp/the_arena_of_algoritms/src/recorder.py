import subprocess
import pygame
from .config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

class VideoRecorder:
    def __init__(self, output_file="simulation.mp4"):
        self.output_file = output_file
        self.process = None
        
    def start(self):
        # Start ffmpeg process
        command = [
            'ffmpeg',
            '-y', # Overwrite output file
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-s', f'{SCREEN_WIDTH}x{SCREEN_HEIGHT}',
            '-pix_fmt', 'rgb24',
            '-r', str(FPS),
            '-i', '-', # Input from pipe
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'ultrafast', # Fast encoding for realtime-ish capture
            '-crf', '23',
            self.output_file
        ]
        
        try:
            self.process = subprocess.Popen(command, stdin=subprocess.PIPE)
            print(f"Recording started: {self.output_file}")
        except FileNotFoundError:
            print("Error: ffmpeg not found. Video recording disabled.")
            self.process = None
        
    def capture_frame(self, surface):
        if self.process:
            try:
                # Get raw string data from surface (fast)
                # Ensure surface is the correct size
                if surface.get_width() != SCREEN_WIDTH or surface.get_height() != SCREEN_HEIGHT:
                    # Should not happen if engine is correct, but safe fallback logic could be added
                    pass
                    
                data = pygame.image.tostring(surface, 'RGB')
                self.process.stdin.write(data)
            except BrokenPipeError:
                print("Error: ffmpeg pipe broken. Stopping recording.")
                self.stop()
            except Exception as e:
                print(f"Error capturing frame: {e}")
            
    def stop(self):
        if self.process:
            if self.process.stdin:
                self.process.stdin.close()
            self.process.wait()
            self.process = None
            print("Recording stopped.")
