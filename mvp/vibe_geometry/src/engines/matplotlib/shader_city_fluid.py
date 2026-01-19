import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import librosa
import os
import subprocess
from scipy.ndimage import gaussian_filter

# --- CONFIGURAÇÕES DE ALTA FLUIDEZ ---
WIDTH, HEIGHT = 1080, 1920
DPI = 100
FPS = 60 
GRID_SIZE = 40 # 40x40 = 1600 prédios (Efeito mar de luz)
AUDIO_PATH = "/home/mateus/projetos/orquestrador/youtube/Harmonic Pendulum Waves/instagram_video_20251229_152102 (1).mp3"

# --- 1. ENGENHARIA DE ÁUDIO SUAVE (EMA) ---
def analyze_audio_fluid(file_path):
    print(f"🌊 Analisando e suavizando áudio: {os.path.basename(file_path)}...")
    y, sr = librosa.load(file_path, sr=44100)
    
    # RMS Bruto
    rms_raw = librosa.feature.rms(y=y)[0]
    # Spectral Flux Bruto
    onset_env_raw = librosa.onset.onset_strength(y=y, sr=sr)
    
    # Suavização Temporal (Exponential Moving Average)
    def ema_smooth(data, alpha=0.15):
        smooth = np.zeros_like(data)
        smooth[0] = data[0]
        for i in range(1, len(data)):
            smooth[i] = alpha * data[i] + (1 - alpha) * smooth[i-1]
        return smooth

    rms = ema_smooth(rms_raw, alpha=0.12) # Mais pesado, mais inércia
    onset = ema_smooth(onset_env_raw, alpha=0.2) # Reage rápido mas sem jitter
    
    duration = librosa.get_duration(y=y, sr=sr)
    return y, sr, rms, onset, duration

# --- 2. ENGINE DE FLUIDEZ VISUAL ---
def get_fluid_heights(X_grid, Z_grid, t, rms, onset, duration):
    # Índice de sincronia
    idx = int((t / duration) * len(rms))
    idx = min(idx, len(rms) - 1)
    
    vol = rms[idx] * 6.5
    pitch = onset[idx] * 0.4
    
    dist = np.sqrt(X_grid**2 + Z_grid**2)
    
    # Altura Base (Ondas circulares fluidas)
    # t*5.0 dá a velocidade da onda se propagando
    wave = np.sin(dist * 0.35 - t * 5.0) * (0.5 + pitch)
    
    # h = base + kick + pitch_wave
    H = (dist * 0.08) + (vol * 5.0) + (wave * 2.5)
    
    # Mascaramento central orgânico
    center_glow = np.exp(-dist**2 / 50.0) * vol * 8.0
    H += center_glow
    
    # Suavização Espacial (Filtro Gaussiano no grid 2D)
    # Isso faz os prédios vizinhos se moverem juntos como um "gel"
    H_smoothed = gaussian_filter(H, sigma=0.8)
    
    return H_smoothed.flatten(), dist.flatten(), vol

import argparse
import sys

def render_fluid_city(audio_path, output_path):
    if not os.path.exists(audio_path):
        print(f"Erro: {audio_path} não encontrado.")
        return

    y, sr, rms, onset, duration = analyze_audio_fluid(audio_path)
    
    print(f"🎬 RENDERIZANDO OCEANO NEON ({GRID_SIZE}x{GRID_SIZE} @ 60fps)...")
    
    fig = plt.figure(figsize=(WIDTH/DPI, HEIGHT/DPI), dpi=DPI, facecolor='#030005')
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#030005')
    ax.axis('off')
    ax.xaxis.set_pane_color((0,0,0,0)); ax.yaxis.set_pane_color((0,0,0,0)); ax.zaxis.set_pane_color((0,0,0,0))
    
    gx = np.linspace(-15, 15, GRID_SIZE)
    gz = np.linspace(-15, 15, GRID_SIZE)
    X_grid, Z_grid = np.meshgrid(gx, gz)
    num_points = GRID_SIZE * GRID_SIZE
    
    scat_top = ax.scatter([], [], [], marker='s', edgecolors='none', alpha=1.0)
    scat_bottom = ax.scatter([], [], [], marker='s', edgecolors='none', alpha=0.15)

    def update(frame):
        t = frame / FPS
        if t > duration: t = duration
        
        H, D, vol = get_fluid_heights(X_grid, Z_grid, t, rms, onset, duration)
        X, Z = X_grid.flatten(), Z_grid.flatten()
        
        # --- COLOR GRADIENT ENGINE (Fluid) ---
        # Camadas: Purple -> Cyan -> Teal -> Green
        colors = np.zeros((num_points, 4))
        mix_v = np.clip(vol * 2.2, 0, 1)
        r_f = np.clip(D / 18.0, 0, 1)
        
        # Base Roxo Profundo
        r = 0.5 * (1 - mix_v)
        g = 0.0 * (1 - mix_v) + mix_v * 1.0
        b = 0.8 * (1 - mix_v) + mix_v * 0.6
        
        # Injetar Ciano nas Bordas Altas
        brightness = np.clip(H / 7.0, 0.5, 2.0)
        colors[:, 0] = np.clip(r * brightness, 0, 1)
        colors[:, 1] = np.clip(g * brightness + (1-r_f)*0.2, 0, 1) # Centro mais verde
        colors[:, 2] = np.clip(b * brightness + r_f*0.4, 0, 1)   # Bordas mais azuis/roxas
        colors[:, 3] = 1.0
        
        scat_top._offsets3d = (X, Z, H)
        scat_top.set_color(colors)
        scat_top.set_sizes(np.full(num_points, 35 + vol * 50))
        
        scat_bottom._offsets3d = (X, Z, -H - 2.0)
        scat_bottom.set_color(colors)
        scat_bottom.set_sizes(np.full(num_points, 30 + vol * 20))
        
        # CÂMERA HIPNÓTICA
        # Rotação multi-frequência para parecer um drone voando suavemente
        ax.view_init(elev=30 + np.sin(t*0.3)*10, azim=t * 15 + np.cos(t*0.2)*5)
        zoom = 18.0 - (np.sin(t*0.4) * 2.0) # Pulso de zoom sutil
        ax.set_xlim(-zoom, zoom); ax.set_ylim(-zoom, zoom); ax.set_zlim(-15, 15)
        
        return scat_top, scat_bottom

    total_frames = int(FPS * duration)
    anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/FPS)
    
    # Temp file
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    anim.save(temp_video, writer='ffmpeg', fps=FPS, bitrate=15000, 
              extra_args=['-vcodec', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p'])
    plt.close()
    
    print("Sincronia Final: Fundindo Áudio e Oceano de Luz...")
    if os.path.exists(output_path): os.remove(output_path)
    cmd = [
        "ffmpeg", "-y", "-i", temp_video, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if os.path.exists(temp_video): os.remove(temp_video)
    
    print(f"\n--- FLUIDMASTER CONCLUÍDO ---")
    print(f"Vídeo Master Final: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Input Audio File")
    parser.add_argument("-o", "--output", default="output_shader_city.mp4", help="Output Video File")
    args = parser.parse_args()
    
    render_fluid_city(args.audio, args.output)
