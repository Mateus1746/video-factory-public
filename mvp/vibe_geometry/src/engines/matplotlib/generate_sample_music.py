import numpy as np
from scipy.io import wavfile

SAMPLE_RATE = 44100
DURATION = 20
BPM = 120
BEAT_DUR = 60 / BPM

def generate_kick(duration=0.1):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    # Pitch drop kick
    freq = np.linspace(150, 40, len(t))
    wave = np.sin(2 * np.pi * freq * t) * np.exp(-10 * t)
    return wave

def generate_snare(duration=0.1):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    # Noise with low-pass (simple white noise)
    noise = np.random.uniform(-1, 1, len(t))
    envelope = np.exp(-15 * t)
    return noise * envelope

def create_sample_track():
    total_samples = int(SAMPLE_RATE * DURATION)
    audio = np.zeros(total_samples)
    
    kick = generate_kick()
    snare = generate_snare()
    
    # Simple Kick-Snare-Kick-Snare at 120 BPM
    for b in range(int(DURATION / BEAT_DUR)):
        t_start = b * BEAT_DUR
        idx = int(t_start * SAMPLE_RATE)
        
        if b % 2 == 0:
            # Kick on 1 and 3
            audio[idx:idx+len(kick)] += kick
        else:
            # Snare on 2 and 4
            audio[idx:idx+len(snare)] += snare * 0.7
            
    # Normalize
    audio /= np.max(np.abs(audio))
    wavfile.write("music.wav", SAMPLE_RATE, (audio * 32767).astype(np.int16))
    print("Sample music generated: music.wav (120 BPM)")

if __name__ == "__main__":
    create_sample_track()
