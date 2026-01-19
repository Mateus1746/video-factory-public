import wave
import math
import struct
import os
import random

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
    print(f"Generated {filename}")

def generate_tone(freq, duration, volume=0.5, wave_type='sine', decay=True):
    n_frames = int(AUDIO_RATE * duration)
    samples = []
    for i in range(n_frames):
        t = float(i) / AUDIO_RATE
        
        # Frequency Modulation (optional slide)
        current_freq = freq
        
        if wave_type == 'sine':
            val = math.sin(2 * math.pi * current_freq * t)
        elif wave_type == 'square':
            val = 1.0 if math.sin(2 * math.pi * current_freq * t) > 0 else -1.0
        elif wave_type == 'saw':
            val = 2.0 * (t * current_freq - math.floor(0.5 + t * current_freq))
        elif wave_type == 'noise':
            val = random.uniform(-1, 1)
            
        # Envelope (Volume Decay)
        env = volume
        if decay:
            # Linear decay
            env = volume * (1.0 - (i / n_frames))
            
        samples.append(val * env)
    return samples

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
