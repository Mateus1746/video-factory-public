import pygame
import numpy as np
import math
import wave
import os
from .config import *

# --- Audio Configuration ---
try:
    pygame.mixer.pre_init(44100, -16, 1, 1024)
    pygame.mixer.init()
    pygame.mixer.set_num_channels(32)
except pygame.error:
    print("⚠️ Áudio Device não encontrado. Usando Dummy Driver.")
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    pygame.mixer.pre_init(44100, -16, 1, 1024)
    pygame.mixer.init()

SAMPLE_RATE = 44100
SOUND_CACHE = {}

PIANO_FREQUENCIES = [
    261.63, # C4
    293.66, # D4
    329.63, # E4
    349.23, # F4
    392.00, # G4
    440.00, # A4
    493.88, # B4
    523.25  # C5
]

class AudioRecorder:
    def __init__(self, sample_rate=SAMPLE_RATE):
        self.sample_rate = sample_rate
        self.events = []
        self.is_recording = EXPORT_MODE
        self.current_time = 0.0
        
    def add_samples(self, samples, start_time):
        if not self.is_recording: return
        self.events.append((samples, start_time))
        # Log periodically to avoid spam
        if len(self.events) % 1000 == 0:
            from .utils import logger
            logger.info(f"Audio Buffer: {len(self.events)} events, current time: {round(start_time, 2)}s")

    def update_time(self, dt):
        self.current_time += dt

    def save(self, filename="simulation_audio.wav"):
        if not self.events: 
            print("No audio events to save.")
            return
        
        print(f"Mixing {len(self.events)} audio events...")
        # Duration is MAX(last_event_end, current_simulation_time)
        last_event_end = max(start + len(s)/self.sample_rate for s, start in self.events)
        final_duration = max(last_event_end, self.current_time)
        
        total_len = int(final_duration * self.sample_rate) + 1000 # Add small buffer
        
        mixed = np.zeros(total_len, dtype=np.float32)
        for samples, start_time in self.events:
            start_idx = int(start_time * self.sample_rate)
            if start_idx < 0: continue
            end_idx = start_idx + len(samples)
            if end_idx > total_len:
                # Pad mixed if necessary
                new_mixed = np.zeros(end_idx + 44100, dtype=np.float32)
                new_mixed[:len(mixed)] = mixed
                mixed = new_mixed
                total_len = len(mixed)
            
            mixed[start_idx:end_idx] += samples.astype(np.float32)
            
        # Normalize to prevent clipping, but keep some headroom
        max_val = np.max(np.abs(mixed))
        if max_val > 0:
            mixed = (mixed / max_val) * 30000
            
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(mixed.astype(np.int16).tobytes())
        print(f"Audio saved to {filename}")

RECORDING_MANAGER = AudioRecorder()

def generate_wave(frequency, duration, wave_type='sine', amplitude=0.09):
    key = (int(frequency), round(duration, 3), wave_type, amplitude)
    
    num_samples = int(duration * SAMPLE_RATE)
    time = np.linspace(0, duration, num_samples, endpoint=False)
    
    if wave_type == 'sine':
        waveform = amplitude * 32767 * np.sin(2 * np.pi * frequency * time)
    elif wave_type == 'square':
        waveform = amplitude * 32767 * np.sign(np.sin(2 * np.pi * frequency * time))
    elif wave_type == 'sawtooth':
        waveform = amplitude * 32767 * (2 * (frequency * time - np.floor(0.5 + frequency * time)))
    else:
        waveform = amplitude * 32767 * np.sin(2 * np.pi * frequency * time)

    attack_time = 0.01
    release_time = 0.05
    attack_samples = int(attack_time * SAMPLE_RATE)
    release_samples = int(release_time * SAMPLE_RATE)
    
    envelope = np.ones(num_samples)
    if attack_samples > 0 and num_samples > attack_samples:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    if release_samples > 0 and num_samples > release_samples:
        envelope[-release_samples:] = np.linspace(1, 0, release_samples)
    
    waveform *= envelope
    samples = waveform.astype(np.int16)
    
    # Cache the Sound object for pygame
    if key in SOUND_CACHE:
        sound = SOUND_CACHE[key]
    else:
        sound = pygame.sndarray.make_sound(samples)
        SOUND_CACHE[key] = sound
        
    # Always register for recording
    RECORDING_MANAGER.add_samples(samples, RECORDING_MANAGER.current_time)
    
    return sound

class SoundManager:
    def __init__(self):
        self.bpm = 140
        self.beat_duration = 60 / self.bpm
        self.timer = 0
        self.beat_count = 0
        self.base_freq = 55  # A1
        self.scale = [1.0, 1.189, 1.334, 1.498, 1.782] # Minor pentatonic ratios
        
    def play_sfx(self, frequency, duration=0.1, wave_type='sine', amplitude=0.09):
        sound = generate_wave(frequency, duration, wave_type, amplitude)
        sound.play()

    def update(self, dt):
        RECORDING_MANAGER.update_time(dt)
        self.timer += dt
        if self.timer >= self.beat_duration:
            self.timer -= self.beat_duration
            self.on_beat()
            self.beat_count += 1

    def on_beat(self):
        # Kick drum
        if self.beat_count % 2 == 0:
            self.play_kick()
        
        # Hi-hat
        if self.beat_count % 4 == 2:
            self.play_hihat()

        # Bassline
        if self.beat_count % 8 < 6:
            note_idx = (self.beat_count % 4)
            freq = self.base_freq * self.scale[note_idx % len(self.scale)]
            self.play_sfx(freq, self.beat_duration * 0.6, 'sawtooth', 0.07)

    def play_kick(self):
        duration = 0.12
        num_samples = int(duration * SAMPLE_RATE)
        time = np.linspace(0, duration, num_samples, endpoint=False)
        freq_sweep = np.linspace(120, 40, num_samples)
        waveform = 0.35 * 32767 * np.sin(2 * np.pi * freq_sweep * time) # Reduced from 0.6
        envelope = np.exp(-12 * time)
        samples = (waveform * envelope).astype(np.int16)
        
        sound = pygame.sndarray.make_sound(samples)
        sound.play()
        RECORDING_MANAGER.add_samples(samples, RECORDING_MANAGER.current_time)

    def play_hihat(self):
        duration = 0.04
        num_samples = int(duration * SAMPLE_RATE)
        waveform = 0.09 * 32767 * (np.random.rand(num_samples) * 2 - 1) # Reduced from 0.15
        envelope = np.linspace(1, 0, num_samples) ** 3
        samples = (waveform * envelope).astype(np.int16)
        
        sound = pygame.sndarray.make_sound(samples)
        sound.play()
        RECORDING_MANAGER.add_samples(samples, RECORDING_MANAGER.current_time)

def generate_note_sound(frequency, duration=0.1):
    return generate_wave(frequency, duration, 'sine', 0.07) # Reduced from 0.12
