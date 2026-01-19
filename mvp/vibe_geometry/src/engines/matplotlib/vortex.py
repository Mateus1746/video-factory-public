import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import librosa
import os
import subprocess
import argparse
import sys

# --- CONFIGURAÇÕES DE ALTA OCTANAGEM ---
WIDTH_PX, HEIGHT_PX = 1080, 1920
DPI = 100
FPS = 60
NUM_DRONES_PER_GROUP = 200 # Total 600

# Cores Neon Cyberpunk
C_RED   = '#FF0040'
C_CYAN  = '#00F0FF'
C_LIME  = '#CCFF00'

def analyze_audio(file_path):
    print(f"Analisando áudio para o Vortex Engine: {file_path}...")
    y, sr = librosa.load(file_path, sr=44100)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, np.ndarray): tempo = tempo[0]
    
    hop_len = int(sr / FPS)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop_len)[0]
    rms = (rms - np.min(rms)) / (np.max(rms) - np.min(rms) + 1e-6)
    return tempo, rms, len(y)/sr

# --- MATEMÁTICA DE VÓRTICE E FORMAS ---
def get_tornado_formation(n, group_id):
    t = np.linspace(0, 8*np.pi, n)
    phase = group_id * (2*np.pi / 3) 
    z = np.linspace(-3, 3, n)
    r = 1.5 * (1 - np.abs(z)/4)
    return np.column_stack((r * np.cos(t + phase), r * np.sin(t + phase), z))

def get_implosion_core(n, group_id):
    indices = np.arange(0, n, dtype=float) + 0.5
    phi = np.arccos(1 - 2*indices/n)
    theta = np.pi * (1 + 5**0.5) * indices
    r = 0.5 + (group_id * 0.2) 
    return np.column_stack((r * np.cos(theta) * np.sin(phi), r * np.sin(theta) * np.sin(phi), r * np.cos(phi)))

def get_expansion_ring(n, group_id):
    t = np.linspace(0, 2*np.pi, n)
    r = 2.8
    if group_id == 0: return np.column_stack((np.cos(t)*r, np.sin(t)*r, (np.random.rand(n)-0.5)*0.5))
    elif group_id == 1: return np.column_stack(((np.random.rand(n)-0.5)*0.5, np.cos(t)*r, np.sin(t)*r))
    else: return np.column_stack((np.cos(t)*r, (np.random.rand(n)-0.5)*0.5, np.sin(t)*r))

def get_chaos_cloud(n):
    return (np.random.rand(n, 3) - 0.5) * 6

