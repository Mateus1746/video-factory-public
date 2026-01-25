import wave
import math
import struct
import os
import random
import json

AUDIO_RATE = 44100

def save_wav(filename, samples):
    """Save raw float samples (-1.0 to 1.0) to a WAV file."""
    # Convert to 16-bit PCM
    data = bytearray()
    for s in samples:
        # Clip
        s = max(-1.0, min(1.0, s))
        # Scale to int16
        val = int(s * 32767)
        data.extend(struct.pack('<h', val))
        
    with wave.open(filename, 'w') as f:
        f.setnchannels(1) # Mono
        f.setsampwidth(2) # 2 bytes (16 bit)
        f.setframerate(AUDIO_RATE)
        f.writeframes(data)
    # print(f"Generated {filename}")

def load_wav(filename):
    """Load WAV file and return list of float samples."""
    with wave.open(filename, 'r') as f:
        n_frames = f.getnframes()
        data = f.readframes(n_frames)
        # Unpack int16
        raw_samples = struct.unpack(f'<{n_frames}h', data)
        # Convert to float
        return [s / 32767.0 for s in raw_samples]

def generate_sync_audio(events_json, output_file, total_duration):
    """Generate a synchronized audio track based on simulation events."""
    with open(events_json, 'r') as f:
        events = json.load(f)
    
    # Pre-generate or ensure assets exist
    generate_assets()
    
    # Map event types to WAV files
    sound_map = {
        "bounce_gain": "assets/bounce_gain.wav",
        "bounce_loss": "assets/bounce_loss.wav",
        "levelup": "assets/levelup.wav",
        "win": "assets/win.wav",
        "item_collect": "assets/collect.wav",
        "chaos_trigger": "assets/alert.wav",
        "pvp_collision": "assets/bounce_loss.wav" # Fallback
    }
    
    # Load all sounds into memory for performance
    loaded_sounds = {}
    for ev_type, path in sound_map.items():
        if os.path.exists(path):
            loaded_sounds[ev_type] = load_wav(path)
    
    # Final buffer
    total_samples = int(AUDIO_RATE * (total_duration + 2.0)) # Add buffer
    final_buffer = [0.0] * total_samples
    
    # Mix sounds at event times
    for ev in events:
        ev_type = ev["type"]
        ev_time = ev["time"]
        
        if ev_type in loaded_sounds:
            sound_data = loaded_sounds[ev_type]
            start_idx = int(ev_time * AUDIO_RATE)
            
            # Mix in
            for i in range(len(sound_data)):
                idx = start_idx + i
                if idx < total_samples:
                    # Simple additive mixing
                    final_buffer[idx] += sound_data[i]
    
    # Normalize if needed to avoid clipping
    max_val = max(abs(s) for s in final_buffer) if final_buffer else 0
    if max_val > 1.0:
        final_buffer = [s / max_val for s in final_buffer]
        
    save_wav(output_file, final_buffer)
    print(f"🎵 Sync audio generated: {output_file} ({len(events)} events)")

def generate_assets():
    if not os.path.exists("assets"):
        os.makedirs("assets")

    # 1. Bounce (High Pitch Ping - Positive)
    # Sine wave sliding down slightly
    samples = []
    duration = 0.15
    for i in range(int(AUDIO_RATE * duration)):
        t = i / AUDIO_RATE
        freq = 800 - (t * 2000) # Slide down
        val = math.sin(2 * math.pi * freq * t) * 0.5 * (1 - t/duration)
        samples.append(val)
    save_wav("assets/bounce_gain.wav", samples)

    # 2. Bounce (Low Thud - Negative)
    samples = []
    duration = 0.2
    for i in range(int(AUDIO_RATE * duration)):
        t = i / AUDIO_RATE
        freq = 150 - (t * 400) # Deep slide
        val = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0 # Square ish
        val *= 0.4 * (1 - t/duration)
        samples.append(val)
    save_wav("assets/bounce_loss.wav", samples)

    # 3. Level Up (Power Up sound)
    samples = []
    duration = 0.4
    for i in range(int(AUDIO_RATE * duration)):
        t = i / AUDIO_RATE
        # Arpeggio effect
        if t < 0.1: freq = 440
        elif t < 0.2: freq = 554
        elif t < 0.3: freq = 659
        else: freq = 880
        
        val = math.sin(2 * math.pi * freq * t) * 0.5
        samples.append(val)
    save_wav("assets/levelup.wav", samples)

    # 4. Win (Fanfare)
    samples = []
    duration = 1.5
    for i in range(int(AUDIO_RATE * duration)):
        t = i / AUDIO_RATE
        freq = 440 + math.sin(t * 20) * 10 # Vibrato
        if t > 0.2: freq = 554
        if t > 0.4: freq = 659
        if t > 0.8: freq = 880
        
        val = math.sin(2 * math.pi * freq * t) * 0.4 * (1 - t/duration)
        samples.append(val)
    save_wav("assets/win.wav", samples)

    # 5. Chaos Alert (Siren / Alarm)
    samples = []
    duration = 0.5
    for i in range(int(AUDIO_RATE * duration)):
        t = i / AUDIO_RATE
        # Fast wobble
        mod = math.sin(2 * math.pi * 15 * t)
        freq = 600 + (mod * 200)
        
        # Sawtooth-ish
        val = 2.0 * (t * freq - math.floor(0.5 + t * freq))
        val *= 0.4 * (1 - t/duration)
        samples.append(val)
    save_wav("assets/alert.wav", samples)

    # 6. Collect Item (Ding)
    samples = []
    duration = 0.1
    for i in range(int(AUDIO_RATE * duration)):
        t = i / AUDIO_RATE
        freq = 1200 + (t * 500) # Quick chirp
        val = math.sin(2 * math.pi * freq * t) * 0.3 * (1 - t/duration)
        samples.append(val)
    save_wav("assets/collect.wav", samples)

if __name__ == "__main__":
    generate_assets()