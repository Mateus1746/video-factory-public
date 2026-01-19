import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import librosa
import os
import subprocess

# --- CONFIGURAÇÕES DE FLUIDEZ VIVA ---
AUDIO_INPUT = "instagram_video_20251229_152102 (1).mp3"
WIDTH, HEIGHT = 1080, 1920
DPI = 100
FPS = 60
DURATION_SEC = 20
NUM_PARTICLES = 900 # Densidade alta para líquido de luz

def analyze_audio(file_path):
    print(f"Analisando frequências para fluxo líquido: {file_path}...")
    y, sr = librosa.load(file_path, sr=44100)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, np.ndarray): tempo = tempo[0]
    
    hop_len = int(sr / FPS)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop_len)[0]
    rms = (rms - np.min(rms)) / (np.max(rms) - np.min(rms) + 1e-6)
    return tempo, rms, len(y)/sr

# --- MATEMÁTICA DE FLUXO (TARGETS EM MOVIMENTO) ---

def get_infinity_flow(n, t):
    """Correnteza em forma de Infinito (Lemniscata)"""
    i = np.linspace(0, 2*np.pi, n)
    phase = i + (t * 2.5) # Velocidade da correnteza
    scale = 2.6
    denom = 1 + np.sin(phase)**2
    x = scale * np.cos(phase) / denom
    y = scale * np.sin(phase) * np.cos(phase) / denom
    z = np.sin(phase * 2) * 0.6
    return np.column_stack((x, y, z))

def get_spiral_vortex(n, t):
    """Tornado onde as partículas sobem em fluxo contínuo"""
    i = np.linspace(0, 1, n)
    # Ciclo de subida infinito
    h = ((i * 4 + t * 1.5) % 5) - 2.5
    r = 0.8 + (h**2) * 0.25
    theta = i * 25 + (t * 4)
    return np.column_stack((r * np.cos(theta), r * np.sin(theta), h))

def get_atomic_chaos(n, t):
    """Órbitas cruzadas multidirecionais"""
    i = np.arange(n)
    group = i % 3
    phase = np.linspace(0, 4*np.pi, n) + (t * 3.5)
    x, y, z = np.zeros(n), np.zeros(n), np.zeros(n)
    
    # Orbit 1: X-Y
    m0 = (group == 0)
    x[m0], y[m0], z[m0] = np.cos(phase[m0])*2.2, np.sin(phase[m0])*2.2, np.sin(phase[m0]*2)*0.4
    # Orbit 2: Y-Z
    m1 = (group == 1)
    x[m1], y[m1], z[m1] = (np.random.rand(np.sum(m1))-0.5)*0.2, np.cos(phase[m1])*2.8, np.sin(phase[m1])*2.8
    # Orbit 3: X-Z Diagonal
    m2 = (group == 2)
    s2 = np.sum(m2)
    x[m2], y[m2], z[m2] = np.sin(phase[m2])*2.4, np.sin(phase[m2])*2.4, np.cos(phase[m2])*2.4
    
    return np.column_stack((x, y, z))

import argparse
import sys

def render_living_fluid(audio_path, output_path):
    if not os.path.exists(audio_path):
        print(f"Erro: {audio_path} não encontrado.")
        return

    bpm, rms_data, audio_dur = analyze_audio(audio_path)
    actual_dur = min(DURATION_SEC, audio_dur)
    total_frames = int(FPS * actual_dur)

    print(f"🌊 RENDERIZANDO LIVING FLUID ENGINE: {WIDTH}x{HEIGHT} @ 60fps")
    fig = plt.figure(figsize=(WIDTH/DPI, HEIGHT/DPI), dpi=DPI, facecolor='black')
    fig.subplots_adjust(0,0,1,1)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('black')
    ax.axis('off')
    ax.xaxis.set_pane_color((0,0,0,0)); ax.yaxis.set_pane_color((0,0,0,0)); ax.zaxis.set_pane_color((0,0,0,0))

    current_pos = (np.random.rand(NUM_PARTICLES, 3) - 0.5) * 6
    velocity = np.zeros((NUM_PARTICLES, 3))
    
    cmap = plt.cm.cool
    base_colors = cmap(np.linspace(0, 1, NUM_PARTICLES))
    scat = ax.scatter([], [], [], s=25, edgecolors='none', alpha=0.8)

    def update(frame):
        nonlocal current_pos, velocity
        t = frame / FPS
        progress = frame / total_frames
        intensity = rms_data[frame] if frame < len(rms_data) else 0
        
        # Escolher Cena
        if progress < 0.35:
            targets = get_infinity_flow(NUM_PARTICLES, t)
            zoom, elev, azim = 3.2, 25, t*15
        elif progress < 0.7:
            targets = get_atomic_chaos(NUM_PARTICLES, t)
            zoom, elev, azim = 3.5, 35, t*25
        else:
            targets = get_spiral_vortex(NUM_PARTICLES, t)
            zoom, elev, azim = 3.5, 15, 45 + t*10

        # Steering Physics (Inertia + Turbulence)
        desired = targets - current_pos
        noise = np.sin(current_pos * 3.5 + t * 6.0) * (0.06 + intensity * 0.1)
        
        # O steering é afetado pela intensidade do áudio (mais reativo nos picos)
        steer = (desired + noise) * (0.09 + intensity * 0.05)
        velocity = velocity * 0.88 + steer
        current_pos += velocity
        
        # Visual: Brilho por velocidade
        speed = np.linalg.norm(velocity, axis=1)
        norm_speed = np.clip(speed * 4.0, 0, 1)
        
        # Aplicar glow nas cores
        dynamic_colors = base_colors.copy()
        dynamic_colors[:, 0:3] = np.clip(dynamic_colors[:, 0:3] + norm_speed[:, None] * 0.6, 0, 1)
        
        scat._offsets3d = (current_pos[:,0], current_pos[:,1], current_pos[:,2])
        scat.set_color(dynamic_colors)
        scat.set_sizes(np.full(NUM_PARTICLES, 25 * (1 + intensity + norm_speed * 0.5)))
        
        ax.set_xlim(-zoom, zoom); ax.set_ylim(-zoom, zoom); ax.set_zlim(-zoom*1.3, zoom*1.3)
        ax.view_init(elev=elev + np.sin(t)*5, azim=azim)
        
        return scat,

    anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/FPS)
    
    # Temp file
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    
    anim.save(temp_video, writer='ffmpeg', fps=FPS, bitrate=12000, 
              extra_args=['-vcodec', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p'])
    plt.close()

    print("Sincronia Final: Fundindo Água de Luz com Áudio...")
    if os.path.exists(output_path): os.remove(output_path)
    cmd = [
        "ffmpeg", "-y", "-i", temp_video, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if os.path.exists(temp_video): os.remove(temp_video)
    print(f"\n--- FLUIDO VIVO CONCLUÍDO ---")
    print(f"Vídeo Master: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Input Audio File")
    parser.add_argument("-o", "--output", default="output_living_fluid.mp4", help="Output Video File")
    args = parser.parse_args()
    
    render_living_fluid(args.audio, args.output)
