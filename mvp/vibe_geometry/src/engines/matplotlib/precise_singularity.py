import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
from mpl_toolkits.mplot3d import Axes3D
import librosa
import os
import subprocess

# --- CONFIGURAÇÕES DE PRECISÃO CÓSMICA ---
AUDIO_INPUT = "instagram_video_20251229_152102 (1).mp3"
WIDTH, HEIGHT = 1080, 1920
DPI = 100
FPS = 60
DURATION_SEC = 22 # Um pouco mais longo para o nascimento gradual
NUM_DRONES_PER_GALAXY = 256
NUM_CENTRAL_DRONES = 256
TOTAL_DRONES = (NUM_DRONES_PER_GALAXY * 3) + NUM_CENTRAL_DRONES

def analyze_audio(file_path):
    print(f"Calibrando frequências cósmicas: {file_path}...")
    y, sr = librosa.load(file_path, sr=44100)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, np.ndarray): tempo = tempo[0]
    hop_len = int(sr / FPS)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop_len)[0]
    rms = (rms - np.min(rms)) / (np.max(rms) - np.min(rms) + 1e-6)
    return tempo, rms, len(y)/sr

# --- DEFINIÇÕES DOS CENTROS ---
CORNER_CENTERS = [
    np.array([-3.0, 3.0, 2.0]),  # Superior Esquerdo
    np.array([3.0, 3.0, -2.0]),  # Superior Direito
    np.array([0.0, -4.0, 0.0])   # Inferior Central
]
COLORS = ['#00F0FF', '#FF00FF', '#00FF99'] # Ciano, Magenta, Esmeralda

import argparse
import sys

