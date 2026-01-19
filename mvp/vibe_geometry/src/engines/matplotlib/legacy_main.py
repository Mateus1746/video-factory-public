import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.io import wavfile
import subprocess
import os
import librosa

# --- CONFIGURAÇÕES ---
AUDIO_FILE = "music.wav" # O arquivo de música base
FPS = 30
DURATION = 20
NUM_DOTS = 14
SAMPLE_RATE = 44100

def analyze_audio(file_path):
    print(f"Analisando áudio: {file_path}...")
    y, sr = librosa.load(file_path, sr=SAMPLE_RATE)
    
    # 1. Detectar BPM e Beats
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    # Se tempo for um array (versão nova), pegar o primeiro valor
    if isinstance(tempo, np.ndarray):
        tempo = tempo[0]
        
    print(f"BPM Detectado: {tempo:.1f}")
    
    # 2. Calcular intensidade (RMS) por frame do vídeo
    # Queremos o RMS mapeado para os frames do vídeo (FPS)
    hop_len = int(sr / FPS)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop_len)[0]
    
    # Normalizar RMS para range [0, 1] para facilitar uso visual
    rms = (rms - np.min(rms)) / (np.max(rms) - np.min(rms) + 1e-6)
    
    return tempo, rms, y

def create_video_reactive(num_dots, duration, bpm, rms_data):
    fig = plt.figure(figsize=(10, 10), dpi=100, facecolor='#000000')
    ax = plt.axes(xlim=(-1.2, 1.2), ylim=(-0.1, 1.1))
    ax.set_facecolor('#000000')
    ax.axis('off')

    # Palette: Neon Magenta -> Cyan
    cmap = plt.cm.magma
    colors = cmap(np.linspace(0.3, 0.9, num_dots))
    
    # Cálculo da Física Sincronizada com o Beats
    # Duração de um beat em segundos
    beat_dur = 60.0 / bpm
    
    # Cada pêndulo deve atingir a borda em um múltiplo do beat.
    # Se ele bater na borda a cada N beats, a frequência é 1 / (2 * N * beat_dur)
    # Vamos fazer o mais rápido bater a cada beat (1/2 ciclo por beat)
    # E o mais lento a cada k beats.
    osc_freqs = []
    for i in range(num_dots):
        beats_per_half_cycle = 2 + i # Pêndulo mais alto bate a cada (2+N) beats
        freq = 1.0 / (2 * beats_per_half_cycle * beat_dur)
        osc_freqs.append(freq)

    dots = []
    lines = []
    
    for i in range(num_dots):
        ln, = ax.plot([], [], color=colors[i], lw=2, alpha=0.4)
        pt, = ax.plot([], [], 'o', color='white', markersize=8,
                     markeredgecolor=colors[i], markeredgewidth=2)
        lines.append(ln)
        dots.append(pt)

    def init():
        for pt in dots: pt.set_data([], [])
        for ln in lines: ln.set_data([], [])
        return dots + lines

    def animate(frame):
        t = frame / FPS
        # Intensidade atual do áudio
        intensity = rms_data[frame] if frame < len(rms_data) else 0
        
        for i, (pt, ln) in enumerate(zip(dots, lines)):
            freq = osc_freqs[i]
            phase = 2 * np.pi * freq * t
            
            x = np.cos(phase) * 0.95
            y = 1.0 - (i / num_dots) * 0.9 - 0.05
            
            # Reatividade Visual:
            # Tamanho da bola e largura do rastro aumentam com o grave/volume
            size = 8 + intensity * 15 # Aumenta significativamente no beat
            pt.set_markersize(size)
            pt.set_data([x], [y])
            
            # Trail reativo
            trail_len = 10
            trail_t = np.linspace(t - 0.2, t, trail_len)
            trail_x = np.cos(2 * np.pi * freq * trail_t) * 0.95
            trail_y = np.full_like(trail_x, y)
            ln.set_data(trail_x, trail_y)
            ln.set_alpha(0.2 + intensity * 0.8)
            ln.set_linewidth(1 + intensity * 5)
            
        return dots + lines

    print(f"Renderizando {FPS*DURATION} frames reativos...")
    anim = animation.FuncAnimation(fig, animate, init_func=init, 
                                   frames=FPS*DURATION, interval=1000/FPS, blit=True)
    anim.save('reactive_video.mp4', writer='ffmpeg', fps=FPS, bitrate=5000)

if __name__ == "__main__":
    if not os.path.exists(AUDIO_FILE):
        print(f"ERRO: Arquivo {AUDIO_FILE} não encontrado. Gere ele primeiro ou forneça um.")
    else:
        # 1. Analisar áudio
        bpm, rms, audio_y = analyze_audio(AUDIO_FILE)
        
        # 2. Gerar Vídeo Reativo
        create_video_reactive(NUM_DOTS, DURATION, bpm, rms)
        
        # 3. Merge Automático
        print("Combinando com a trilha sonora...")
        output_filename = "Beat_Reactive_Pendulum.mp4"
        if os.path.exists(output_filename): os.remove(output_filename)
        
        cmd = [
            "ffmpeg", "-y",
            "-i", "reactive_video.mp4",
            "-i", AUDIO_FILE,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_filename
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        print(f"\n--- SUCESSO! ---")
        print(f"Arquivo final: {output_filename}")