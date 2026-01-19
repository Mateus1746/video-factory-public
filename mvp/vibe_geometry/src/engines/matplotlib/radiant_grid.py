import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import librosa
import os
import subprocess

# --- CONFIGURAÇÕES 'THE RADIANT GRID' ---
AUDIO_INPUT = "instagram_video_20251229_152102 (1).mp3"
NUM_DRONES = 300        # Quantidade ideal para clareza visual
FPS = 30
WIDTH, HEIGHT = 9, 16   # Proporção Viral (Reels/TikTok)
VIDEO_FILE = "radiant_temp.mp4"
FINAL_FILE = "The_Radiant_Grid_Show.mp4"

def analyze_audio(file_path):
    print(f"Analisando áudio: {file_path}...")
    y, sr = librosa.load(file_path, sr=44100)
    
    # BPM e Beats
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, np.ndarray): tempo = tempo[0]
    print(f"BPM Detectado: {tempo:.1f}")
    
    # RMS para Kick-Flash
    hop_len = int(sr / FPS)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop_len)[0]
    rms = (rms - np.min(rms)) / (np.max(rms) - np.min(rms) + 1e-6)
    
    return tempo, rms, len(y)/sr

# --- BIBLIOTECA DE FORMAS GEOMÉTRICAS (ORDEM) ---
def get_chaos():
    return (np.random.rand(NUM_DRONES, 3) - 0.5) * 4

def get_sphere():
    indices = np.arange(0, NUM_DRONES, dtype=float) + 0.5
    phi = np.arccos(1 - 2*indices/NUM_DRONES)
    theta = np.pi * (1 + 5**0.5) * indices
    return np.column_stack((np.cos(theta) * np.sin(phi), np.sin(theta) * np.sin(phi), np.cos(phi))) * 0.9

def get_cube():
    # Grid 3D perfeito
    side = int(np.power(NUM_DRONES, 1/3))
    x, y, z = np.indices((side, side, side))
    coords = (np.column_stack((x.flatten(), y.flatten(), z.flatten())) - side/2) / (side/2)
    # Complementar se necessário
    if coords.shape[0] < NUM_DRONES:
        extra = (np.random.rand(NUM_DRONES - coords.shape[0], 3) - 0.5) * 2
        coords = np.vstack((coords, extra))
    return coords[:NUM_DRONES] * 0.8

def get_pyramid():
    # Base quadrada + topo
    pts = []
    base_size = int(np.sqrt(NUM_DRONES * 0.8))
    for i in range(base_size):
        for j in range(base_size):
            pts.append([i/base_size - 0.5, -0.5, j/base_size - 0.5])
    
    # Lados subindo para o topo (0, 0.7, 0)
    top = [0, 0.7, 0]
    while len(pts) < NUM_DRONES:
        t = np.random.rand()
        base_pt = pts[np.random.randint(0, len(pts))]
        pts.append([base_pt[0]*(1-t), -0.5*(1-t) + 0.7*t, base_pt[2]*(1-t)])
    return np.array(pts[:NUM_DRONES])

def get_ring():
    angles = np.linspace(0, 2*np.pi, NUM_DRONES)
    return np.column_stack((np.cos(angles)*1.2, np.zeros(NUM_DRONES), np.sin(angles)*1.2))

# --- COREOGRAFIA 'SNAP' ---
CHOREOGRAPHY = [
    (get_chaos, 4),      # Início confuso
    (get_sphere, 6),     # Ordem esférica
    (get_chaos, 2),      # Explosão rápida
    (get_cube, 6),       # Ordem cúbica
    (get_pyramid, 8),    # Geometria complexa
    (get_ring, 6),       # Anel Final
    (get_chaos, 4)       # Dispersão
]

import argparse
import sys