def render_precise_singularity(audio_path, output_path):
    if not os.path.exists(audio_path):
        print(f"Erro: {audio_path} não encontrado.")
        return

    bpm, rms_data, audio_dur = analyze_audio(audio_path)
    actual_dur = min(DURATION_SEC, audio_dur)
    total_frames = int(FPS * actual_dur)

    print(f"🌌 RENDERIZANDO PRECISE SINGULARITY: {WIDTH}x{HEIGHT} @ 60fps")
    fig = plt.figure(figsize=(WIDTH/DPI, HEIGHT/DPI), dpi=DPI, facecolor='black')
    fig.subplots_adjust(0,0,1,1)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('black')
    ax.axis('off')
    ax.xaxis.set_pane_color((0,0,0,0)); ax.yaxis.set_pane_color((0,0,0,0)); ax.zaxis.set_pane_color((0,0,0,0))

    # Estado Inicial
    positions = np.zeros((TOTAL_DRONES, 3))
    colors = np.zeros((TOTAL_DRONES, 4)) # RGBA
    active_mask = np.zeros(TOTAL_DRONES, dtype=bool)
    
    scat = ax.scatter([], [], [], s=30, edgecolors='white', linewidth=0.1)

    def update(frame):
        nonlocal positions, colors, active_mask
        t = frame / FPS
        progress = frame / total_frames
        intensity = rms_data[frame] if frame < len(rms_data) else 0
        
        # --- TIMELINE ---
        # 0.0 to 0.5: Nascimento gradual galáxias
        # 0.5 to 0.6: Estabilização
        # 0.6: Enxame central aparece
        # 0.6 to 1.0: Colapso orbital
        
        # 1. ATIVAÇÃO GRADUAL (Nascimento)
        if progress < 0.5:
            # Ativa drones um por um baseado no progresso
            max_to_activate = int(progress / 0.5 * (NUM_DRONES_PER_GALAXY * 3))
            active_mask[:max_to_activate] = True
            
        # 2. APARECIMENTO DO ENXAME CENTRAL (Jump cut / Burst)
        if progress >= 0.6:
            active_mask[NUM_DRONES_PER_GALAXY*3:] = True
            
        # 3. FÍSICA DE MOVIMENTO
        # Galáxias dos Cantos
        collapse_factor = np.power(max(0, (progress - 0.65) / 0.35), 2)
        
        for g in range(3):
            idx_start = g * NUM_DRONES_PER_GALAXY
            idx_end = (g + 1) * NUM_DRONES_PER_GALAXY
            mask = active_mask[idx_start:idx_end]
            if not np.any(mask): continue
            
            # Geometria Espiral
            indices = np.linspace(0.1, 1.0, NUM_DRONES_PER_GALAXY)[mask]
            angle = indices * 8 * np.pi + (t * 2.5)
            r = indices * 2.2 * (1 - collapse_factor)
            
            lx = r * np.cos(angle)
            ly = r * np.sin(angle)
            lz = np.sin(angle * 0.5) * 0.2
            
            # Centro da galáxia se move para o centro universal (0,0,0) na queda
            center = CORNER_CENTERS[g] * (1 - collapse_factor)
            
            # Se colapsando, adicionamos a órbita circular ao redor do centro universal (0,0,0)
            if collapse_factor > 0:
                orbit_angle = t * 1.5 + g * (2*np.pi/3)
                orbit_r = np.linalg.norm(CORNER_CENTERS[g]) * (1 - collapse_factor)
                center_x = orbit_r * np.cos(orbit_angle)
                center_y = orbit_r * np.sin(orbit_angle)
                center = np.array([center_x, center_y, center[2]])
            
            positions[idx_start:idx_end][mask] = np.column_stack((lx, ly, lz)) + center
            
            # Cores das Galáxias
            c_base = mcolors.to_rgba(COLORS[g])
            colors[idx_start:idx_end][mask] = c_base
            # Glow no colapso
            colors[idx_start:idx_end][mask, 0:3] += collapse_factor * 0.4

        # Enxame Central
        if progress >= 0.6:
            idx_start = NUM_DRONES_PER_GALAXY * 3
            mask = active_mask[idx_start:]
            
            # Rotação ultra rápida
            indices = np.linspace(0, 1, NUM_CENTRAL_DRONES)
            angle = indices * 4 * np.pi + (t * 20.0) # Muito rápido
            # Respira com o audio
            r = (0.2 + indices * 0.6) * (1.0 + intensity * 0.5)
            
            cx = r * np.cos(angle)
            cy = r * np.sin(angle)
            cz = (np.random.rand(NUM_CENTRAL_DRONES) - 0.5) * 0.8
            
            positions[idx_start:] = np.column_stack((cx, cy, cz))
            # Branco/Dourado brilhante
            colors[idx_start:] = [1, 1, 0.7, 1] 

        # --- VISUALIZAÇÃO ---
        final_colors = np.clip(colors[active_mask], 0, 1)
        scat._offsets3d = (positions[:,0][active_mask], positions[:,1][active_mask], positions[:,2][active_mask])
        scat.set_color(final_colors)
        
        # Tamanho dinâmico (Kick/RMS)
        base_size = 30
        dynamic_size = base_size * (1.0 + intensity * 1.5)
        scat.set_sizes(np.full(np.sum(active_mask), dynamic_size))

        # --- CÂMERA ---
        if progress < 0.6:
            # Pan cinematográfico entre os nascimentos
            ax.view_init(elev=30, azim=t*8)
            zoom = 4.5
        else:
            # Zoom In e Shake
            zoom = 4.5 - (progress - 0.6) * 10.0
            zoom = max(0.4, zoom)
            shake = intensity * 0.8 * collapse_factor
            ax.view_init(elev=30 + np.sin(t*30)*shake, azim=t*15 + np.cos(t*30)*shake)
            
        ax.set_xlim(-zoom, zoom); ax.set_ylim(-zoom, zoom); ax.set_zlim(-zoom*1.3, zoom*1.3)

        return scat,

    anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/FPS)
    
    # Temp file
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    
    anim.save(temp_video, writer='ffmpeg', fps=FPS, bitrate=12000, 
              extra_args=['-vcodec', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p'])
    plt.close()

    print("Sincronia Final: Ativando Nascimento e Queda...")
    if os.path.exists(output_path): os.remove(output_path)
    cmd = [
        "ffmpeg", "-y", "-i", temp_video, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if os.path.exists(temp_video): os.remove(temp_video)
    print(f"\n--- COREOGRAFIA PRECISA CONCLUÍDA ---")
    print(f"Vídeo Master: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Input Audio File")
    parser.add_argument("-o", "--output", default="output_precise.mp4", help="Output Video File")
    args = parser.parse_args()
    
    render_precise_singularity(args.audio, args.output)
