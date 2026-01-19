import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import librosa
import os
import subprocess

# --- CONFIGURAÇÕES DE SINFONIA VISUAL ---
AUDIO_INPUT = "instagram_video_20251229_152102 (1).mp3"
WIDTH, HEIGHT = 1080, 1920
DPI = 100
FPS = 60
DURATION_SEC = 20
NUM_PER_SWARM = 250 # 750 drones totais

# Palette Cyber-Orchestra
COLOR_MELODY = '#00F0FF'  # Ciano Elétrico
COLOR_BASS   = '#FF0055'  # Magenta Profundo
COLOR_HARMONY= '#FFCC00'  # Dourado

def analyze_audio(file_path):
    print(f"Afinando instrumentos: Analisando {file_path}...")
    y, sr = librosa.load(file_path, sr=44100)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, np.ndarray): tempo = tempo[0]
    
    hop_len = int(sr / FPS)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop_len)[0]
    rms = (rms - np.min(rms)) / (np.max(rms) - np.min(rms) + 1e-6)
    return tempo, rms, len(y)/sr

# --- MATEMÁTICA DAS FORMAS VOLUMÉTRICAS ---
def get_flower_of_life(n, t, layer):
    indices = np.linspace(0, 2*np.pi, n)
    if layer == 0:
        r = 1.0 + 0.15 * np.sin(t * 8)
        x = r * np.cos(indices * 3 + t) * np.cos(indices)
        y = r * np.sin(indices * 3 + t) * np.cos(indices)
        z = np.sin(indices * 4 + t) * 0.4
    elif layer == 1:
        r = 2.0 + 0.1 * np.cos(t * 2)
        x = r * np.cos(indices + t*0.5)
        y = r * np.sin(indices + t*0.5)
        z = np.sin(indices * 6) * 0.3
    else:
        h = np.linspace(-2.2, 2.2, n)
        r = 1.6 * (1 - np.abs(h)/3.2)
        theta = indices * 5 + t
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        z = h
    return np.column_stack((x, y, z))

def get_galaxy_flow(n, t, layer):
    indices = np.linspace(0.1, 1.0, n)
    angle = indices * 5 * np.pi + (t * 0.6)
    if layer == 0:
        r = indices * 1.6
        z = np.sin(angle) * 0.4
    elif layer == 1:
        r = indices * 3.2 + 0.4
        angle -= 0.6
        z = np.cos(angle * 1.5) * 0.6
    else:
        r = 1.2 + np.sin(indices * 8 + t) * 0.5
        z = np.linspace(-3.5, 3.5, n)
        angle = t * 1.2
    return np.column_stack((r * np.cos(angle), r * np.sin(angle), z))

def get_heart_beat(n, t, layer, intensity):
    # Batida real baseada no audio + pulso cardíaco matemático
    beat = (np.power(np.sin(t * 3.2), 64) * 0.4 + 1.0) * (1.0 + intensity * 0.25)
    u = np.linspace(0, 2*np.pi, n)
    v = np.linspace(0, np.pi, n)
    np.random.shuffle(v) # Volume interno
    
    x = 16 * np.sin(v)**3
    y = 13 * np.cos(v) - 5 * np.cos(2*v) - 2 * np.cos(3*v) - np.cos(4*v)
    z = np.sin(u) * 10
    
    scale = 0.09 * beat
    if layer == 0: scale *= 0.7
    elif layer == 1: scale *= 1.25
    else: scale *= 1.0; z = (np.random.rand(n)-0.5)*20
    
    points = np.column_stack((x, y, z)) * scale
    rot = t * 0.5
    c, s = np.cos(rot), np.sin(rot)
    Rx = np.array([[1,0,0],[0,c,-s],[0,s,c]])
    return np.dot(points, Rx)

import argparse
import sys

