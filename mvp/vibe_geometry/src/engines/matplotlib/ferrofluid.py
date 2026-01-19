import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import librosa
import os
import subprocess

# --- CONFIGURAÇÕES DO SIMBIONTE ---
WIDTH, HEIGHT = 1080, 1920
DPI = 100
FPS = 60 
RESOLUTION = 60 # 60x60 mesh
AUDIO_PATH = "/home/mateus/projetos/orquestrador/youtube/Harmonic Pendulum Waves/instagram_video_20251229_152102 (1).mp3"

# --- 1. ANÁLISE DE IMPACTO MAGNÉTICO ---
def analyze_audio_ferro(file_path):
    print(f"🧬 Extraindo DNA magnético de: {os.path.basename(file_path)}...")
    y, sr = librosa.load(file_path, sr=44100)
    rms = librosa.feature.rms(y=y)[0]
    
    # Spectral Flux para os "Spikes" agressivos
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    
    # Suavização para evitar flicker extremo
    def smooth(data, win=5):
        return np.convolve(data, np.ones(win)/win, mode='same')
    
    rms = smooth(rms, win=10)
    onset_env = smooth(onset_env, win=5)
    
    duration = librosa.get_duration(y=y, sr=sr)
    return y, sr, rms, onset_env, duration

# --- 2. ENGINE DE DEFORMAÇÃO 3D ---
def get_ferro_surface(U, V, t, vol, spike_intensity):
    base_radius = 2.0 + (vol * 1.5) # Respiração baseada no volume
    
    # Fórmulas de espinhos (Interferência harmônica esférica)
    # n_spikes aumenta com o tempo ou volume? Vamos fixar o padrão mas crescer a altura
    h1 = np.sin(U * 8 + t * 2) * np.cos(V * 7 - t)
    h2 = np.sin(U * 15) * np.sin(V * 12 + t * 3) * 0.5
    
    # Spike Intensity (Onset) dita a agressividade do relevo
    spike_height = spike_intensity * 1.5
    
    # Raio Final
    R = base_radius + (h1 + h2) * spike_height
    
    # Rugosidade de micro-detalhe
    R += np.sin(U * 30) * np.cos(V * 25) * 0.05
    
    # Cartesiano
    X = R * np.cos(U) * np.sin(V)
    Y = R * np.sin(U) * np.sin(V)
    Z = R * np.cos(V)
    
    return X, Y, Z, R

import argparse
import sys

def render_ferrofluid_venom(audio_path, output_path):
    if not os.path.exists(audio_path):
        print(f"Erro: {audio_path} não encontrado!")
        return

    y_audio, sr_audio, rms, onset, duration = analyze_audio_ferro(audio_path)
    audio_time = np.linspace(0, duration, len(rms))
    
    print(f"🧲 RENDERIZANDO CYBER-VENOM ({duration:.1f}s)...")
    
    fig = plt.figure(figsize=(WIDTH/DPI, HEIGHT/DPI), dpi=DPI, facecolor='#020005')
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor='#020005'
    ax.axis('off')
    # Remover grids
    ax.xaxis.set_pane_color((0,0,0,0)); ax.yaxis.set_pane_color((0,0,0,0)); ax.zaxis.set_pane_color((0,0,0,0))

    # Mesh base
    u = np.linspace(0, 2 * np.pi, RESOLUTION)
    v = np.linspace(0, np.pi, RESOLUTION)
    U, V = np.meshgrid(u, v)

    def update(frame):
        t = frame / FPS
        if t > duration: t = duration
        ax.clear()
        ax.axis('off')
        
        # Audio Sync
        vol_val = np.interp(t, audio_time, rms) * 6.0
        spike_val = np.interp(t, audio_time, onset) * 0.4
        
        X, Y, Z, R = get_ferro_surface(U, V, t, vol_val, spike_val)
        
        # Color Engine: De acordo com a altura do espinho (R)
        # Magma colormap para o visual de "tensão" energética
        norm_r = (R - np.min(R)) / (np.max(R) - np.min(R) + 0.1)
        colors = plt.cm.magma(norm_r)
        
        # Superfície com Mesh visível (edges) para profundidade
        surf = ax.plot_surface(X, Y, Z, facecolors=colors, 
                               edgecolor='#00FFFF', linewidth=0.15,
                               antialiased=True, shade=True, alpha=0.95)
        
        # CÂMERA
        ax.view_init(elev=22 + np.sin(t*0.4)*12, azim=t * 25)
        limit = 4.5
        ax.set_xlim(-limit, limit); ax.set_ylim(-limit, limit); ax.set_zlim(-limit * 1.5, limit * 1.5)
        
        return surf,

    total_frames = int(FPS * duration)
    print(f"🎬 Magnetizando {total_frames} frames de Simbionte Alienígena...")
    anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/FPS)
    
    # Temp file
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    anim.save(temp_video, writer='ffmpeg', fps=FPS, bitrate=15000,
              extra_args=['-vcodec', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p'])
    plt.close()

    print("Sincronia Final: Fundindo Áudio e Fluido Magnético...")
    if os.path.exists(output_path): os.remove(output_path)
    
    cmd = [
        "ffmpeg", "-y", "-i", temp_video, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if os.path.exists(temp_video): os.remove(temp_video)
    
    print(f"\n--- SYMBIOTE CONCLUÍDO ---")
    print(f"Vídeo Master Final: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Input Audio File")
    parser.add_argument("-o", "--output", default="output_ferro.mp4", help="Output Video File")
    args = parser.parse_args()
    
    render_ferrofluid_venom(args.audio, args.output)
