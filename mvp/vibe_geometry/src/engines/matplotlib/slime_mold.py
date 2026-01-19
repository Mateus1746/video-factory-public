import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.spatial import cKDTree
import librosa
import os
import subprocess

# --- CONFIGURAÇÕES DO SLIME MOLD ---
WIDTH, HEIGHT = 1080, 1920
DPI = 100
FPS = 60 
NUM_AGENTS = 1200
SENSOR_DIST = 0.18 # Raio de percepção
AUDIO_PATH = "/home/mateus/projetos/orquestrador/youtube/Harmonic Pendulum Waves/instagram_video_20251229_152102 (1).mp3"

# --- 1. ANÁLISE DE NUTRIENTES (ÁUDIO) ---
def analyze_audio_slime(file_path):
    print(f"🦠 Extraindo nutrientes de: {os.path.basename(file_path)}...")
    y, sr = librosa.load(file_path, sr=44100)
    rms = librosa.feature.rms(y=y)[0]
    # Onsets para as trocas de cor
    onsets = librosa.onset.onset_strength(y=y, sr=sr)
    duration = librosa.get_duration(y=y, sr=sr)
    return y, sr, rms, onsets, duration

# --- 2. ENGINE BIOLÓGICA ---
import argparse
import sys

def render_slime_mold_master(audio_path, output_path):
    if not os.path.exists(audio_path):
        print(f"Erro: {audio_path} não encontrado.")
        return

    y_audio, sr_audio, rms, onsets, duration = analyze_audio_slime(audio_path)
    audio_time = np.linspace(0, duration, len(rms))
    
    print(f"🟢 CULTIVANDO REDE VIVA ({duration:.1f}s)...")
    
    fig = plt.figure(figsize=(WIDTH/DPI, HEIGHT/DPI), dpi=DPI, facecolor='black')
    ax = fig.add_axes([0, 0, 1, 1], xlim=(-2, 2), ylim=(-2 * 1.77, 2 * 1.77))
    ax.set_facecolor('black')
    ax.axis('off')
    
    # Inicialização: Círculo concentrado
    angles = np.random.rand(NUM_AGENTS) * 2 * np.pi
    radii = np.sqrt(np.random.rand(NUM_AGENTS)) * 1.2
    pos = np.column_stack((radii * np.cos(angles), radii * np.sin(angles) * 1.5))
    
    # Velocidades iniciais aleatórias
    vel = (np.random.rand(NUM_AGENTS, 2) - 0.5) * 0.05
    
    scat = ax.scatter(pos[:,0], pos[:,1], s=5, c='#00FF00', alpha=0.45, edgecolors='none')

    # Estado de cor persistente
    current_color_r = 0.0
    current_color_b = 0.0

    def update(frame):
        nonlocal pos, vel, current_color_r, current_color_b
        t = frame / FPS
        if t > duration: t = duration
        
        # 1. Sync Áudio
        vol = np.interp(t, audio_time, rms) * 8.0
        beat = np.interp(t, audio_time, onsets)
        
        # 2. IA de Proximidade (cKDTree)
        tree = cKDTree(pos)
        # Buscar o vizinho mais próximo dentro do raio de sensor
        dists, idxs = tree.query(pos, k=2, distance_upper_bound=SENSOR_DIST)
        
        neighbor_idx = idxs[:, 1]
        valid_mask = (neighbor_idx < NUM_AGENTS)
        
        # Atração para vizinhos
        if np.any(valid_mask):
            targets = pos[neighbor_idx[valid_mask]]
            steer = targets - pos[valid_mask]
            norm = np.linalg.norm(steer, axis=1, keepdims=True)
            steer = np.divide(steer, norm, where=norm!=0)
            
            # Steer strength cresce com o volume da música
            strength = 0.08 * (1.0 + vol)
            vel[valid_mask] += steer * strength
        
        # Inércia e Normalização de Velocidade
        speed = 0.025 * (1.1 + vol * 0.5)
        v_norm = np.linalg.norm(vel, axis=1, keepdims=True)
        vel = np.divide(vel, v_norm, where=v_norm!=0) * speed
        
        # Jitter de exploração (Aumenta na calmaria)
        jitter_amt = 0.005 / (0.1 + vol)
        vel += (np.random.rand(NUM_AGENTS, 2) - 0.5) * jitter_amt
        
        # Movimentação
        pos += vel
        
        # 3. Toroide (Continuidade Infinita)
        pos[:, 0] = ((pos[:, 0] + 2.0) % 4.0) - 2.0
        pos[:, 1] = ((pos[:, 1] + 3.5) % 7.0) - 3.5
        
        # 4. Engine de Cores (Nutrientes Pulsantes)
        # Onsets transformam Verde -> Amarelo -> Branco
        if beat > 2.5:
            current_color_r = np.clip(current_color_r + 0.15, 0, 1)
            current_color_b = np.clip(current_color_b + 0.05, 0, 0.4)
        else:
            current_color_r *= 0.98 # Decaimento para verde
            current_color_b *= 0.96
            
        colors = np.zeros((NUM_AGENTS, 4))
        colors[:, 0] = current_color_r # Vermelho injetado (V+G=Amarelo)
        colors[:, 1] = 1.0            # Verde (Base Slimy)
        colors[:, 2] = current_color_b # Azul (Injetado para branco)
        colors[:, 3] = np.clip(0.35 + vol * 0.2, 0.2, 0.7) # Rastro mais denso no volume
        
        scat.set_offsets(pos)
        scat.set_color(colors)
        scat.set_sizes(np.full(NUM_AGENTS, 4 + vol * 8)) # Partículas pulsam
        
        # 5. Câmera Dinâmica
        zoom = 1.8 + np.sin(t * 0.5) * 0.1
        ax.set_xlim(-zoom, zoom)
        ax.set_ylim(-zoom * 1.77, zoom * 1.77)
        
        return scat,

    total_frames = int(FPS * duration)
    print(f"🎬 Orquestrando {total_frames} frames de Rede Slime...")
    anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/FPS)
    
    # Temp file
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    anim.save(temp_video, writer='ffmpeg', fps=FPS, bitrate=12000,
              extra_args=['-vcodec', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p'])
    plt.close()

    print("Sincronia Final: Fundindo Áudio e Rede Biológica...")
    if os.path.exists(output_path): os.remove(output_path)
    cmd = [
        "ffmpeg", "-y", "-i", temp_video, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if os.path.exists(temp_video): os.remove(temp_video)
    
    print(f"\n--- SLIME NETWORK CONCLUÍDA ---")
    print(f"Vídeo Master Final: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Input Audio File")
    parser.add_argument("-o", "--output", default="output_slime_mold.mp4", help="Output Video File")
    args = parser.parse_args()
    
    render_slime_mold_master(args.audio, args.output)
