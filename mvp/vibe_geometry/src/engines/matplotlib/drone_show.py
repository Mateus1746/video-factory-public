import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.io import wavfile
import subprocess
import os
import librosa

# --- CONFIGURAÇÕES ---
AUDIO_INPUT = "instagram_video_20251229_152102 (1).mp3"
FPS = 30 # Usando 30 para renderizar mais rápido com análise complexa
DURATION = 20  # Segundos para o vídeo renderizado
NUM_DRONES = 45
SAMPLE_RATE = 44100
VIDEO_FILE = "drone_show_temp.mp4"
FINAL_FILE = "Drone_Show_Instagram_Reactive.mp4"

import argparse
import sys

def analyze_audio(file_path):
    print(f"Analisando áudio: {file_path}...")
    y, sr = librosa.load(file_path, sr=SAMPLE_RATE)
    
    # 1. Detectar BPM
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, np.ndarray):
        tempo = tempo[0]
    print(f"BPM Detectado: {tempo:.1f}")
    
    # 2. Calcular intensidade (RMS) mapeada para os frames do vídeo
    hop_len = int(sr / FPS)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop_len)[0]
    
    # Normalizar RMS para range [0, 1]
    rms = (rms - np.min(rms)) / (np.max(rms) - np.min(rms) + 1e-6)
    
    # Duração baseada no áudio ou limite
    duration = librosa.get_duration(y=y, sr=sr)
    
    return tempo, rms, duration

def create_animation(bpm, rms_data, duration, output_path):
    print("Renderizando animação 3D Reativa...")
    fig = plt.figure(figsize=(10, 10), facecolor='black')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-180, 180)
    ax.set_ylim(-180, 180)
    ax.axis('off')
    ax.set_facecolor('black')

    # Cores Neon (Vibrant Magenta -> Electric Blue)
    cmap = plt.cm.cool
    colors = cmap(np.linspace(0, 1, NUM_DRONES))

    # Cálculo de Frequências Sincronizadas com o Beat
    beat_dur = 60.0 / bpm
    osc_freqs = []
    for i in range(NUM_DRONES):
        # Cada drone completa um ciclo em múltiplos do beat
        # Drone 0: 2 beats, Drone 1: 3 beats, etc.
        beats_per_cycle = 4 + i 
        freq = 1.0 / (beats_per_cycle * beat_dur)
        osc_freqs.append(freq)

    drones = []
    trails = []
    
    for i in range(NUM_DRONES):
        glow_pts = []
        for alpha in [0.15, 0.3, 0.7]:
            pt, = ax.plot([], [], 'o', color=colors[i], alpha=alpha)
            glow_pts.append(pt)
        drones.append(glow_pts)
        
        tr, = ax.plot([], [], color=colors[i], alpha=0.2, lw=0.8)
        trails.append(tr)

    def init():
        for i in range(NUM_DRONES):
            for pt in drones[i]: pt.set_data([], [])
            trails[i].set_data([], [])
        return [p for d in drones for p in d] + trails

    def animate(frame):
        t = frame / FPS
        # Intensidade atual do áudio
        intensity = rms_data[frame] if frame < len(rms_data) else 0
        
        for i in range(NUM_DRONES):
            freq = osc_freqs[i]
            phase = 2 * np.pi * freq * t
            
            # Movimento em 3D: Cilindro em expansão harmônica
            r_base = 0.6 + 0.6 * (i / NUM_DRONES)
            # Reatividade na amplitude: O raio expande com o grave
            r = r_base * (1 + intensity * 0.3)
            
            x_3d = r * np.cos(phase)
            y_3d = (i / NUM_DRONES - 0.5) * 2.5
            z_3d = r * np.sin(phase)
            
            x_2d, y_2d, factor = project(x_3d, y_3d, z_3d)
            
            # Update Drones
            # Blink local do drone (ponto de virada) + Global (RMS)
            blink = np.maximum(0, np.cos(phase)) ** 15
            reactive_glow = intensity * 1.5 + blink
            
            for j, pt in enumerate(drones[i]):
                base_size = [25, 12, 6][j] * (factor / 100)
                pt.set_markersize(base_size * (1 + reactive_glow * 1.5))
                pt.set_data([x_2d], [y_2d])
                pt.set_alpha(np.clip([0.1, 0.3, 0.7][j] * (1 + reactive_glow), 0, 1))
            
            # Trail
            trail_len = 15
            t_trail = np.linspace(t - 0.25, t, trail_len)
            p_trail = 2 * np.pi * freq * t_trail
            x_t = r * np.cos(p_trail)
            y_t = np.full(trail_len, y_3d)
            z_t = r * np.sin(p_trail)
            
            x_t2, y_t2, _ = project(x_t, y_t, z_t)
            trails[i].set_data(x_t2, y_t2)
            trails[i].set_alpha(np.clip(0.15 * (1 + intensity * 2), 0, 0.6))

        return [p for d in drones for p in d] + trails

    # total_frames
    total_frames = int(FPS * duration)

    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=total_frames, interval=1000/FPS, blit=True)
    
    # Temp file
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    anim.save(temp_video, writer='ffmpeg', fps=FPS, bitrate=8000)
    plt.close()
    
    return temp_video

def merge_drone(video_path, audio_path, output_path, duration):
    print("Combinando com o áudio original do Instagram...")
    if os.path.exists(output_path): os.remove(output_path)
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", str(duration), 
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if os.path.exists(video_path): os.remove(video_path)
    print(f"\n--- SUCESSO! ---")
    print(f"Vídeo final gerado: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Input Audio File")
    parser.add_argument("-o", "--output", default="output_drone_show.mp4", help="Output Video File")
    args = parser.parse_args()
    
    if not os.path.exists(args.audio):
        print(f"ERRO: Arquivo {args.audio} não encontrado.")
    else:
        bpm, rms, dur = analyze_audio(args.audio)
        temp_vid = create_animation(bpm, rms, dur, args.output)
        merge_drone(temp_vid, args.audio, args.output, dur)
