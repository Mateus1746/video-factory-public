"""
Audio Renderer Module.
Handles audio mixing, synthesis, and muxing with video.
"""

import json
import random
import subprocess
import numpy as np
from scipy.io import wavfile
from pathlib import Path
from typing import List, Dict

import config

class AudioRenderer:
    def __init__(self):
        print("🔊 Initializing Audio Renderer...")
        self.root_dir = Path(__file__).parent
        self.samplerate = 48000
        self.sfx_kernels = self._load_assets()
        
    def _load_assets(self) -> Dict[str, np.ndarray]:
        """Load all SFX into memory once."""
        kernels = {}
        
        # 1. Load SFX
        sound_files = config.AUDIO_PATHS.copy()
        # Remove BG from SFX list to handle separately (or keep it if logic changes)
        # In current logic, BG is handled dynamically per video or fixed.
        
        for name, rel_path in sound_files.items():
            if name == "bg": continue # Handle BG separately
            
            path = self.root_dir / rel_path
            if path.exists():
                try:
                    sr, data = wavfile.read(str(path))
                    # Normalize to int16 range if needed (scipy reads as is)
                    if data.dtype != np.int16:
                        if data.dtype == np.float32:
                            data = (data * 32767).astype(np.int16)
                    
                    # Ensure Stereo
                    if len(data.shape) == 1:
                        data = np.stack([data, data], axis=1)
                        
                    kernels[name] = data
                except Exception as e:
                    print(f"⚠️ Failed to load SFX {path}: {e}")
            else:
                print(f"⚠️ SFX missing: {path}")
                
        return kernels

    def render(self, events: List[dict], video_path: Path, output_path: Path):
        """Render audio for a specific video with Spatial Panning."""
        print(f"🎵 Rendering Spatial Audio for {video_path.name}...")
        
        duration = self._get_video_duration(video_path)
        if duration == 0:
            duration = max(e["t"] for e in events) + 2.0 if events else 10.0
                
        num_samples = int(duration * self.samplerate)
        bg_path = self.root_dir / config.AUDIO_PATHS.get("bg", "assets/music/bg_48.wav")
        bg_track = self._prepare_bg(bg_path, num_samples)
        
        sfx_track = np.zeros((num_samples, 2), dtype=np.float64)
        
        for evt in events:
            name = evt["name"]
            t = evt["t"]
            vol = evt["vol"]
            # Get X position for panning (0.0 to 1.0)
            # Default to center (0.5) if not provided
            x_pos = evt.get("x", 0.5) 
            
            if name in self.sfx_kernels:
                kernel = self.sfx_kernels[name]
                
                # Pitch Variation
                pitch = random.uniform(0.9, 1.1)
                if pitch != 1.0:
                    indices = np.round(np.arange(0, len(kernel), pitch)).astype(int)
                    indices = indices[indices < len(kernel)]
                    kernel_pitched = kernel[indices]
                else:
                    kernel_pitched = kernel
                
                # SPATIAL PANNING LOGIC
                # Left volume = 1.0 - x_pos, Right volume = x_pos
                pan_l = 1.0 - x_pos
                pan_r = x_pos
                
                start = int(t * self.samplerate)
                end = start + len(kernel_pitched)
                
                if start >= num_samples: continue
                if end > num_samples:
                    kernel_pitched = kernel_pitched[:num_samples - start]
                    end = num_samples
                
                # Apply Pan to kernel (assuming kernel is stereo)
                kernel_panned = kernel_pitched.astype(np.float64)
                kernel_panned[:, 0] *= pan_l # Left channel
                kernel_panned[:, 1] *= pan_r # Right channel
                    
                sfx_track[start:end] += kernel_panned * vol

        # 4. Mastering
        # BG Volume: 0.4, SFX: 1.0 (accumulated)
        if len(bg_track.shape) == 1:
            bg_track = np.stack([bg_track, bg_track], axis=1)
            
        final_track = (bg_track.astype(np.float64) * 0.4) + sfx_track
        
        # Limiter
        max_val = np.max(np.abs(final_track))
        if max_val > 32767:
            final_track = (final_track / max_val) * 32767
            
        final_int16 = final_track.astype(np.int16)
        
        # 5. Export Temp Wav
        temp_wav = self.root_dir / f"temp_{output_path.stem}.wav"
        wavfile.write(str(temp_wav), self.samplerate, final_int16)
        
        # 6. Mux with FFmpeg
        self._mux(video_path, temp_wav, output_path)
        
        # Cleanup
        if temp_wav.exists():
            temp_wav.unlink()

    def _get_video_duration(self, video_path: Path) -> float:
        try:
            res = subprocess.run([
                "ffprobe", "-v", "error", "-show_entries", "format=duration", 
                "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)
            ], capture_output=True, text=True)
            return float(res.stdout.strip())
        except Exception as e:
            print(f"⚠️ Could not probe duration: {e}")
            return 0.0

    def _prepare_bg(self, path: Path, num_samples: int) -> np.ndarray:
        try:
            sr, bg_data = wavfile.read(str(path))
            if bg_data.dtype != np.int16:
                bg_data = (bg_data * 32767).astype(np.int16)
        except:
            # Silent fallback
            return np.zeros((num_samples, 2), dtype=np.int16)
            
        if len(bg_data) < num_samples:
            repeats = (num_samples // len(bg_data)) + 1
            return np.tile(bg_data, (repeats, 1))[:num_samples]
        return bg_data[:num_samples]

    def _mux(self, video: Path, audio: Path, output: Path):
        cmd = [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(video),
            "-i", str(audio),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(output)
        ]
        subprocess.run(cmd, check=True)
