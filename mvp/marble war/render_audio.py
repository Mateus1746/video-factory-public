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

    # 2. Asset Mapping (from config)
    sound_files = config.AUDIO_PATHS.copy()
    bg_file = sound_files.pop("bg", "assets/music/bg_48.wav")

    # 3. Load BG and Initialize Final Track
    try:
        samplerate, bg_data = wavfile.read(bg_file)
        if bg_data.dtype != np.int16:
            bg_data = (bg_data * 32767).astype(np.int16)
    except FileNotFoundError:
        print(f"Warning: BG file {bg_file} not found. Creating silent BG.")
        samplerate = 48000
        bg_data = np.zeros(samplerate * 15, dtype=np.int16)
    
    # Calculate duration based on video file or events
    max_t = 15.0 # Default
    if Path("output_render.mp4").exists():
        # Get duration using ffprobe
        try:
            res = subprocess.run([
                "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", "output_render.mp4"
            ], capture_output=True, text=True)
            max_t = float(res.stdout.strip())
            print(f"Video duration: {max_t:.2f}s")
        except:
            print("Could not probe video duration, using events.")
            if events:
                max_t = max(e["t"] for e in events) + 2.0
    elif events:
        max_t = max(e["t"] for e in events) + 2.0 # buffer for last sound
        
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
    if len(bg_track.shape) == 1:
        bg_track = np.stack([bg_track, bg_track], axis=1)
        
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
    try:
        subprocess.run(cmd, check=True)
        print("Done! Result saved as final_with_audio.mp4")
    except subprocess.CalledProcessError as e:
        print(f"❌ Muxing failed: {e}")

if __name__ == "__main__":
    render_audio()