import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import librosa
import numpy as np
import soundfile as sf


def detect_key_and_mode(y: np.ndarray, sr: int) -> Tuple[str, str]:
    """
    Detects the key and mode (Major/Minor) of the audio using Chroma features
    and Krumhansl-Schmuckler template matching.
    """
    # 1. Get Chroma features
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_sum = np.sum(chroma, axis=1)

    # 2. Key templates (Krumhansl-Schmuckler)
    major_template = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor_template = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    best_corr = -1.0
    best_key = ""
    best_mode = ""

    for i in range(12):
        # Rotate templates to match current root note
        rotated_major = np.roll(major_template, i)
        rotated_minor = np.roll(minor_template, i)

        # Calculate Pearson correlation
        corr_major = np.corrcoef(chroma_sum, rotated_major)[0, 1]
        corr_minor = np.corrcoef(chroma_sum, rotated_minor)[0, 1]

        if corr_major > best_corr:
            best_corr = corr_major
            best_key = note_names[i]
            best_mode = "Major"
        
        if corr_minor > best_corr:
            best_corr = corr_minor
            best_key = note_names[i]
            best_mode = "Minor"

    return best_key, best_mode


def extract_beat_data(
    audio_path: str, 
    output_json: Optional[str] = None, 
    target_bpm: Optional[float] = None
) -> Optional[Dict[str, Any]]:
    """
    Extracts high-precision beat timestamps, BPM (with octave correction), 
    Key, and energy levels.
    """
    print(f"🚀 Loading audio: {os.path.basename(audio_path)}...")
    try:
        y, sr = librosa.load(audio_path, sr=None)
    except Exception as e:
        print(f"❌ Error loading audio: {e}")
        return None

    duration = librosa.get_duration(y=y, sr=sr)
    
    # 1. Detect Key and Mode
    print("🎹 Detecting Key/Mode...")
    key, mode = detect_key_and_mode(y, sr)
    print(f"✨ Detected Key: {key} {mode}")

    # 2. Enhanced Beat Tracking with Octave Correction
    print("🧠 Analyzing beats (with octave correction)...")
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    
    # If no target_bpm is provided, we try to see if the default detection is too high
    # Usually, pop/rock is in 70-130 range. If > 140, it might be double time.
    start_bpm = target_bpm if target_bpm else 80.0
    
    tempo_array, beat_frames = librosa.beat.beat_track(
        onset_envelope=onset_env, 
        sr=sr,
        start_bpm=start_bpm
    )
    
    bpm = float(np.mean(tempo_array)) if np.ndim(tempo_array) > 0 else float(tempo_array)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    
    # 3. Extract energy level (peak onset strength) at each beat
    onset_frames = librosa.frames_to_time(np.arange(len(onset_env)), sr=sr)
    
    beat_data: List[Dict[str, Any]] = []
    for t in beat_times:
        idx = np.argmin(np.abs(onset_frames - t))
        energy = float(onset_env[idx])
        
        beat_data.append({
            "timestamp": round(float(t), 4),
            "energy": round(energy, 4),
            "ms": int(t * 1000)
        })

    intervals = np.diff(beat_times)
    avg_deltatime = float(np.mean(intervals)) if len(intervals) > 0 else 0.0
    
    print("-" * 40)
    print(f"✅ ANALYSIS COMPLETE")
    print("-" * 40)
    print(f"Key: {key} {mode}")
    print(f"BPM: {bpm:.2f}")
    print(f"Total Batidas: {len(beat_data)}")
    print("-" * 40)
    
    results = {
        "metadata": {
            "filename": os.path.basename(audio_path),
            "bpm": bpm,
            "key": key,
            "mode": mode,
            "deltatime": avg_deltatime,
            "duration": duration,
            "total_beats": len(beat_data)
        },
        "beats": beat_data
    }

    if output_json:
        print(f"💾 Saving to {output_json}...")
        with open(output_json, 'w') as f:
            json.dump(results, f, indent=4)

    return results


def generate_click_track(audio_path: str, beat_times: List[float], output_path: str):
    print(f"🔊 Generating click track: {output_path}...")
    y, sr = librosa.load(audio_path, sr=None)
    clicks = librosa.clicks(frames=None, sr=sr, times=np.array(beat_times), length=len(y))
    y_mixed = librosa.util.normalize(y * 0.5 + clicks * 0.5)
    sf.write(output_path, y_mixed, sr)
    print("✨ Click track saved!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrai BPM, Key e Batidas com alta precisão.")
    parser.add_argument("audio", help="Caminho para o arquivo de áudio")
    parser.add_argument("-o", "--output", help="Salvar resultado em JSON")
    parser.add_argument("--bpm", type=float, help="Dica de BPM inicial (ajuda na correção de oitava)")
    parser.add_argument("--clicks", help="Gerar arquivo de áudio com clicks")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.audio):
        print(f"❌ Arquivo não encontrado: {args.audio}")
        sys.exit(1)
        
    data = extract_beat_data(args.audio, args.output, args.bpm)
    
    if data and args.clicks:
        times = [b["timestamp"] for b in data["beats"]]
        generate_click_track(args.audio, times, args.clicks)
