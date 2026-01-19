import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import librosa
import os
import subprocess

# --- CONFIGURAÇÕES MASTER ---
WIDTH, HEIGHT = 1080, 1920
DPI = 100
FPS = 60 
NUM_BANDS = 64
AUDIO_PATH = "/home/mateus/projetos/orquestrador/youtube/Harmonic Pendulum Waves/instagram_video_20251229_152102 (1).mp3"

# --- 1. ENGENHARIA DE ESPECTRO (MEL-SCALE + TILT) ---
def analyze_audio_spectrum(file_path, n_bands=64):
    print(f"📊 Analisando espectro Mel ({n_bands} bandas): {os.path.basename(file_path)}...")
    y, sr = librosa.load(file_path, sr=44100)
    
    # 1. Mel Spectrogram para distribuição psicoacústica melhorada
    # Usando n_mels=n_bands para mapeamento direto
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=2048, hop_length=512, n_mels=n_bands, fmin=20, fmax=18000)
    
    # 2. Conversão para dB
    bands = librosa.power_to_db(S, ref=np.max)
    
    # 3. Frequency Tilt (Compensação de brilho para altas frequências)
    # Frequências altas costumam ter menos energia, vamos dar um boost linear
    tilt = np.linspace(0, 15, n_bands).reshape(-1, 1) # Boost de até 15dB no topo
    bands = bands + tilt
    
    # 4. Normalização e Escala reativa
    bands = np.clip((bands + 70) / 70, 0.01, 1.0) # Range comprimido para mais movimento
    
    # 5. Amortecimento (Liquid Decay)
    smoothed_bands = np.zeros_like(bands)
    for t in range(1, bands.shape[1]):
        # Subida rápida, descida suave (0.85 decay)
        decay = 0.88
        smoothed_bands[:, t] = np.maximum(bands[:, t], smoothed_bands[:, t-1] * decay)
    
    duration = librosa.get_duration(y=y, sr=sr)
    return smoothed_bands, duration

# --- 2. GRADIENTE DE CALOR (NEON STYLE) ---
NEON_COLORS = ["#FF00FF", "#00FFFF", "#00FF00", "#FFFF00"] # Magenta -> Cyan -> Green -> Yellow
custom_cmap = LinearSegmentedColormap.from_list("neon_gradient", NEON_COLORS)

import argparse
import sys

def render_spectrum_master(audio_path, output_path):
    if not os.path.exists(audio_path):
        print(f"Erro: {audio_path} não encontrado.")
        return

    bands_data, duration = analyze_audio_spectrum(audio_path, NUM_BANDS)
    
    print(f"🌈 RENDERIZANDO SPECTRUM MASTER ({duration:.1f}s | 60fps)...")
    
    fig, ax = plt.subplots(figsize=(WIDTH/DPI, HEIGHT/DPI), dpi=DPI, facecolor='black')
    ax.set_facecolor('black')
    ax.set_xlim(-0.5, NUM_BANDS - 0.5)
    ax.set_ylim(-2.0, 2.0) # Espaço aumentado para evitar clipping e reflexo
    ax.axis('off')
    
    x_pos = np.arange(NUM_BANDS)
    
    # Camadas para efeito de Glow
    # Barras de brilho (largas, alpha baixo)
    glow_top = ax.bar(x_pos, np.zeros(NUM_BANDS), width=1.1, color='white', align='center', alpha=0.15, linewidth=0, zorder=1)
    glow_bottom = ax.bar(x_pos, np.zeros(NUM_BANDS), width=1.1, color='white', align='center', alpha=0.1, linewidth=0, zorder=1)
    
    # Barras Superiores (Sólidas/Núcleo)
    bars_top = ax.bar(x_pos, np.zeros(NUM_BANDS), width=0.75, color='white', align='center', linewidth=0, zorder=2)
    
    # Barras Inferiores (Reflexo)
    bars_bottom = ax.bar(x_pos, np.zeros(NUM_BANDS), width=0.75, color='white', align='center', alpha=0.35, linewidth=0, zorder=2)

    # Frame mapping
    total_frames = int(FPS * duration)
    data_frames = bands_data.shape[1]

    def update(frame):
        # Mapeia frame do vídeo para coluna de dados do áudio
        idx = int((frame / total_frames) * data_frames)
        idx = min(idx, data_frames - 1)
        
        amps = bands_data[:, idx]
        # Exagerar um pouco o movimento (Power scale) para ser mais percussivo
        amps = np.power(amps, 1.3)
        
        # Cores baseadas na altura (Neon Spectrum)
        colors = custom_cmap(amps)
        
        for i in range(NUM_BANDS):
            h = amps[i] * 1.8 # Escala visual aumentada
            c = colors[i]
            
            # Atualiza núcleo
            bars_top[i].set_height(h)
            bars_top[i].set_color(c)
            
            # Atualiza reflexo
            bars_bottom[i].set_height(-h * 0.7)
            bars_bottom[i].set_color(c)
            
            # Atualiza Glow
            glow_top[i].set_height(h * 1.05)
            glow_top[i].set_color(c)
            
            glow_bottom[i].set_height(-h * 0.75)
            glow_bottom[i].set_color(c)

        return list(bars_top) + list(bars_bottom) + list(glow_top) + list(glow_bottom)

    print(f"🎬 Orquestrando {total_frames} frames de equalização neon...")
    anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/FPS, blit=True)
    
    # Temp file
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    anim.save(temp_video, writer='ffmpeg', fps=FPS, bitrate=15000,
              extra_args=['-vcodec', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p'])
    plt.close()

    print("Sincronia Final: Fundindo Espectro e Áudio...")
    if os.path.exists(output_path): os.remove(output_path)
    cmd = [
        "ffmpeg", "-y", "-i", temp_video, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if os.path.exists(temp_video): os.remove(temp_video)
    
    print(f"\n--- SPECTRUM CONCLUÍDO ---")
    print(f"Vídeo Master Final: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Input Audio File")
    parser.add_argument("-o", "--output", default="output_spectrum.mp4", help="Output Video File")
    args = parser.parse_args()
    
    render_spectrum_master(args.audio, args.output)
