import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import librosa
import os
import subprocess

# --- CONFIGURAÇÕES DE DRAMA CÓSMICO ---
AUDIO_INPUT = "instagram_video_20251229_152102 (1).mp3"
WIDTH, HEIGHT = 1080, 1920
DPI = 100
FPS = 60
DURATION_SEC = 20
NUM_DRONES = 1024
NUM_GALAXIES = 3

def analyze_audio(file_path):
    print(f"Sincronizando relógio atômico: {file_path}...")
    y, sr = librosa.load(file_path, sr=44100)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, np.ndarray): tempo = tempo[0]
    hop_len = int(sr / FPS)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop_len)[0]
    rms = (rms - np.min(rms)) / (np.max(rms) - np.min(rms) + 1e-6)
    return tempo, rms, len(y)/sr

# --- FÍSICA GALÁCTICA ---

def create_galaxy_centers():
    centers = []
    np.random.seed(77)
    for _ in range(NUM_GALAXIES):
        centers.append({
            'pos': (np.random.rand(3) - 0.5) * 6.0,
            'rot_axis': np.random.rand(3),
            'rot_speed': np.random.uniform(1.0, 3.0),
            'color': np.random.rand(3) # RGB
        })
    return centers

def get_galaxy_points(n_total, t, centers, collapse_factor):
    """
    n_total: drones
    collapse_factor: 0 (distribuído) a 1 (todos no black hole central)
    """
    points = np.zeros((n_total, 3))
    colors = np.zeros((n_total, 3))
    drones_per_galaxy = n_total // len(centers)
    
    for i, c in enumerate(centers):
        idx_start = i * drones_per_galaxy
        idx_end = (i + 1) * drones_per_galaxy
        n = idx_end - idx_start
        
        # Geometria Espiral Local
        indices = np.linspace(0.1, 1.0, n)
        angle = indices * 6 * np.pi + (t * c['rot_speed'])
        r = indices * 2.0 * (1 - collapse_factor) # Galáxia encolhe
        
        # Posição Relativa
        lx = r * np.cos(angle)
        ly = r * np.sin(angle)
        lz = np.sin(angle * 0.5) * 0.2
        local_points = np.column_stack((lx, ly, lz))
        
        # Rotação da Galáxia (Tilt)
        axis = c['rot_axis'] / np.linalg.norm(c['rot_axis'])
        theta = 0.5 # Tilt fixo
        ux, uy, uz = axis
        rot_mat = np.array([
            [np.cos(theta) + ux**2*(1-np.cos(theta)), ux*uy*(1-np.cos(theta))-uz*np.sin(theta), ux*uz*(1-np.cos(theta))+uy*np.sin(theta)],
            [uy*ux*(1-np.cos(theta))+uz*np.sin(theta), np.cos(theta)+uy**2*(1-np.cos(theta)), uy*uz*(1-np.cos(theta))-ux*np.sin(theta)],
            [uz*ux*(1-np.cos(theta))-uy*np.sin(theta), uz*uy*(1-np.cos(theta))+ux*np.sin(theta), np.cos(theta)+uz**2*(1-np.cos(theta))]
        ])
        local_points = np.dot(local_points, rot_mat.T)
        
        # Posição Final: Centro Local -> Centro Universal (0,0,0) conforme colapsa
        world_center = c['pos'] * (1 - collapse_factor)
        points[idx_start:idx_end] = local_points + world_center
        colors[idx_start:idx_end] = c['color']
        
    return points, colors

import argparse
import sys

