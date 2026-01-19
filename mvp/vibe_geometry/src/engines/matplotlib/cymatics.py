import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import librosa
import os
import subprocess

# --- CONFIGURAÇÕES MASTER ---
WIDTH, HEIGHT = 1080, 1920
DPI = 100
FPS = 60 
NUM_SAND = 8000 # Dobro de densidade para mandalas nítidas
AUDIO_PATH = "/home/mateus/projetos/orquestrador/youtube/Harmonic Pendulum Waves/instagram_video_20251229_152102 (1).mp3"

# --- 1. ENGENHARIA DE ÁUDIO REATIVA ---
def analyze_audio_cymatics_v2(file_path):
    print(f"📊 Extraindo batidas e ressonância: {os.path.basename(file_path)}...")
    y, sr = librosa.load(file_path, sr=44100)
    rms = librosa.feature.rms(y=y)[0]
    
    # Detecção de batidas reais (Onsets)
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, wait=1, pre_avg=1, post_avg=1, pre_max=1, post_max=1)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    
    duration = librosa.get_duration(y=y, sr=sr)
    return y, sr, rms, onset_times, duration

# --- 2. FÍSICA DE CHLADNI PURA ---
def chladni_equation(x, y, m, n):
    return np.cos(n * np.pi * x) * np.cos(m * np.pi * y) - \
           np.cos(m * np.pi * x) * np.cos(n * np.pi * y)

# Lista expandida de modos geométricos
MODES = [
    (3, 2), (3, 3), (4, 3), (2, 5), (5, 4), (6, 5), (4, 7), (8, 7), (10, 8), (12, 11), (15, 14)
]

import argparse
import sys

def render_cymatics_v2(audio_path, output_path):
    if not os.path.exists(audio_path):
        print(f"Erro: {audio_path} não encontrado.")
        return

    y_audio, sr_audio, rms, onset_times, duration = analyze_audio_cymatics_v2(audio_path)
    audio_time_axis = np.linspace(0, duration, len(rms))
    
    print(f"🐚 GERANDO CYMATICS 2.0 ({duration:.1f}s | Real Physics)...")
    
    fig = plt.figure(figsize=(WIDTH/DPI, HEIGHT/DPI), dpi=DPI, facecolor='black')
    ax = fig.add_axes([0, 0, 1, 1], xlim=(-1.05, 1.05), ylim=(-1.05 * 1.77, 1.05 * 1.77))
    ax.set_facecolor('black')
    ax.axis('off')

    # Areia espalhada uniformemente
    pos = (np.random.rand(NUM_SAND, 2) - 0.5) * 2.0
    pos[:, 1] *= 1.77 
    
    scat = ax.scatter(pos[:,0], pos[:,1], s=2.5, c='white', alpha=0.8, edgecolors='none')

    # Estado de controle
    current_mode_idx = 0

    def update(frame):
        nonlocal pos, current_mode_idx
        t = frame / FPS
        if t > duration: t = duration
        
        # 1. Sync Áudio
        vol = np.interp(t, audio_time_axis, rms) * 10.0
        
        # 2. Troca de Modo no Onset (Batida)
        # Se o tempo 't' passou por um onset recente, trocamos o desenho
        # Simplificação: contamos quantos onsets passamos
        onsets_past = np.sum(onset_times < t)
        current_mode_idx = onsets_past % len(MODES)
        m, n = MODES[current_mode_idx]
        
        # 3. Física Estocástica (Sem Gravidade Central)
        x = pos[:, 0]
        y = pos[:, 1] / 1.77
        
        vibration = chladni_equation(x, y, m, n)
        
        # Deslocamento: violentamente alto onde vibra, quase zero nos nodos
        # vibration**2 garante que a direção não importa, apenas a amplitude
        move_intensity = 0.04 * (vibration**2 + 0.05) * (0.3 + vol)
        move_intensity = move_intensity.reshape(-1, 1)
        
        # Movimento aleatório puro (Areia pulando na placa)
        jitter = (np.random.rand(NUM_SAND, 2) - 0.5) * move_intensity
        pos += jitter
        
        # 4. Tratamento de Bordas (Bounce sutil para não sumirem)
        mask_x = np.abs(pos[:, 0]) > 1.0
        pos[mask_x, 0] *= -0.95
        mask_y = np.abs(pos[:, 1]) > 1.77
        pos[mask_y, 1] *= -0.95
        
        # 5. Visual: Brilho Nodal
        # Partículas paradas brilham. Partículas em movimento ficam com rastro (alpha baixo)
        colors = np.ones((NUM_SAND, 4))
        # Nodos (vibration=0) brilham em 1.0. Antinodos ficam transparentes.
        alpha = np.clip(1.0 - np.abs(vibration) * 3.0, 0.15, 1.0)
        colors[:, 3] = alpha
        
        # Flashes brancos puros nas batidas (vol alto)
        flash = np.clip(vol * 0.1, 0, 0.3)
        colors[:, 0:3] += flash

        scat.set_offsets(pos)
        scat.set_color(np.clip(colors, 0, 1))
        
        # Zoom Pulsante
        zoom_pulse = 1.05 + np.sin(t * 0.8) * 0.02 + (vol * 0.005)
        ax.set_xlim(-zoom_pulse, zoom_pulse)
        ax.set_ylim(-zoom_pulse * 1.77, zoom_pulse * 1.77)
        
        return scat,

    total_frames = int(FPS * duration)
    print(f"🎬 Orquestrando {total_frames} frames de Geometria Rítmica...")
    anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/FPS)
    
    # Temp file
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    
    anim.save(temp_video, writer='ffmpeg', fps=FPS, bitrate=12000,
              extra_args=['-vcodec', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p'])
    plt.close()

    final_output = output_path
    print("Sincronia Final: Fundindo Geometria Corrigida e Áudio...")
    if os.path.exists(final_output): os.remove(final_output)
    cmd = [
        "ffmpeg", "-y", "-i", temp_video, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", final_output
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if os.path.exists(temp_video): os.remove(temp_video)
    
    print(f"\n--- RESONANCE V2 CONCLUÍDO ---")
    print(f"Vídeo Master Final: {final_output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Input Audio File")
    parser.add_argument("-o", "--output", default="output_cymatics.mp4", help="Output Video File")
    args = parser.parse_args()
    
    render_cymatics_v2(args.audio, args.output)
