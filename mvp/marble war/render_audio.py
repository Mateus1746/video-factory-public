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
        with open("audio_log.json", "r") as f:
            events = json.load(f)
    except FileNotFoundError:
        print("Error: audio_log.json not found. Run simulation first.")
        return

    # 2. Asset Mapping (Normalized 48kHz)
    sound_files = {
        "collision": "assets/music/collision_48.wav",
        "powerup": "assets/music/powerup_48.wav",
        "elimination": "assets/music/elimination_48.wav",
        "tictoc": "assets/music/tictoc_48.wav"
    }
    bg_file = "assets/music/bg_48.wav"

    # 3. Load BG and Initialize Final Track
    samplerate, bg_data = wavfile.read(bg_file)
    if bg_data.dtype != np.int16:
        bg_data = (bg_data * 32767).astype(np.int16)
    
    # Calculate duration based on frames
    frames = list(Path("frames").glob("*.png"))
    if frames:
        max_t = len(frames) / config.FPS
        print(f"Total frames: {len(frames)} -> Duration: {max_t:.2f}s")
    elif events:
        max_t = max(e["t"] for e in events) + 2.0 # buffer for last sound
    else:
        max_t = 15.0 # Default
        
    num_samples = int(max_t * samplerate)
    # Trim or loop BG if necessary
    if len(bg_data) < num_samples:
        # Loop BG
        repeats = (num_samples // len(bg_data)) + 1
        bg_track = np.tile(bg_data, (repeats, 1))[:num_samples]
    else:
        bg_track = bg_data[:num_samples]

    # Initialize SFX track (float64 for mixing precision)
    sfx_track = np.zeros((num_samples, 2), dtype=np.float64)

    # 4. Load SFX Kernels
    sfx_kernels = {}
    for name, path in sound_files.items():
        if Path(path).exists():
            sr, data = wavfile.read(path)
            if data.dtype != np.int16:
                data = (data * 32767).astype(np.int16)
            # Handle mono SFX
            if len(data.shape) == 1:
                data = np.stack([data, data], axis=1)
            sfx_kernels[name] = data
        else:
            print(f"Warning: SFX asset missing: {path}")

    # 5. Additive Synthesis (Mixing)
    print(f"Mixing {len(events)} audio events...")
    for evt in events:
        name = evt["name"]
        t = evt["t"]
        vol = evt["vol"]
        
        if name in sfx_kernels:
            kernel = sfx_kernels[name]
            # Nexus: Variação de Pitch para ASMR
            pitch_factor = random.uniform(0.9, 1.1)
            if pitch_factor != 1.0:
                indices = np.round(np.arange(0, len(kernel), pitch_factor)).astype(int)
                indices = indices[indices < len(kernel)]
                kernel = kernel[indices]
            start_sample = int(t * samplerate)
            end_sample = start_sample + len(kernel)
            
            # Clip if goes beyond duration
            if start_sample >= num_samples:
                continue
            if end_sample > num_samples:
                kernel = kernel[:num_samples - start_sample]
                end_sample = num_samples
                
            sfx_track[start_sample:end_sample] += kernel.astype(np.float64) * vol

    # 6. Mastering (Combine and Normalize)
    # Background volume reduction
    final_track = (bg_track.astype(np.float64) * 0.4) + sfx_track
    
    # Prevent clipping
    max_val = np.max(np.abs(final_track))
    if max_val > 32767:
        print(f"Mastering: Normalizing (peak: {max_val})")
        final_track = (final_track / max_val) * 32767

    final_audio = final_track.astype(np.int16)
    
    # 7. Export
    wavfile.write("final_audio.wav", samplerate, final_audio)
    print("Success: final_audio.wav generated.")

    # 8. Mux Video and Audio
    print("Muxing video and audio with FFmpeg...")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", "60",
        "-i", "frames/frame_%04d.png",
        "-i", "final_audio.wav",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "video_with_audio.mp4"
    ]
    subprocess.run(cmd)
    print("Done! Result saved as video_with_audio.mp4")

if __name__ == "__main__":
    render_audio()
