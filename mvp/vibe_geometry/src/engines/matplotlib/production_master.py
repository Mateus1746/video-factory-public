import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import librosa
import os
import subprocess

# --- CONFIGURAÇÕES DE PRODUÇÃO (MASTER SCRIPT) ---
AUDIO_INPUT = "instagram_video_20251229_152102 (1).mp3"
WIDTH_PX = 1080
HEIGHT_PX = 1920
DPI = 100
FIG_W = WIDTH_PX / DPI  # 10.8 polegadas
FIG_H = HEIGHT_PX / DPI # 19.2 polegadas

FPS = 60                # Fluidez máxima para mobile
DURATION_SEC = 20       # Tempo estendido para sincronizar com o áudio
BITRATE = 12000         # 12 Mbps (Alta qualidade)

# --- CONFIGURAÇÃO DO ENXAME (SWARM) ---
NUM_DRONES_PER_GROUP = 200 # 600 drones totais
TOTAL_DRONES = NUM_DRONES_PER_GROUP * 3

# Cores Neon de Alta Visibilidade
COLOR_ALPHA = '#FF0055' # Neon Red/Pink
COLOR_BETA  = '#00FF99' # Neon Green/Cyan
COLOR_GAMMA = '#0088FF' # Electric Blue

def analyze_audio(file_path):
    print(f"Analisando áudio para sincronia fina: {file_path}...")
    y, sr = librosa.load(file_path, sr=44100)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, np.ndarray): tempo = tempo[0]
    
    hop_len = int(sr / FPS)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop_len)[0]
    rms = (rms - np.min(rms)) / (np.max(rms) - np.min(rms) + 1e-6)
    return tempo, rms, len(y)/sr

# --- FUNÇÕES GEOMÉTRICAS ---
def get_sphere_sector(n, center=(0,0,0), radius=1.0):
    indices = np.arange(0, n, dtype=float) + 0.5
    phi = np.arccos(1 - 2*indices/n)
    theta = np.pi * (1 + 5**0.5) * indices
    x = np.cos(theta) * np.sin(phi) * radius + center[0]
    y = np.sin(theta) * np.sin(phi) * radius + center[1]
    z = np.cos(phi) * radius + center[2]
    return np.column_stack((x, y, z))

def get_atomic_orbits(n, axis='x', scale=1.8):
    t = np.linspace(0, 2*np.pi, n)
    jitter = (np.random.rand(n) - 0.5) * 0.15
    if axis == 'x':
        x = np.cos(t) * scale
        y = np.sin(t) * scale
        z = np.sin(2*t) * 0.5 + jitter
    elif axis == 'y':
        x = jitter
        y = np.cos(t) * scale
        z = np.sin(t) * scale
    else:
        x = np.cos(t) * scale
        y = np.sin(t) * scale 
        z = np.sin(t) * scale 
    return np.column_stack((x, y, z))

def get_dna_helix(n, offset_angle=0):
    t = np.linspace(0, 4*np.pi, n)
    radius = 1.2
    x = radius * np.cos(t + offset_angle)
    y = radius * np.sin(t + offset_angle)
    z = np.linspace(-3.0, 3.0, n)
    return np.column_stack((x, y, z))

def get_choreography(progress):
    if progress < 0.20:
        r = 0.8
        t1 = get_sphere_sector(NUM_DRONES_PER_GROUP, (0, -1.5, 0), r)
        t2 = get_sphere_sector(NUM_DRONES_PER_GROUP, (1.3, 1.0, 0), r)
        t3 = get_sphere_sector(NUM_DRONES_PER_GROUP, (-1.3, 1.0, 0), r)
        return t1, t2, t3
    elif progress < 0.60:
        t1 = get_atomic_orbits(NUM_DRONES_PER_GROUP, 'x')
        t2 = get_atomic_orbits(NUM_DRONES_PER_GROUP, 'y')
        t3 = get_atomic_orbits(NUM_DRONES_PER_GROUP, 'z')
        return t1, t2, t3
    else:
        t1 = get_dna_helix(NUM_DRONES_PER_GROUP, 0)
        t2 = get_dna_helix(NUM_DRONES_PER_GROUP, 2*np.pi/3)
        t3 = get_dna_helix(NUM_DRONES_PER_GROUP, 4*np.pi/3)
        return t1, t2, t3

import argparse
import sys

