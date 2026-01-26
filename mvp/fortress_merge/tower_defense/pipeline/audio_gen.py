"""
Audio Generation - High Quality Synth
Replaces noise-based SFX with clean synthesized tones (Lasers, Bass Kicks).
"""
import numpy as np
try:
    from moviepy.editor import AudioArrayClip, VideoFileClip
except ImportError:
    try:
        from moviepy.audio.AudioClip import AudioArrayClip
        from moviepy.video.io.VideoFileClip import VideoFileClip
    except ImportError:
        try:
            from moviepy.audio.AudioClip import AudioArrayClip
            from moviepy.video.VideoClip import VideoFileClip
        except ImportError:
            # Fallback for v2.0+
            from moviepy.video.io.VideoFileClip import VideoFileClip
            from moviepy.audio.AudioClip import AudioArrayClip

class AudioEngine:
    def __init__(self, fps=44100):
        self.sample_rate = fps

    def _generate_sine(self, duration, freq_start, freq_end=None, volume=0.5):
        """Generates a clean sine wave with optional frequency sweep."""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        if freq_end:
            # Exponential slide for that "Pew" sound
            freq = freq_start * (freq_end / freq_start)**(t / duration)
        else:
            freq = freq_start
            
        # Integrate frequency to get phase
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        wave = np.sin(phase)
        
        # Envelope (Fade out)
        envelope = np.exp(-5 * t / duration)
        wave *= envelope
        
        # Stereo
        return np.vstack((wave, wave)).T * volume

    def create_shot_sound(self):
        """Laser 'Pew' sound (High to Low frequency). Clean, no static."""
        # 0.1s duration, 600Hz -> 100Hz sweep
        return self._generate_sine(0.1, 600, 100, volume=0.3)

    def create_rocket_sound(self):
        """Lower pitched 'Whoosh'."""
        return self._generate_sine(0.3, 300, 50, volume=0.4)

    def create_coin_sound(self):
        """High pitched 'Ding' (Constant freq)."""
        return self._generate_sine(0.1, 1500, 1500, volume=0.2) # Quick high beep

    def create_death_sound(self):
        """Quick bass thud."""
        return self._generate_sine(0.15, 150, 50, volume=0.4)
        
    def create_explosion_sound(self):
        """Deep rumble."""
        return self._generate_sine(0.4, 100, 20, volume=0.5)

    def generate_soundtrack(self, total_duration):
        """
        Generates a clean Synthwave beat.
        Structure: Kick Drum (Bass) + High Arp (Melody)
        """
        bpm = 120
        beat_dur = 60 / bpm
        total_samples = int(self.sample_rate * total_duration)
        track = np.zeros((total_samples, 2))
        
        # 1. Kick Drum (The Beat) - Pure Sine Sweep 150Hz -> 40Hz
        t_kick = np.linspace(0, 0.2, int(self.sample_rate * 0.2), False)
        # Pitch envelope
        f_kick = 150 * (40 / 150)**(t_kick / 0.2)
        phase_kick = 2 * np.pi * np.cumsum(f_kick) / self.sample_rate
        kick_wave = np.sin(phase_kick) * np.exp(-10 * t_kick) * 0.6
        kick_stereo = np.vstack((kick_wave, kick_wave)).T

        # 2. Hi-Hat (Short high frequency blip) - replacing noise hat
        t_hat = np.linspace(0, 0.05, int(self.sample_rate * 0.05), False)
        hat_wave = np.sin(2 * np.pi * 8000 * t_hat) * np.exp(-50 * t_hat) * 0.15
        hat_stereo = np.vstack((hat_wave, hat_wave)).T

        current_sample = 0
        beat = 0
        
        while current_sample < total_samples:
            # Kick on 1, 2, 3, 4
            if beat % 1 == 0:
                end = min(current_sample + len(kick_stereo), total_samples)
                track[current_sample:end] += kick_stereo[:end-current_sample]
            
            # Hat on off-beats (0.5, 1.5...)
            else:
                end = min(current_sample + len(hat_stereo), total_samples)
                track[current_sample:end] += hat_stereo[:end-current_sample]
            
            # Simple Bass/Arp Tone (Square-ish wave approximated)
            # Note sequence: A (220) -> C (261) -> E (329)
            scale = [220, 261, 329, 261]
            freq = scale[int(beat % 4)]
            
            # Generate a 1/8th note tone
            note_dur = beat_dur / 2
            t_note = np.linspace(0, note_dur, int(self.sample_rate * note_dur), False)
            # Add some harmonics for "synth" sound
            note_wave = (np.sin(2 * np.pi * freq * t_note) + 
                         0.5 * np.sin(2 * np.pi * freq * 2 * t_note)) * 0.1
            note_stereo = np.vstack((note_wave, note_wave)).T
            
            n_start = current_sample
            n_end = min(n_start + len(note_stereo), total_samples)
            track[n_start:n_end] += note_stereo[:n_end-n_start]

            current_sample += int(self.sample_rate * (beat_dur / 2)) # Advance by half beat
            beat += 0.5

        return track

def mix_audio_to_video(video_path, audio_events, output_path, total_duration):
    """
    Integrates sound events AND music into the video.
    """
    sr = 44100
    engine = AudioEngine(sr)
    
    # 1. Generate Music Track
    full_audio = engine.generate_soundtrack(total_duration)
    
    # 2. Overlay SFX
    for ts, event_type in audio_events:
        idx = int(ts * sr)
        clip = None
        
        if event_type == "shot":
            clip = engine.create_shot_sound()
        elif event_type == "death":
            clip = engine.create_death_sound()
        elif event_type == "coin":
            clip = engine.create_coin_sound()
        elif event_type == "explosion":
            clip = engine.create_explosion_sound()
        elif event_type == "rocket":
            clip = engine.create_rocket_sound()
        
        if clip is not None:
            # Mix clip
            end_idx = min(idx + len(clip), len(full_audio))
            # Add to track (simple summing)
            full_audio[idx:end_idx] += clip[:end_idx-idx]

    # Normalize carefully (Soft clipping / Limiter)
    # 1. Hard clip peaks
    np.clip(full_audio, -1.5, 1.5, out=full_audio)
    # 2. Normalize to 0.9 range
    max_val = np.max(np.abs(full_audio))
    if max_val > 0:
        full_audio /= max_val
        full_audio *= 0.9

    import moviepy
    print(f"DEBUG: MoviePy version: {getattr(moviepy, '__version__', 'unknown')}")
    
    audio_clip = AudioArrayClip(full_audio, fps=sr)
    video = VideoFileClip(video_path)
    
    # Dual compatibility for MoviePy 1.x and 2.x
    if hasattr(audio_clip, 'set_duration'):
        audio_clip = audio_clip.set_duration(video.duration)
    else:
        audio_clip = audio_clip.with_duration(video.duration)
        
    if hasattr(video, 'set_audio'):
        final_video = video.set_audio(audio_clip)
    else:
        final_video = video.with_audio(audio_clip)
    
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")