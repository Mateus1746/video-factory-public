import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import librosa
import os
import subprocess

# --- CONFIGURAÇÕES DO SHADER ---
WIDTH, HEIGHT = 1080, 1920
DPI = 100
FPS = 60 
GRID_SIZE = 25 
AUDIO_PATH = "/home/mateus/projetos/orquestrador/youtube/Harmonic Pendulum Waves/instagram_video_20251229_152102 (1).mp3"

# --- 1. ANÁLISE DE ÁUDIO REAL ---
def analyze_audio(file_path):
    print(f"📊 Analisando frequências de: {os.path.basename(file_path)}...")
    y, sr = librosa.load(file_path, sr=44100)
    
    # RMS (Volume/Kick)
    rms = librosa.feature.rms(y=y)[0]
    # Spectral Flux (Ripples/Mudanças)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    
    duration = librosa.get_duration(y=y, sr=sr)
    return y, sr, rms, onset_env, duration

# --- 2. MATH DO SHADER ---
def get_audio_data(t, rms, onset, duration):
    # Converte tempo em índice de frame de áudio
    idx = int((t / duration) * len(rms))
    idx = min(idx, len(rms) - 1)
    
    vol = rms[idx] * 5.0 # Ganho para visibilidade
    pitch = onset[idx] * 0.5
    return vol, pitch

def generate_grid_heights(X, Z, t, rms, onset, duration):
    dist = np.sqrt(X**2 + Z**2)
    vol, pitch = get_audio_data(t, rms, onset, duration)
    
    # h = d*.12*(1.+pitch*1.6) + v*2.
    # Adaptado para áudio real: adicionamos uma componente de onda baseada no t
    wave_sync = np.sin(dist * 0.3 - t * 4.0) * pitch * 2.0
    
    heights = (dist * 0.1) * (1.0 + pitch * 2.0) + (vol * 6.0) + wave_sync
    
    # Brilho central no Kick real
    center_mask = dist < 7.0
    heights[center_mask] *= (1.0 + vol * 1.5)
    
    return heights, dist, vol

import argparse
import sys

def render_real_audio_city(audio_path, output_path):
    if not os.path.exists(audio_path):
        print(f"Erro: {audio_path} não encontrado.")
        return

    y, sr, rms, onset, duration = analyze_audio(audio_path)
    
    print(f"🎛️ INICIANDO RENDERIZAÇÃO REAL-SYNC ({duration:.1f}s)...")
    
    fig = plt.figure(figsize=(WIDTH/DPI, HEIGHT/DPI), dpi=DPI, facecolor='#050005')
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#050005')
    ax.axis('off')
    ax.xaxis.set_pane_color((0,0,0,0)); ax.yaxis.set_pane_color((0,0,0,0)); ax.zaxis.set_pane_color((0,0,0,0))
    
    # Grid fixo
    gx = np.linspace(-15, 15, GRID_SIZE)
    gz = np.linspace(-15, 15, GRID_SIZE)
    X_grid, Z_grid = np.meshgrid(gx, gz)
    X, Z = X_grid.flatten(), Z_grid.flatten()
    num_points = len(X)
    
    scat_top = ax.scatter([], [], [], marker='s', edgecolors='none', alpha=1.0)
    scat_bottom = ax.scatter([], [], [], marker='s', edgecolors='none', alpha=0.2)

    def update(frame):
        t = frame / FPS
        if t > duration: t = duration
        
        H, D, vol = generate_grid_heights(X, Z, t, rms, onset, duration)
        
        # --- COLOR ENGINE SINCRO ---
        colors = np.zeros((num_points, 4))
        # Mix baseado no volume real (Kick)
        mix_factor = np.clip(vol * 2.5, 0, 1)
        radial_factor = np.clip(D / 20.0, 0, 1)
        
        # Purple base -> Green Neon flash
        r = 0.6 * (1 - mix_factor) + 0.0 * mix_factor
        g = 0.0 * (1 - mix_factor) + 1.0 * mix_factor
        b = 0.8 * (1 - mix_factor) + 0.5 * mix_factor
        
        # Brilho nos topos (H)
        brightness = np.clip(H / 8.0, 0.4, 2.0)
        colors[:, 0] = np.clip(r * brightness, 0, 1)
        colors[:, 1] = np.clip(g * brightness, 0, 1)
        colors[:, 2] = np.clip(b * brightness + radial_factor*0.2, 0, 1)
        colors[:, 3] = 1.0
        
        scat_top._offsets3d = (X, Z, H)
        scat_top.set_color(colors)
        scat_top.set_sizes(np.full(num_points, 50 + vol * 60))
        
        scat_bottom._offsets3d = (X, Z, -H - 1.0)
        scat_bottom.set_color(colors)
        scat_bottom.set_sizes(np.full(num_points, 45 + vol * 30))
        
        # CÂMERA DINÂMICA
        ax.view_init(elev=32 + np.sin(t*0.5)*8, azim=t * 20)
        zoom = 18.0
        ax.set_xlim(-zoom, zoom); ax.set_ylim(-zoom, zoom); ax.set_zlim(-15, 15)
        
        return scat_top, scat_bottom

    total_frames = int(FPS * duration)
    print(f"🎬 Gerando {total_frames} frames de Real-Audio Cyber-Shader...")
    anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/FPS)
    
    # Temp file
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    anim.save(temp_video, writer='ffmpeg', fps=FPS, bitrate=12000, 
              extra_args=['-vcodec', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p'])
    plt.close()
    
    print("Sincronia Final: Fundindo Áudio Real e Neon City...")
    if os.path.exists(output_path): os.remove(output_path)
    cmd = [
        "ffmpeg", "-y", "-i", temp_video, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if os.path.exists(temp_video): os.remove(temp_video)
    
    print(f"\n--- REAL-SYNC CONCLUÍDO ---")
    print(f"Vídeo Master Final: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Input Audio File")
    parser.add_argument("-o", "--output", default="output_shader_city.mp4", help="Output Video File")
    args = parser.parse_args()
    
    render_real_audio_city(args.audio, args.output)