def create_radiant_grid(audio_path, output_path):
    print("Iniciando 'The Radiant Grid' Rendering...")
    
    bpm, rms_data, total_duration = analyze_audio(audio_path)
    
    fig = plt.figure(figsize=(WIDTH, HEIGHT), facecolor='black')
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('black')
    ax.grid(False)
    ax.set_axis_off()
    
    # Remover panes
    ax.xaxis.set_pane_color((0,0,0,0)); ax.yaxis.set_pane_color((0,0,0,0)); ax.zaxis.set_pane_color((0,0,0,0))

    beat_frames = int(60 / bpm * FPS)
    
    # Sequência de alvos frame a frame
    target_sequence = []
    for shape_func, beats in CHOREOGRAPHY:
        target_shape = shape_func()
        for _ in range(beats * beat_frames):
            target_sequence.append(target_shape)
    
    total_frames = min(len(target_sequence), int(total_duration * FPS))
    current_pos = get_chaos()
    
    # Drones: Core (Branco) + Glow (Neon Cyan)
    # Camada 1: Glow exterior
    glow = ax.scatter(current_pos[:,0], current_pos[:,1], current_pos[:,2], 
                      c='#00f2ff', s=40, alpha=0.3, edgecolors='none', depthshade=True)
    # Camada 2: Core brilhante
    core = ax.scatter(current_pos[:,0], current_pos[:,1], current_pos[:,2], 
                      c='white', s=8, alpha=0.9, edgecolors='none', depthshade=True)

    def update(frame):
        nonlocal current_pos
        
        target = target_sequence[frame]
        intensity = rms_data[frame] if frame < len(rms_data) else 0
        
        # --- MOVIMENTO SNAP (Suave mas Intencional) ---
        # Interpolação Linear com aceleração baseada no beat
        lerp_speed = 0.12 + intensity * 0.1
        current_pos += (target - current_pos) * lerp_speed
        
        # --- CÂMERA DINÂMICA ---
        # Rotação suave em torno do centro
        ax.view_init(elev=15 + np.sin(frame*0.04)*10, azim=frame * 1.2)
        
        # --- KICK-FLASH (REAÇÃO AO SOM) ---
        # Spike no tamanho e brilho
        flash_size_factor = 1 + intensity * 2.5
        flash_alpha_factor = 0.3 + intensity * 0.7
        
        # Update Visuals
        # Aplicamos profundidade manual simulada pelo scatter (depthshade=True ajuda)
        glow._offsets3d = (current_pos[:,0], current_pos[:,1], current_pos[:,2])
        core._offsets3d = (current_pos[:,0], current_pos[:,1], current_pos[:,2])
        
        glow.set_sizes(np.full(NUM_DRONES, 50 * flash_size_factor))
        glow.set_alpha(flash_alpha_factor * 0.4)
        
        core.set_sizes(np.full(NUM_DRONES, 10 * (1 + intensity * 1.2)))
        core.set_alpha(np.clip(0.8 + intensity * 0.2, 0, 1))
        
        # Cor varia levemente entre Cyan e Violet no Beat
        glow_color = plt.cm.cool(0.3 + intensity * 0.4)
        glow.set_facecolor(glow_color)
        
        return glow, core

    print(f"Renderizando {total_frames} frames de ordem e significado...")
    anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/FPS, blit=False)
    
    # Temp file
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    anim.save(temp_video, writer='ffmpeg', fps=FPS, bitrate=10000)
    plt.close()
    
    print("Sincronia Final: Onde a Ordem encontra o Ritmo...")
    if os.path.exists(output_path): os.remove(output_path)
    cmd = [
        "ffmpeg", "-y",
        "-i", temp_video,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if os.path.exists(temp_video): os.remove(temp_video)
    print(f"\n--- RADIAÇÃO CONCLUÍDA ---")
    print(f"Arquivo final: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Input Audio File")
    parser.add_argument("-o", "--output", default="output_radiant.mp4", help="Output Video File")
    args = parser.parse_args()
    
    if not os.path.exists(args.audio):
        print(f"Erro: {args.audio} não encontrado.")
    else:
        create_radiant_grid(args.audio, args.output)
