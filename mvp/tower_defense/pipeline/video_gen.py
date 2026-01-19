"""
FFmpeg Video Encoder Wrapper
"""
import subprocess
import os
from sim import config

class VideoEncoder:
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.width = config.VIDEO_WIDTH
        self.height = config.VIDEO_HEIGHT
        self.fps = config.FPS
        self.process = None

    def start(self):
        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        command = [
            'ffmpeg',
            '-y', # Overwrite
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-s', f'{self.width}x{self.height}',
            '-pix_fmt', 'rgb24',
            '-r', str(self.fps),
            '-i', '-', # Input from pipe
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'fast',
            '-crf', '18', # High quality
             self.output_path
        ]
        
        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE 
            # Note: stderr=PIPE might fill up buffer if we don't read it. 
            # Safest is usually None or handle generic output.
            # But for debugging let's keep it.
        )
        print(f"Started FFMPEG recording to {self.output_path}")

    def write_frame(self, raw_data):
        if self.process:
            self.process.stdin.write(raw_data)

    def finish(self):
        if self.process:
            self.process.stdin.close()
            self.process.wait()
            print("Video encoding finished.")