def render_harmonic_flow(audio_path, output_path):
    if not os.path.exists(audio_path):
        print(f"Erro: {audio_path} não encontrado.")
        return

    bpm, rms_data, audio_dur = analyze_audio(audio_path)
    actual_dur = min(DURATION_SEC, audio_dur)
    total_frames = int(FPS * actual_dur)

    print(f"🎵 RENDERIZANDO HARMONIC FLOW: {WIDTH}x{HEIGHT} @ 60fps")
    
    fig = plt.figure(figsize=(WIDTH/DPI, HEIGHT/DPI), dpi=DPI, facecolor='black')
    fig.subplots_adjust(0,0,1,1)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('black')
    ax.axis('off')
    ax.xaxis.set_pane_color((0,0,0,0)); ax.yaxis.set_pane_color((0,0,0,0)); ax.zaxis.set_pane_color((0,0,0,0))

    pos = [np.zeros((NUM_PER_SWARM, 3)) for _ in range(3)]
    scats = []
    colors = [COLOR_MELODY, COLOR_BASS, COLOR_HARMONY]
    base_sizes = [28, 45, 18]
    for i in range(3):
        s = ax.scatter([], [], [], c=colors[i], s=base_sizes[i], edgecolors='white', lw=0.1, alpha=0.85)
        scats.append(s)

    def update(frame):
        t_sec = frame / FPS
        progress = frame / total_frames
        intensity = rms_data[frame] if frame < len(rms_data) else 0
        
        # Beat Impulse Simulado para visual breath
        beat_phase = (t_sec * (bpm/60)) % 1.0
        beat_impulse = np.exp(-6 * beat_phase)
        total_intensity = max(intensity, beat_impulse)
        
        # Timeline
        if progress < 0.35:
            targets = [get_flower_of_life(NUM_PER_SWARM, t_sec, i) for i in range(3)]
            zoom = 3.2
            ax.view_init(elev=25, azim=t_sec * 12)
        elif progress < 0.7:
            targets = [get_galaxy_flow(NUM_PER_SWARM, t_sec, i) for i in range(3)]
            zoom = 3.8
            ax.view_init(elev=12 + np.sin(t_sec)*8, azim=t_sec * 18)
        else:
            targets = [get_heart_beat(NUM_PER_SWARM, t_sec, i, intensity) for i in range(3)]
            zoom = 3.6 - (progress - 0.7) * 0.8
            ax.view_init(elev=20, azim=45 + np.sin(t_sec*0.5)*10)

        # Physics Flow
        smoothness = 0.08 + total_intensity * 0.05
        for i in range(3):
            target = targets[i] * (1.0 + 0.12 * total_intensity)
            turbulence = np.sin(pos[i] * 2.5 + t_sec) * 0.025
            pos[i] = pos[i] * (1 - smoothness) + (target + turbulence) * smoothness
            
            scats[i]._offsets3d = (pos[i][:,0], pos[i][:,1], pos[i][:,2])
            scats[i].set_sizes(np.full(NUM_PER_SWARM, base_sizes[i] * (1 + total_intensity * 1.6)))
            scats[i].set_alpha(0.7 + total_intensity * 0.3)

        ax.set_xlim(-zoom, zoom); ax.set_ylim(-zoom, zoom); ax.set_zlim(-zoom*1.2, zoom*1.2)
        return scats

    anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/FPS)
    
    # Use output filename for temp to avoid collisions
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    
    anim.save(temp_video, writer='ffmpeg', fps=FPS, bitrate=12000, 
              extra_args=['-vcodec', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p'])
    plt.close()

    print("Mixagem Final: O Coral de Luz está pronto.")
    if os.path.exists(output_path): os.remove(output_path)
    cmd = [
        "ffmpeg", "-y", "-i", temp_video, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if os.path.exists(temp_video): os.remove(temp_video)
    print(f"\n--- SINFONIA CONCLUÍDA ---")
    print(f"Vídeo Master: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Input Audio File")
    parser.add_argument("-o", "--output", default="output_harmonic.mp4", help="Output Video File")
    args = parser.parse_args()
    
    render_harmonic_flow(args.audio, args.output)
