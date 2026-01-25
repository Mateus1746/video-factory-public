import os
import sys
import subprocess
from config import WIDTH, HEIGHT, FPS
from pipeline.audio_mixer import AudioMixer

def run_step(step_name, command):
    print(f"🔹 [{step_name}] Running...")
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ [{step_name}] Failed: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return False

def compile_video(frames_path, output_path):
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(frames_path, "frame_%05d.jpg"),
        "-vf", f"scale={WIDTH}:{HEIGHT}",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        output_path
    ]
    return run_step("Compile Video", cmd)

def mix_audio(events_path, video_path, theme):
    return AudioMixer.mix(events_path, video_path, FPS, theme)
