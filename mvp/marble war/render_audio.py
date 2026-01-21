import random
import json
import numpy as np
from scipy.io import wavfile
import subprocess
from pathlib import Path
import config

def render_audio():
    print("--- Spec_Harmony_Waves: Harmonic Reconstruction Kernel ---")
    
    # 1. Load Audio Log
    try:
        with open("audio_events.json", "r") as f:
            events = json.load(f)
    except FileNotFoundError:
        print("Error: audio_events.json not found. Run simulation first.")
        return

    # ... (skipping to muxing logic) ...

    # 7. Export
    wavfile.write("final_audio.wav", samplerate, final_audio)
    print("Success: final_audio.wav generated.")

    # 8. Mux Video and Audio
    print("Muxing output_render.mp4 and final_audio.wav...")
    cmd = [
        "ffmpeg", "-y",
        "-i", "output_render.mp4",
        "-i", "final_audio.wav",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "final_with_audio.mp4"
    ]
    subprocess.run(cmd, check=True)
    print("Done! Result saved as final_with_audio.mp4")

if __name__ == "__main__":
    render_audio()
