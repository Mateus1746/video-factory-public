import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import librosa
import os
import subprocess

# --- CONFIGURAÇÕES MASTER ---
WIDTH, HEIGHT = 1080, 1920
DPI = 100
FPS = 60 
BAR_COUNT_HALF = 40 # 40 de cada lado = 80 total
CURVE_DEPTH = 0.45
AUDIO_PATH = "/home/mateus/projetos/orquestrador/youtube/Harmonic Pendulum Waves/instagram_video_20251229_152102 (1).mp3"

# --- 1. ENGENHARIA DE ÁUDIO (MEL-SCALE + TILT) ---
def analyze_audio_arch(file_path, n_bands=40):
    print(f"📊 Analisando Mel-Bands para o Arco: {os.path.basename(file_path)}...")
    y, sr = librosa.load(file_path, sr=44100)
    
    # 1. Mel Spectrogram (Grave no centro, Agudos nas pontas)
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=2048, hop_length=512, n_mels=n_bands, fmin=30, fmax=16000)
    
    # 2. Conversão dB e Tilt
    bands = librosa.power_to_db(S, ref=np.max)
    tilt = np.linspace(0, 12, n_bands).reshape(-1, 1) # Boost de 12dB no topo
    bands = bands + tilt
    
    # 3. Normalização
    bands = np.clip((bands + 75) / 75, 0.01, 1.0)
    
    # 4. Suavização (Fall-off)
    smoothed = np.zeros_like(bands)
    for t in range(1, bands.shape[1]):
        smoothed[:, t] = np.maximum(bands[:, t], smoothed[:, t-1] * 0.89)
        
    duration = librosa.get_duration(y=y, sr=sr)
    return smoothed, duration

import argparse
import sys

def render_arch_master(audio_path, output_path):
    if not os.path.exists(audio_path):
        print(f"Erro: {audio_path} não encontrado.")
        return

    bands, duration = analyze_audio_arch(audio_path, BAR_COUNT_HALF)
    
    print(f"⛩️ CONSTRUINDO ARCO MASTER ({duration:.1f}s | 60fps)...")
    
    fig, ax = plt.subplots(figsize=(WIDTH/DPI, HEIGHT/DPI), dpi=DPI, facecolor='black')
    ax.set_facecolor('black')
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-2.2, 2.5) # Aumentado para acomodar arco e reflexo sem cortes
    ax.axis('off')

    # Geometria do Arco (Refinada)
    x_right = np.linspace(0.01, 1, BAR_COUNT_HALF)
    x_all = np.concatenate([-x_right[::-1], x_right])
    
    # Base Curvada (Parábola mais elegante)
    curve_base = (1.0 - x_all**2) * CURVE_DEPTH
    
    bar_width = (2.0 / (BAR_COUNT_HALF * 2)) * 0.75
    
    # Cores Neon (Gradiente Indigo -> Cyan -> Magenta)
    from matplotlib.colors import LinearSegmentedColormap
    ARCH_COLORS = ["#4B0082", "#00FFFF", "#FF00FF"]
    arch_cmap = LinearSegmentedColormap.from_list("arch_neon", ARCH_COLORS)
    base_colors = arch_cmap(np.linspace(0, 1, len(x_all)))

    # Barras e Reflexos com Camadas de Glow
    glow_bars = ax.bar(x_all, np.zeros(len(x_all)), width=bar_width*1.4, 
                       bottom=curve_base, color='white', alpha=0.15, edgecolor='none', zorder=1)
    
    plot_bars = ax.bar(x_all, np.zeros(len(x_all)), width=bar_width, 
                       bottom=curve_base, color='white', edgecolor='none', zorder=2)
    
    plot_refs = ax.bar(x_all, np.zeros(len(x_all)), width=bar_width,
                       bottom=curve_base, color='white', alpha=0.3, edgecolor='none', zorder=2)

    total_frames = int(FPS * duration)
    data_frames = bands.shape[1]
    
    # Obter RMS para pulso global
    y_audio, _ = librosa.load(audio_path, sr=44100)
    rms = librosa.feature.rms(y=y_audio, hop_length=512)[0]
    rms = (rms - np.min(rms)) / (np.max(rms) - np.min(rms) + 1e-6)

    def update(frame):
        idx = int((frame / total_frames) * data_frames)
        idx = min(idx, data_frames - 1)
        
        # Pulso global do Arco
        pulse = 1.0 + rms[min(idx, len(rms)-1)] * 0.15
        
        # Áudio espelhado: centro (idx 0) é grave
        audio_half = bands[:, idx]
        audio_full = np.concatenate([audio_half[::-1], audio_half])
        
        for i, h in enumerate(audio_full):
            h_vis = np.power(h, 1.2) * 1.5 * pulse # Escala e pulso
            c = base_colors[i]
            
            # Reatividade de Cor (Branco nos picos)
            if h > 0.8:
                final_c = 'white'
            else:
                final_c = c
                
            # Atualizar Barra
            plot_bars[i].set_height(h_vis)
            plot_bars[i].set_color(final_c)
            
            # Atualizar Glow
            glow_bars[i].set_height(h_vis * 1.1)
            glow_bars[i].set_color(final_c)
            
            # Atualizar Reflexo
            plot_refs[i].set_height(-h_vis * 0.6)
            plot_refs[i].set_color(final_c)

        return list(plot_bars) + list(plot_refs) + list(glow_bars)

    print(f"🎬 Orquestrando {total_frames} frames de arco digital...")
    anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/FPS, blit=True)
    
    # Temp file
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    
    anim.save(temp_video, writer='ffmpeg', fps=FPS, bitrate=10000,
              extra_args=['-vcodec', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p'])
    plt.close()

    print("Sincronia Final: Fundindo Geometria em Arco e Áudio...")
    if os.path.exists(output_path): os.remove(output_path)
    
    cmd = [
        "ffmpeg", "-y", "-i", temp_video, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if os.path.exists(temp_video): os.remove(temp_video)
    
    print(f"\n--- ARCH MASTER CONCLUÍDO ---")
    print(f"Vídeo Master Final: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Input Audio File")
    parser.add_argument("-o", "--output", default="output_arch.mp4", help="Output Video File")
    args = parser.parse_args()
    
    render_arch_master(args.audio, args.output)
