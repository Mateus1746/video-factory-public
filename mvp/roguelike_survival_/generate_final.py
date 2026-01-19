import os
import random
from moviepy.video.VideoClip import VideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from src.render_engine import RenderEngine
from src.config import SCREEN_W, SCREEN_H

# CONFIG
DURATION = 40  # Compact, high-energy Short
FPS = 60
OUTPUT_FILE = "final_render_1080p.mp4"
AUDIO_DIR = "assets/audio/music"

print(f"Initializing FINAL Render ({SCREEN_W}x{SCREEN_H} @ {FPS}fps)... This may take a while.")

engine = RenderEngine(SCREEN_W, SCREEN_H)

def make_frame(t):
    dt = 1.0 / FPS
    # Only step if we haven't reached the end state logic inside engine
    # The engine.step() already checks for game_over/victory and freezes, so we just call it.
    engine.step(dt)
    return engine.render()

clip = VideoClip(make_frame, duration=DURATION)

# AUDIO HANDLING
music_files = [f for f in os.listdir(AUDIO_DIR) if f.endswith(".mp3")]
if music_files:
    chosen_music = random.choice(music_files)
    print(f"Adding Soundtrack: {chosen_music}")
    
    music_path = os.path.join(AUDIO_DIR, chosen_music)
    audio = AudioFileClip(music_path)
    
    # Loop if shorter than duration
    if audio.duration < DURATION:
        audio = audio.loop(duration=DURATION)
    else:
        audio = audio.subclip(0, DURATION)
        
    # Fade out last 2 seconds
    try:
        audio = audio_fadeout(audio, 2.0)
    except Exception as e:
        print(f"Could not apply audio fadeout: {e}")
        
    clip = clip.set_audio(audio)
else:
    print("WARNING: No music found in assets/audio/music")

# High quality encoding
clip.write_videofile(OUTPUT_FILE, fps=FPS, codec="libx264", bitrate="8000k", preset="medium", audio_codec="aac")
print(f"Done! Saved to {OUTPUT_FILE}")