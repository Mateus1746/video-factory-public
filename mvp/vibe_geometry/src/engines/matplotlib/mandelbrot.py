import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import librosa
import os
import subprocess

# --- CONFIGURAÇÕES MASTER ---
WIDTH, HEIGHT = 720, 1280 # Resolução otimizada para fractal vertical
DPI = 100
FPS = 60 # 60fps para fluidez cinematográfica
MAX_ZOOM = 80000.0 # Mergulho profundo
CENTER_X = -0.7436438870371587
CENTER_Y =  0.1318259042053119
AUDIO_PATH = "/home/mateus/projetos/orquestrador/youtube/Harmonic Pendulum Waves/instagram_video_20251229_152102 (1).mp3"

# --- 1. ENGENHARIA DE ÁUDIO SINESTÉSICA ---
def analyze_audio_mandelbrot(file_path):
    print(f"🌀 Analisando ritmos para o mergulho: {os.path.basename(file_path)}...")
    y, sr = librosa.load(file_path, sr=22050) # Downsample para análise rápida
    rms = librosa.feature.rms(y=y)[0]
    onsets = librosa.onset.onset_strength(y=y, sr=sr)
    duration = librosa.get_duration(y=y, sr=sr)
    
    # Suavização
    rms = np.convolve(rms, np.ones(5)/5, mode='same')
    return y, sr, rms, onsets, duration

import numba
from numba import njit, prange

# --- 2. MOTOR FRACTAL OTIMIZADO (NUMBA) ---
@njit(parallel=True, fastmath=True)
def mandelbrot_numba(h, w, zoom, offset_x, offset_y, max_iter):
    x_width = 1.5 / zoom
    y_height = 1.5 * (h/w) / zoom
    
    div_time = np.zeros((h, w), dtype=np.float32)
    
    # Prange distribui o loop pelos núcleos da CPU
    for i in prange(h):
        for j in range(w):
            # Mapeamento de coordenadas
            cx = offset_x - x_width + (2.0 * x_width * j / w)
            cy = offset_y - y_height + (2.0 * y_height * i / h)
            
            # Algoritmo de Escape
            zx, zy = 0.0, 0.0
            iters = 0
            while zx*zx + zy*zy <= 4.0 and iters < max_iter:
                # Z = Z^2 + C
                xtemp = zx*zx - zy*zy + cx
                zy = 2.0 * zx * zy + cy
                zx = xtemp
                iters += 1
            
            # Suavização simples (opcional, aqui usamos o iter clássico para o cycle)
            div_time[i, j] = iters
            
    return div_time

import argparse
import sys

def render_mandelbrot_dive(audio_path, output_path):
    if not os.path.exists(audio_path):
        print(f"Erro: {audio_path} não encontrado.")
        return

    y_audio, sr_audio, rms, onsets, duration = analyze_audio_mandelbrot(audio_path)
    audio_time = np.linspace(0, duration, len(rms))
    
    print(f"🌀 INICIANDO INFINITE ZOOM ({duration:.1f}s | 60fps)...")
    
    fig = plt.figure(figsize=(WIDTH/DPI, HEIGHT/DPI), dpi=DPI)
    fig.subplots_adjust(0,0,1,1)
    ax = fig.add_subplot(111)
    ax.axis('off')
    
    # Colormap Psicodélico
    cmap = plt.cm.magma # Magma/Inferno/Twilight_shifted
    
    im = ax.imshow(np.zeros((HEIGHT, WIDTH)), cmap=cmap, origin='lower', interpolation='bilinear')

    # Estado de cor persistente
    color_offset = 0.0

    def update(frame):
        nonlocal color_offset
        t = frame / (FPS * duration)
        if t > 1.0: t = 1.0
        
        # 1. Sync Áudio
        vol = np.interp(frame/FPS, audio_time, rms) * 10
        beat = np.interp(frame/FPS, audio_time, onsets)
        
        # 2. Zoom Exponencial
        # Usamos t**1.5 para uma aceleração mais drástica no final
        current_zoom = 1.0 + (MAX_ZOOM - 1.0) * (t**1.8)
        
        # 3. Nível de Detalhe (Iterations)
        # Sobe com o zoom e pulsa com beats
        base_iter = int(60 + 200 * t)
        spike_iter = int(beat * 15)
        current_iter = min(base_iter + spike_iter, 512)
        
        # 4. Render Fractal
        data = mandelbrot_numba(HEIGHT, WIDTH, current_zoom, CENTER_X, CENTER_Y, current_iter)
        
        # 5. Fluxo de Cor (Cycle)
        # Velocidade do fluxo baseada no volume
        color_offset += 1.5 + vol * 5.0
        data_cyclic = (data * 5 + color_offset) % 256
        
        im.set_data(data_cyclic)
        
        if frame % (FPS*5) == 0:
            print(f"Mergulho: {int(t*100)}% | Zoom: {int(current_zoom)}x | Iter: {current_iter}")
            
        return [im]

    total_frames = int(FPS * duration)
    print(f"🎬 Orquestrando {total_frames} frames de matemática infinita...")
    anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/FPS)
    
    # Temp file
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    
    anim.save(temp_video, writer='ffmpeg', fps=FPS, bitrate=15000,
              extra_args=['-vcodec', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p'])
    plt.close()

    print("Sincronia Final: Fundindo Geometria Fractal e Áudio...")
    if os.path.exists(output_path): os.remove(output_path)
    cmd = [
        "ffmpeg", "-y", "-i", temp_video, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if os.path.exists(temp_video): os.remove(temp_video)
    
    print(f"\n--- ZOOM CONCLUÍDO ---")
    print(f"Vídeo Master Final: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Input Audio File")
    parser.add_argument("-o", "--output", default="output_mandelbrot.mp4", help="Output Video File")
    args = parser.parse_args()
    
    render_mandelbrot_dive(args.audio, args.output)