def render_galactic_singularity(audio_path, output_path):
    if not os.path.exists(audio_path):
        print(f"Erro: {audio_path} não encontrado.")
        return

    bpm, rms_data, audio_dur = analyze_audio(audio_path)
    actual_dur = min(DURATION_SEC, audio_dur)
    total_frames = int(FPS * actual_dur)

    print(f"🌌 RENDERIZANDO GALACTIC SINGULARITY: {WIDTH}x{HEIGHT} @ 60fps")
    fig = plt.figure(figsize=(WIDTH/DPI, HEIGHT/DPI), dpi=DPI, facecolor='black')
    fig.subplots_adjust(0,0,1,1)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('black')
    ax.axis('off')
    ax.xaxis.set_pane_color((0,0,0,0)); ax.yaxis.set_pane_color((0,0,0,0)); ax.zaxis.set_pane_color((0,0,0,0))

    centers = create_galaxy_centers()
    current_pos = np.zeros((NUM_DRONES, 3))
    velocity = np.zeros((NUM_DRONES, 3))
    
    scat = ax.scatter([], [], [], s=30, edgecolors='white', linewidth=0.1, alpha=0.9)

    def update(frame):
        nonlocal current_pos, velocity
        t = frame / FPS
        progress = frame / total_frames
        intensity = rms_data[frame] if frame < len(rms_data) else 0
        
        # Lógica de Colapso (Singularidade)
        # O buraco negro começa a dominar após 60% do vídeo
        collapse_trigger = 0.6
        if progress < collapse_trigger:
            collapse_factor = 0
            black_hole_intensity = 0
        else:
            # Cresce exponencialmente
            collapse_factor = np.power((progress - collapse_trigger) / (1 - collapse_trigger), 2)
            black_hole_intensity = collapse_factor
            
        # Obter alvos galácticos
        target_pos, drone_colors = get_galaxy_points(NUM_DRONES, t, centers, collapse_factor)
        
        # Physics: Steering + Suction
        desired = target_pos - current_pos
        
        # Se o buraco negro estiver ativo, adiciona sucção em espiral para (0,0,0)
        if black_hole_intensity > 0:
            dist_to_center = np.linalg.norm(current_pos, axis=1, keepdims=True)
            suction_dir = -current_pos / (dist_to_center + 1e-6)
            # Tangente para espiral
            vortex_dir = np.column_stack((-current_pos[:,1], current_pos[:,0], np.zeros(NUM_DRONES)))
            vortex_dir /= (np.linalg.norm(vortex_dir, axis=1, keepdims=True) + 1e-6)
            
            suction_force = (suction_dir * 0.5 + vortex_dir * 0.3) * black_hole_intensity * 2.0
            desired += suction_force * 5.0 # Força bruta de sucção
            
        # Inércia
        smoothness = 0.1 + intensity * 0.1
        velocity = velocity * 0.85 + desired * smoothness
        current_pos += velocity
        
        # Spaghettification: Aceleração estica os drones (visual hack: tamanho)
        speed = np.linalg.norm(velocity, axis=1)
        # Mais perto do centro e mais rápido = mais "brilhante" e maior
        dynamic_sizes = 20 + speed * 50 * (1 + black_hole_intensity)
        
        # Cores: Tornam-se brancas/amarelas no horizonte de eventos
        final_colors = drone_colors.copy()
        glow = np.clip(speed * 3.0 * black_hole_intensity, 0, 1)
        final_colors[:, 0:3] = np.clip(final_colors[:, 0:3] + glow[:, None], 0, 1)
        
        scat._offsets3d = (current_pos[:,0], current_pos[:,1], current_pos[:,2])
        scat.set_color(final_colors)
        scat.set_sizes(dynamic_sizes)
        
        # Câmera Warp
        if progress < collapse_trigger:
            # Zoom out para mostrar as galáxias
            zoom = 4.0 + progress * 2.0
            ax.view_init(elev=20, azim=t*10)
        else:
            # Zoom in dramático na singularidade
            zoom = 6.0 - (progress - collapse_trigger) * 12.0
            zoom = max(0.5, zoom)
            shake = intensity * 0.5 * black_hole_intensity
            ax.view_init(elev=20 + np.sin(t*20)*shake, azim=t*20 + np.cos(t*20)*shake)

        ax.set_xlim(-zoom, zoom); ax.set_ylim(-zoom, zoom); ax.set_zlim(-zoom*1.3, zoom*1.3)
        
        return scat,

    anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/FPS)
    
    # Temp file
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    
    anim.save(temp_video, writer='ffmpeg', fps=FPS, bitrate=12000, 
              extra_args=['-vcodec', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p'])
    plt.close()

    print("Sincronia Final: Colapsando o Universo no Áudio...")
    if os.path.exists(output_path): os.remove(output_path)
    cmd = [
        "ffmpeg", "-y", "-i", temp_video, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if os.path.exists(temp_video): os.remove(temp_video)
    print(f"\n--- SINGULARIDADE CONCLUÍDA ---")
    print(f"Vídeo Master: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Input Audio File")
    parser.add_argument("-o", "--output", default="output_galactic.mp4", help="Output Video File")
    args = parser.parse_args()
    
    render_galactic_singularity(args.audio, args.output)
