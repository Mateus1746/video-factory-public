import argparse
import json
import os
import sys

import librosa
import numpy as np

from beat_timer import extract_beat_data


def map_pitch_to_color(pitch_index):
    """
    Maps a pitch index (0-11 for C-B) to a HEX color.
    Colors progression:
    Low (Grave) -> Blue/Purple
    Mid -> Green/Yellow
    High (Agudo) -> Orange/Pink
    """
    # Using a 12-tone color map (Chroma)
    # 0:C, 1:C#, 2:D, 3:D#, 4:E, 5:F, 6:F#, 7:G, 8:G#, 9:A, 10:A#, 11:B
    colors = [
        "#0000FF", # C  - Blue
        "#4B0082", # C# - Indigo
        "#8B00FF", # D  - Violet
        "#9400D3", # D# - DarkViolet
        "#FF00FF", # E  - Magenta
        "#FF1493", # F  - DeepPink
        "#FF4500", # F# - OrangeRed
        "#FF8C00", # G  - DarkOrange
        "#FFA500", # G# - Orange
        "#FFD700", # A  - Gold
        "#FFFF00", # A# - Yellow
        "#ADFF2F"  # B  - GreenYellow
    ]
    return colors[pitch_index % 12]

def analyze_music(file_path, output_path, target_bpm=None):
    print(f"🎵 Analyzing music (Enhanced): {file_path}...")
    
    # Use the improved beat_timer logic
    beat_results = extract_beat_data(file_path, target_bpm=target_bpm)
    if not beat_results:
        print("❌ Failed to extract beat data.")
        return

    try:
        y, sr = librosa.load(file_path, sr=None)
    except Exception as e:
        print(f"Error loading file for chroma: {e}")
        return

    print("✨ Extracting fine-grained features (Chroma/Energy)...")
    # We still use RMS and Chroma for the visual data points
    rms = librosa.feature.rms(y=y)[0]
    rms_times = librosa.frames_to_time(range(len(rms)), sr=sr)

    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_times = librosa.frames_to_time(range(chroma.shape[1]), sr=sr)
    
    # --- MULTI-BAND SPECTROGRAM ANALYSIS ---
    # We want 4 bands: Sub (<250), LowMid (250-500), HighMid (500-2000), High (>2000)
    # Using Mel Spectrogram is efficient
    print("🌈 Analyzing Frequency Bands...")
    # n_mels=128 gives decent resolution
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
    # Convert to log scale (dB)
    S_dB = librosa.power_to_db(S, ref=np.max)
    
    # Get frequencies of mel bins
    mel_freqs = librosa.mel_frequencies(n_mels=128, fmin=0, fmax=8000)
    
    # Define masks for bands
    mask_sub = mel_freqs < 250
    mask_low = (mel_freqs >= 250) & (mel_freqs < 500)
    mask_mid = (mel_freqs >= 500) & (mel_freqs < 2000)
    mask_high = mel_freqs >= 2000
    
    # Calculate energy per band over time
    # Normalize result to 0-1 range roughly using MinMax later or just local scaling
    band_sub = np.mean(S[mask_sub], axis=0)
    band_low = np.mean(S[mask_low], axis=0)
    band_mid = np.mean(S[mask_mid], axis=0)
    band_high = np.mean(S[mask_high], axis=0)
    
    # Normalize bands (local scaling relative to song max)
    def normalize_band(b):
        m = np.max(b)
        if m == 0: return b
        return b / m

    band_sub = normalize_band(band_sub)
    band_low = normalize_band(band_low)
    band_mid = normalize_band(band_mid)
    band_high = normalize_band(band_high)
    
    mel_times = librosa.frames_to_time(range(S.shape[1]), sr=sr)

    data = {
        "metadata": beat_results["metadata"],
        "beats": []
    }

    # Re-process beats from the high-precision extraction
    for b in beat_results["beats"]:
        b_time = b["timestamp"]
        
        # Find the index in RMS and Chroma closest to the beat time
        rms_idx = np.argmin(np.abs(rms_times - b_time))
        chroma_idx = np.argmin(np.abs(chroma_times - b_time))
        mel_idx = np.argmin(np.abs(mel_times - b_time))

        # Get energy at this beat (we can use the one from beat_timer too, but let's keep RMS for compatibility)
        energy = float(rms[rms_idx])

        # --- RETENTION BOOST ---
        # 5-Second Rule: Force high energy in the intro to ensure strong visual engagement
        if b_time < 5.0:
            # Boost multiplier and set a high floor (4.0 guarantees a strong pulse)
            energy = max(energy * 2.5, 4.0)

        # Get dominant pitch at this beat
        pitch_distribution = chroma[:, chroma_idx]
        dominant_pitch_idx = int(np.argmax(pitch_distribution))
        color = map_pitch_to_color(dominant_pitch_idx)
        
        # Get Band Energies
        # We boost them slightly to emphasize hits
        b_v1 = float(band_sub[mel_idx])
        b_v2 = float(band_low[mel_idx])
        b_v3 = float(band_mid[mel_idx])
        b_v4 = float(band_high[mel_idx])

        data["beats"].append({
            "timestamp": round(float(b_time), 3),
            "energy": round(energy, 5),
            "pitch_index": dominant_pitch_idx,
            "color_hex": color,
            "beat_timer_energy": b["energy"],
            "energy_bands": [round(b_v1, 3), round(b_v2, 3), round(b_v3, 3), round(b_v4, 3)]
        })

    print(f"Exporting to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)
    
    print("Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze MP3 for beats, pitch, and energy.")
    parser.add_argument("input", help="Path to input MP3 file")
    parser.add_argument("-o", "--output", default="output.json", help="Path to output JSON file")
    parser.add_argument("--bpm", type=float, help="BPM Hint (targets specific octave)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"File not found: {args.input}")
        sys.exit(1)
        
    analyze_music(args.input, args.output, args.bpm)
