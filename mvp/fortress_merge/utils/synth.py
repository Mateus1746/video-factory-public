import wave
import math
import struct
import random
import os

SFX_DIR = "assets/sfx"

def save_wav(filename, data, sample_rate=44100):
    path = os.path.join(SFX_DIR, filename)
    with wave.open(path, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(data)
    print(f"Generated: {path}")

def generate_tone(freq, duration, vol=0.5, type='sine', decay=True):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    data = bytearray()
    
    for i in range(n_samples):
        t = i / sample_rate
        if type == 'sine':
            value = math.sin(2 * math.pi * freq * t)
        elif type == 'square':
            value = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
        elif type == 'noise':
            value = random.uniform(-1, 1)
        elif type == 'saw':
            value = 2 * (t * freq - math.floor(0.5 + t * freq))
        
        # Envelope
        envelope = 1.0
        if decay:
            envelope = max(0, 1 - (i / n_samples))
        
        sample = int(value * vol * envelope * 32767)
        data += struct.pack('<h', sample)
    return data

def generate_sweep(start_freq, end_freq, duration, vol=0.5):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    data = bytearray()
    
    for i in range(n_samples):
        progress = i / n_samples
        freq = start_freq + (end_freq - start_freq) * progress
        t = i / sample_rate
        # Frequency integration (approximate)
        phase = 2 * math.pi * (start_freq * t + 0.5 * (end_freq - start_freq) * t**2 / duration)
        
        value = math.sin(phase)
        sample = int(value * vol * (1 - progress) * 32767)
        data += struct.pack('<h', sample)
    return data

if __name__ == "__main__":
    # Shoot: High pitch fast decay
    save_wav("shoot.wav", generate_tone(880, 0.1, vol=0.3, type='square'))
    
    # Hit: Low noise
    save_wav("hit.wav", generate_tone(100, 0.1, vol=0.4, type='noise'))
    
    # Explosion: Longer noise
    save_wav("explosion.wav", generate_tone(50, 0.3, vol=0.5, type='noise'))
    
    # Merge: Rising Sweep (Magical)
    save_wav("merge.wav", generate_sweep(400, 1200, 0.3, vol=0.4))
    
    # Buy: High coin sound
    save_wav("buy.wav", generate_tone(1500, 0.15, vol=0.3, type='sine'))
    
    # Game Over: Descending Sweep
    save_wav("gameover.wav", generate_sweep(300, 50, 1.0, vol=0.5))
