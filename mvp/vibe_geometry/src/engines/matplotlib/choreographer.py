import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import librosa
import os
import subprocess

# --- CONFIGURAÇÕES ---
AUDIO_INPUT = "instagram_video_20251229_152102 (1).mp3"
NUM_DRONES = 400       
FPS = 30
TRANSITION_SPEED = 0.1 # Suavidade do Lerp
VIDEO_FILE = "choreography_temp.mp4"
FINAL_FILE = "3D_Swarm_Choreographer_Final.mp4"

def analyze_audio(file_path):
    print(f"Analisando áudio: {file_path}...")
    y, sr = librosa.load(file_path, sr=44100)
    
    # 1. Detectar BPM
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, np.ndarray):
        tempo = tempo[0]
    print(f"BPM Detectado: {tempo:.1f}")
    
    # 2. Calcular intensidade (RMS) por frame
    hop_len = int(sr / FPS)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop_len)[0]
    rms = (rms - np.min(rms)) / (np.max(rms) - np.min(rms) + 1e-6)
    
    return tempo, rms, len(y)/sr

# --- BIBLIOTECA DE FORMAS ---
def get_random_chaos():
    return (np.random.rand(NUM_DRONES, 3) - 0.5) * 4

def get_sphere():
    indices = np.arange(0, NUM_DRONES, dtype=float) + 0.5
    phi = np.arccos(1 - 2*indices/NUM_DRONES)
    theta = np.pi * (1 + 5**0.5) * indices
    return np.column_stack((np.cos(theta) * np.sin(phi), np.sin(theta) * np.sin(phi), np.cos(phi)))

def get_cube():
    side = int(np.cbrt(NUM_DRONES))
    x, y, z = np.indices((side, side, side))
    coords = np.column_stack((x.flatten(), y.flatten(), z.flatten()))
    coords = (coords - side/2) / (side/2)
    if coords.shape[0] < NUM_DRONES:
        extra = (np.random.rand(NUM_DRONES - coords.shape[0], 3) - 0.5) * 2
        coords = np.vstack((coords, extra))
    return coords[:NUM_DRONES]

def get_saturn_rings():
    split = int(NUM_DRONES * 0.6)
    indices = np.arange(0, split, dtype=float) + 0.5
    phi = np.arccos(1 - 2*indices/split)
    theta = np.pi * (1 + 5**0.5) * indices
    sphere = np.column_stack((np.cos(theta) * np.sin(phi) * 0.6, np.sin(theta) * np.sin(phi) * 0.6, np.cos(phi) * 0.6))
    
    ring_count = NUM_DRONES - split
    angles = np.linspace(0, 2*np.pi, ring_count)
    ring = np.column_stack((np.cos(angles) * 1.3, np.sin(angles) * 1.3, np.random.randn(ring_count) * 0.05))
    return np.vstack((sphere, ring))

def get_double_helix():
    t = np.linspace(0, 4*np.pi, NUM_DRONES)
    x = np.cos(t) * 0.7
    y = np.sin(t) * 0.7
    z = np.linspace(-1.2, 1.2, NUM_DRONES)
    return np.column_stack((x, y, z))

# --- COREOGRAFIA ---
# (Função, Batidas)
CHOREOGRAPHY_PLAN = [
    (get_random_chaos, 4),
    (get_sphere, 4),
    (get_random_chaos, 2),
    (get_cube, 4),
    (get_double_helix, 8),
    (get_saturn_rings, 8),
    (get_random_chaos, 4)
]

import argparse
import sys

def create_show(audio_path, output_path):
    print("Iniciando Coreografia 3D...")
    
    bpm, rms_data, total_duration = analyze_audio(audio_path)
    
    fig = plt.figure(figsize=(10, 10), facecolor='black')
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('black')
    ax.grid(False)
    ax.set_axis_off()
    
    # Remover bordas
    ax.xaxis.set_pane_color((0,0,0,0))
    ax.yaxis.set_pane_color((0,0,0,0))
    ax.zaxis.set_pane_color((0,0,0,0))

    beat_frames = int(60 / bpm * FPS)
    
    # Gerar sequência de alvos
    target_sequence = []
    for shape_func, beats in CHOREOGRAPHY_PLAN:
        target_shape = shape_func()
        for _ in range(beats * beat_frames):
            target_sequence.append(target_shape)
    
    total_frames = min(len(target_sequence), int(total_duration * FPS))
    current_pos = get_random_chaos()
    
    # Usar scatter com cores hsv radiais
    scat = ax.scatter(current_pos[:,0], current_pos[:,1], current_pos[:,2], 
                      c='cyan', s=5, depthshade=True, edgecolors='none')

    def animate(frame):
        nonlocal current_pos
        
        target = target_sequence[frame]
        intensity = rms_data[frame] if frame < len(rms_data) else 0
        
        # Interpolação com efeito de snap (acelera se longe)
        diff = target - current_pos
        current_pos += diff * (TRANSITION_SPEED + intensity * 0.1)
        
        # Rotação da Câmera
        ax.view_init(elev=20 + np.sin(frame*0.05)*10, azim=frame * 0.8)
        
        # Efeito Visual: Cor e Tamanho reativos
        dist = np.linalg.norm(current_pos, axis=1)
        norm_dist = dist / (np.max(dist) + 1e-6)
        colors = plt.cm.hsv(norm_dist * 0.8 + intensity * 0.2)
        
        scat._offsets3d = (current_pos[:,0], current_pos[:,1], current_pos[:,2])
        scat.set_color(colors)
        # Tamanho maior no beat
        scat.set_sizes(np.full(NUM_DRONES, 5 + intensity * 25))
        
        return scat,

    print(f"Renderizando {total_frames} frames reativos...")
    anim = animation.FuncAnimation(fig, animate, frames=total_frames, interval=1000/FPS, blit=False)
    
    # Temp file
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    anim.save(temp_video, writer='ffmpeg', fps=FPS, bitrate=10000)
    plt.close()
    
    print("Mixagem final com o áudio do Instagram...")
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
    print(f"\n--- SHOW CONCLUÍDO ---")
    print(f"Arquivo final: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Input Audio File")
    parser.add_argument("-o", "--output", default="output_choreography.mp4", help="Output Video File")
    args = parser.parse_args()
    
    if not os.path.exists(args.audio):
        print(f"Erro: {args.audio} não encontrado.")
    else:
        create_show(args.audio, args.output)