def render_production_master(audio_path, output_path):
    if not os.path.exists(audio_path):
        print(f"Erro: {audio_path} não encontrado.")
        return

    bpm, rms_data, audio_dur = analyze_audio(audio_path)
    actual_dur = min(DURATION_SEC, audio_dur)
    total_frames = int(FPS * actual_dur)

    print(f"--- INICIANDO RENDERIZAÇÃO DE PRODUÇÃO ---")
    print(f"Resolução: {WIDTH_PX}x{HEIGHT_PX} | FPS: {60} | Duração: {actual_dur:.1f}s")
    
    fig = plt.figure(figsize=(FIG_W, FIG_H), dpi=DPI, facecolor='black')
    plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('black')
    ax.grid(False)
    ax.axis('off')
    ax.xaxis.set_pane_color((0, 0, 0, 0)); ax.yaxis.set_pane_color((0, 0, 0, 0)); ax.zaxis.set_pane_color((0, 0, 0, 0))
    
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2.5, 2.5); ax.set_zlim(-3.5, 3.5)

    pos_a = np.zeros((NUM_DRONES_PER_GROUP, 3)) + 5 
    pos_b = np.zeros((NUM_DRONES_PER_GROUP, 3)) - 5
    pos_c = np.zeros((NUM_DRONES_PER_GROUP, 3)) 
    
    scat_a = ax.scatter([], [], [], c=COLOR_ALPHA, s=40, depthshade=True, edgecolors='white', linewidth=0.2)
    scat_b = ax.scatter([], [], [], c=COLOR_BETA,  s=40, depthshade=True, edgecolors='white', linewidth=0.2)
    scat_c = ax.scatter([], [], [], c=COLOR_GAMMA, s=40, depthshade=True, edgecolors='white', linewidth=0.2)

    def update(frame):
        nonlocal pos_a, pos_b, pos_c
        progress = frame / total_frames
        
        target_a, target_b, target_c = get_choreography(progress)
        intensity = rms_data[frame] if frame < len(rms_data) else 0
        
        # Camera Orbit Cinematic
        ax.view_init(elev=20 + np.sin(progress*np.pi)*10, azim=45 + (progress * 180))
        
        # Física: Aceleração no Beat + Noise
        speed = 0.05 + intensity * 0.1
        pos_a += (target_a - pos_a) * speed + (np.random.rand(*pos_a.shape) - 0.5) * 0.03
        pos_b += (target_b - pos_b) * speed + (np.random.rand(*pos_b.shape) - 0.5) * 0.03
        pos_c += (target_c - pos_c) * speed + (np.random.rand(*pos_c.shape) - 0.5) * 0.03
        
        # Sincronia de Brilho
        size_dynamic = 40 * (1 + intensity * 1.5)
        alpha_dynamic = 0.7 + intensity * 0.3
        
        scat_a._offsets3d = (pos_a[:,0], pos_a[:,1], pos_a[:,2])
        scat_b._offsets3d = (pos_b[:,0], pos_b[:,1], pos_b[:,2])
        scat_c._offsets3d = (pos_c[:,0], pos_c[:,1], pos_c[:,2])
        
        for s in [scat_a, scat_b, scat_c]:
            s.set_sizes(np.full(NUM_DRONES_PER_GROUP, size_dynamic))
            s.set_alpha(alpha_dynamic)
            
        return scat_a, scat_b, scat_c

    anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/FPS)
    
    # Temp file
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    
    print("Renderizando vídeo de alta fidelidade...")
    anim.save(temp_video, writer='ffmpeg', fps=FPS, 
              extra_args=['-vcodec', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p'],
              bitrate=BITRATE)
    plt.close()

    # Merge com Áudio
    final_output = output_path
    print("Fundindo com áudio original...")
    if os.path.exists(final_output): os.remove(final_output)
    cmd = [
        "ffmpeg", "-y",
        "-i", temp_video,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "256k",
        "-shortest",
        final_output
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if os.path.exists(temp_video): os.remove(temp_video)
    print(f"\n--- PRODUÇÃO CONCLUÍDA ---")
    print(f"Arquivo pronto para upload: {final_output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Input Audio File")
    parser.add_argument("-o", "--output", default="output_production.mp4", help="Output Video File")
    args = parser.parse_args()
    
    render_production_master(args.audio, args.output)