def render_dynamic_vortex(audio_path, output_path):
    if not os.path.exists(audio_path):
        print(f"Erro: {audio_path} não encontrado.")
        return

    bpm, rms_data, audio_dur = analyze_audio(audio_path)
    actual_dur = audio_dur
    total_frames = int(FPS * actual_dur)

    print(f"🎬 INICIANDO RENDERIZAÇÃO: DYNAMIC VORTEX ENGINE")
    print(f"Qualidade: {WIDTH_PX}x{HEIGHT_PX} @ {FPS}fps | Duração: {actual_dur:.1f}s")

    fig = plt.figure(figsize=(WIDTH_PX/DPI, HEIGHT_PX/DPI), dpi=DPI, facecolor='black')
    fig.subplots_adjust(0,0,1,1)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('black')
    ax.axis('off')
    ax.xaxis.set_pane_color((0,0,0,0)); ax.yaxis.set_pane_color((0,0,0,0)); ax.zaxis.set_pane_color((0,0,0,0))

    pos_1, pos_2, pos_3 = [get_chaos_cloud(NUM_DRONES_PER_GROUP) for _ in range(3)]

    scat_1 = ax.scatter([], [], [], c=C_RED,  s=40, edgecolors='white', lw=0.2, depthshade=True)
    scat_2 = ax.scatter([], [], [], c=C_CYAN, s=40, edgecolors='white', lw=0.2, depthshade=True)
    scat_3 = ax.scatter([], [], [], c=C_LIME, s=40, edgecolors='white', lw=0.2, depthshade=True)

    def get_stage(progress):
        # 0-30%: TORNADO
        if progress < 0.3: return [get_tornado_formation(NUM_DRONES_PER_GROUP, i) for i in range(3)], "vortex"
        # 30-50%: IMPLOSÃO (BUILD-UP)
        elif progress < 0.5: return [get_implosion_core(NUM_DRONES_PER_GROUP, i) for i in range(3)], "implode"
        # 50-80%: EXPLOSÃO (DROP)
        elif progress < 0.8: return [get_expansion_ring(NUM_DRONES_PER_GROUP, i) for i in range(3)], "explode"
        # 80-100%: TORNADO FINAL
        else: return [get_tornado_formation(NUM_DRONES_PER_GROUP, i) for i in range(3)], "vortex"

    def update(frame):
        nonlocal pos_1, pos_2, pos_3
        progress = frame / total_frames if total_frames > 0 else 0
        targets, move_type = get_stage(progress)
        intensity = rms_data[frame] if frame < len(rms_data) else 0
        
        # Física: Aceleração e Drift
        if move_type == "implode": speed, noise_amp = 0.15, 0.01
        elif move_type == "explode": speed, noise_amp = 0.22, 0.1
        else: speed, noise_amp = 0.09, 0.05

        rot_speed = frame * 0.08
        c, s = np.cos(rot_speed), np.sin(rot_speed)
        Rz = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        
        for i, (pos, targ) in enumerate(zip([pos_1, pos_2, pos_3], targets)):
            rotated_targ = np.dot(targ, Rz)
            direction = rotated_targ - pos
            if move_type == "vortex":
                direction += np.cross(pos, np.array([0,0,1])) * 0.06
            
            # Kick-Flash Physics: Empurrão extra na batida
            pos += direction * (speed + intensity * 0.15) + (np.random.rand(*pos.shape)-0.5) * noise_amp

        # Câmera de Ação Reativa
        if move_type == "implode":
            # Zoom In Progressivo
            zoom = 2.0 - (progress - 0.3) * 5.0 
            zoom = max(0.5, zoom)
            ax.set_xlim(-zoom, zoom); ax.set_ylim(-zoom, zoom); ax.set_zlim(-zoom*1.5, zoom*1.5)
            ax.view_init(elev=20, azim=frame*1.5)
        elif move_type == "explode":
            # Zoom Out Instantâneo + Shake
            zoom = 3.5 + intensity * 0.5
            ax.set_xlim(-zoom, zoom); ax.set_ylim(-zoom, zoom); ax.set_zlim(-zoom*1.5, zoom*1.5)
            ax.view_init(elev=40, azim=frame*0.5 + intensity*10)
        else:
            ax.set_xlim(-3, 3); ax.set_ylim(-3, 3); ax.set_zlim(-4, 4)
            ax.view_init(elev=15 + np.sin(frame*0.05)*10, azim=frame*1.2)

        # Atualiza Scatters
        size_dynamic = 40 * (1 + intensity * 2.0)
        alpha_dynamic = 0.7 + intensity * 0.3
        
        for i, (s, p) in enumerate(zip([scat_1, scat_2, scat_3], [pos_1, pos_2, pos_3])):
            s._offsets3d = (p[:,0], p[:,1], p[:,2])
            s.set_sizes(np.full(NUM_DRONES_PER_GROUP, size_dynamic))
            s.set_alpha(alpha_dynamic)
            
        if frame % 30 == 0:
            print(f"Frame {frame}/{total_frames} ({progress*100:.1f}%)", end='\r')
            
        return scat_1, scat_2, scat_3

    anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/FPS)
    
    # Temp file
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    print(f"Renderizando frames...")
    anim.save(temp_video, writer='ffmpeg', fps=FPS, bitrate=12000, 
              extra_args=['-vcodec', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p'])
    plt.close()

    print("Sincronia Final: O Drop visual...")
    if os.path.exists(output_path): os.remove(output_path)
    cmd = [
        "ffmpeg", "-y",
        "-i", temp_video,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "256k",
        "-shortest",
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if os.path.exists(temp_video): os.remove(temp_video)
    print(f"\n--- VORTEX CONCLUÍDO ---")
    print(f"Arquivo Master: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Arquivo MP3")
    parser.add_argument("-o", "--output", default="output_vortex.mp4", help="Arquivo de Saída")
    args = parser.parse_args()
    
    render_dynamic_vortex(args.audio, args.output)