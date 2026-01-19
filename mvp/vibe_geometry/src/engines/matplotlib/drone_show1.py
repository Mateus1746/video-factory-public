import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.io import wavfile
import subprocess
import os

# --- CONFIGURAÇÕES ---
FPS = 60
DURATION = 15  # Segundos para um loop perfeito
NUM_DRONES = 40
SAMPLE_RATE = 44100
VIDEO_FILE = "drone_show_temp.mp4"
AUDIO_FILE = "drone_show.wav"
FINAL_FILE = "Drone_Show_Harmonic_3D.mp4"

import argparse
import sys
import librosa # Add librosa for analysis since this script was generative

# --- HARDWARE & CONFIG ---
FPS = 60
NUM_DRONES = 40

# --- PROJEÇÃO 3D ---
def project(x, y, z):
    # Câmera simples (Perspectiva)
    fov = 400
    viewer_distance = 4
    factor = fov / (viewer_distance + z)
    x_2d = x * factor
    y_2d = y * factor
    return x_2d, y_2d, factor 

# --- ANIMAÇÃO ---
def create_animation(audio_path, output_path):
    print(f"Analisando {audio_path}...")
    y, sr = librosa.load(audio_path, sr=44100)
    duration = librosa.get_duration(y=y, sr=sr)
    
    # RMS para reatividade
    hop_len = int(sr / FPS)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop_len)[0]
    rms = (rms - np.min(rms)) / (np.max(rms) - np.min(rms) + 1e-6)

    print("Renderizando animação 3D...")
    fig = plt.figure(figsize=(10, 10), facecolor='black')
    ax = fig.add_axes([0, 0, 1, 1], projection=None)
    ax.set_xlim(-150, 150)
    ax.set_ylim(-150, 150)
    ax.axis('off')
    ax.set_facecolor('black')

    # Cores Neon (Cyan -> Violet)
    cmap = plt.cm.cool
    colors = cmap(np.linspace(0, 1, NUM_DRONES))

    drones = []
    trails = []
    
    for i in range(NUM_DRONES):
        # Brilho (Glow): Varias camadas de pontos com alpha diferente
        glow_pts = []
        for alpha in [0.2, 0.4, 0.8]:
            pt, = ax.plot([], [], 'o', color=colors[i], alpha=alpha, markersize=10 / alpha**0.5)
            glow_pts.append(pt)
        drones.append(glow_pts)
        
        tr, = ax.plot([], [], color=colors[i], alpha=0.3, lw=1)
        trails.append(tr)

    # Frequências visuais de rotação
    F_START = 1.0 / 15 * 10 
    F_END = 1.0 / 15 * 20   
    FREQS = np.linspace(F_START, F_END, NUM_DRONES)

    def init():
        for i in range(NUM_DRONES):
            for pt in drones[i]: pt.set_data([], [])
            trails[i].set_data([], [])
        return [p for d in drones for p in d] + trails

    def animate(frame):
        t = frame / FPS
        intensity = rms[frame] if frame < len(rms) else 0
        
        for i in range(NUM_DRONES):
            freq = FREQS[i]
            phase = 2 * np.pi * freq * t
            
            # Movimento em 3D: Círculo rotativo com variação harmônica
            r = 0.5 + 0.5 * (i / NUM_DRONES)
            # Expand radius on loud parts
            r = r * (1 + intensity * 0.2)
            
            x_3d = r * np.cos(phase)
            y_3d = (i / NUM_DRONES - 0.5) * 2
            z_3d = r * np.sin(phase)
            
            x_2d, y_2d, factor = project(x_3d, y_3d, z_3d)
            
            # Update Drones (Glow)
            blink = np.maximum(0, np.cos(phase)) ** 20 
            glow = blink + intensity
            
            for j, pt in enumerate(drones[i]):
                # Tamanho baseado no blink + perspectiva
                base_size = [20, 10, 5][j] * (factor / 100)
                pt.set_markersize(base_size * (1 + glow * 2))
                pt.set_data([x_2d], [y_2d])
                alpha_val = [0.1, 0.3, 0.8][j] * (1 + glow)
                pt.set_alpha(np.clip(alpha_val, 0, 1))
            
            # Trail (Rastro no tempo)
            trail_len = 20
            t_trail = np.linspace(t - 0.3, t, trail_len)
            p_trail = 2 * np.pi * freq * t_trail
            x_t = r * np.cos(p_trail)
            y_t = np.full(trail_len, y_3d)
            z_t = r * np.sin(p_trail)
            
            x_t2, y_t2, f_t = project(x_t, y_t, z_t)
            trails[i].set_data(x_t2, y_t2)
            trails[i].set_alpha(np.clip(0.2 * (factor / 100), 0, 1))

        return [p for d in drones for p in d] + trails

    total_frames = int(FPS * duration)
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=total_frames, interval=1000/FPS, blit=True)
    
    # Temp file
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    anim.save(temp_video, writer='ffmpeg', fps=FPS, bitrate=8000)
    plt.close()
    
    print("Combinando Áudio e Vídeo final...")
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
    print(f"\n--- SUCESSO! ---")
    print(f"Vídeo gerado: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Input Audio File")
    parser.add_argument("-o", "--output", default="output_drone_show1.mp4", help="Output Video File")
    args = parser.parse_args()
    
    if not os.path.exists(args.audio):
        print(f"Erro: {args.audio} não encontrado.")
    else:
        create_animation(args.audio, args.output)
