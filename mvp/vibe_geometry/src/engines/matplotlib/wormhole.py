import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import LineCollection
import librosa
import os
import subprocess

# --- CONFIGURAÇÕES MASTER ---
WIDTH, HEIGHT = 1080, 1920
DPI = 100
FPS = 60
MAX_LINES = 15 # Máximo de linhas simultâneas para não poluir
AUDIO_PATH = "/home/mateus/projetos/orquestrador/youtube/Harmonic Pendulum Waves/instagram_video_20251229_152102 (1).mp3"

# --- 1. ENGENHARIA DE ÁUDIO MULTIBANDA ---
def analyze_audio_multiband(file_path):
    print(f"🌀 Extraindo DNA sonoro: {os.path.basename(file_path)}...")
    y, sr = librosa.load(file_path, sr=44100)
    
    # Onsets para "Nascimento" de linhas
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, backtrack=True)
    onset_times = librosa.frames_to_time(onsets, sr=sr)
    
    # 4 Bandas de frequência: Sub/Bass, Low-Mid, Mid, High
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
    
    bands_limits = [0, 200, 800, 3000, 16000]
    band_energies = []
    for i in range(len(bands_limits)-1):
        mask = (freqs >= bands_limits[i]) & (freqs < bands_limits[i+1])
        energy = np.mean(S[mask, :], axis=0)
        # Normalização logarítmica
        energy = librosa.amplitude_to_db(energy, ref=np.max)
        energy = np.clip((energy + 80) / 80, 0, 1.0)
        # Suavização
        energy = np.convolve(energy, np.ones(5)/5, mode='same')
        band_energies.append(energy)
        
    duration = librosa.get_duration(y=y, sr=sr)
    return band_energies, onset_times, duration

# --- 2. CLASSE DE LINHA WHIRLPOOL ---
class WhirlpoolLine:
    def __init__(self, start_time, band_idx, color):
        self.start_time = start_time
        self.band_idx = band_idx
        self.color = color
        self.points = 500 
        self.angle_offset = np.random.rand() * 2 * np.pi
        self.rot_speed = (0.5 + np.random.rand() * 1.5) * (1 if np.random.rand() > 0.5 else -1)
        self.target_pos = np.array([0.0, 0.0])
        
        # Destino Aleatório para o efeito de Sução (Macarrão)
        side_x = 2.2 * (1 if np.random.rand() > 0.5 else -1)
        side_y = (np.random.rand() - 0.5) * 4.0
        self.suction_target = np.array([side_x, side_y])
        
        # Ponto de controle para a curva de saída (Bezier)
        self.ctrl_p = np.array([np.random.uniform(-1.2, 1.2), np.random.uniform(-1.2, 1.2)])
        
        self.is_dead = False

    def get_path(self, t, intensity, is_outro, outro_progress):
        dt = t - self.start_time
        if dt < 0: return None
        
        # 1. Crescimento e Geometria da Espiral
        growth = min(1.0, dt / 5.0)
        num_turns = 12 * np.pi * growth
        # Criamos o "caminho" total da espiral
        thetas = np.linspace(0, num_turns, self.points)
        time_rot = t * self.rot_speed + self.angle_offset
        
        # Raio base
        radius_scale = growth * (0.8 + intensity * 0.4)
        r = (thetas / (12 * np.pi)) * radius_scale
        
        # Posições da Espiral
        x_spiral = self.target_pos[0] + r * np.cos(thetas + time_rot)
        y_spiral = self.target_pos[1] + r * np.sin(thetas + time_rot)
        spiral_path = np.column_stack([x_spiral, y_spiral])

        if not is_outro:
            return spiral_path
        
        # 2. Lógica de SAÍDA: Macarrão Sugado por um Ponto Fixo
        # Ponto de conexão (a ponta da espiral no momento do início do outro)
        # Para um efeito mais fluido, usamos a ponta atual da espiral
        p_start = spiral_path[-1] # A ponta externa da espiral
        p_mid = self.ctrl_p
        p_end = self.suction_target
        
        # Criar a Curva de Conector até o buraquinho (Bezier)
        # Usamos t_c para desenrolar o macarrão ao longo dela
        steps = 200
        tc = np.linspace(0, 1, steps)
        x_conn = (1-tc)**2 * p_start[0] + 2*(1-tc)*tc * p_mid[0] + tc**2 * p_end[0]
        y_conn = (1-tc)**2 * p_start[1] + 2*(1-tc)*tc * p_mid[1] + tc**2 * p_end[1]
        connector_path = np.column_stack([x_conn, y_conn])
        
        # Caminho Total = Espiral + Conector
        full_path = np.vstack([spiral_path, connector_path])
        
        # No outro_progress (0 a 1), a linha "slicka" pelo caminho até o ponto final
        # start_idx caminha do início ao fim do caminho total
        total_len = len(full_path)
        start_idx = int(outro_progress * total_len)
        
        # A linha vai encolhendo conforme é sugada
        # Mantemos uma janela que se move e diminui
        visible_path = full_path[start_idx:]
        
        if len(visible_path) < 2:
            self.is_dead = True
            return None
            
        return visible_path

import argparse
import sys

def render_aesthetic_whirlpool(audio_path, output_path):
    if not os.path.exists(audio_path):
        print(f"Erro: {audio_path} não encontrado")
        return

    band_energies, onset_times, duration = analyze_audio_multiband(audio_path)
    time_axis = np.linspace(0, duration, band_energies[0].shape[0])
    
    print(f"🌀 RENDERIZANDO WHIRLPOOL AESTHETIC...")
    
    fig, ax = plt.subplots(figsize=(WIDTH/DPI, HEIGHT/DPI), dpi=DPI, facecolor='black')
    ax.set_facecolor('black')
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-2.6, 2.6)
    ax.axis('off')
    plt.subplots_adjust(0,0,1,1)

    # Cores Neon
    NEON_PALETTE = ['#FF00FF', '#00FFFF', '#00FF00', '#FFFF00', '#FF3131']
    
    active_lines = []
    
    # Criar coleções (uma para cada cor para efeito de glow)
    # Vamos usar LineCollections individuais para flexibilidade
    line_objects = []
    for _ in range(MAX_LINES):
        lc = LineCollection([], linewidths=2, alpha=0, zorder=5)
        # Glow layer
        lc_glow = LineCollection([], linewidths=6, alpha=0, zorder=4)
        ax.add_collection(lc)
        ax.add_collection(lc_glow)
        line_objects.append((lc, lc_glow))

    total_frames = int(FPS * duration)
    
    # Controle de Onsets Processados
    next_onset_idx = 0

    def update(frame):
        nonlocal next_onset_idx, active_lines
        t = frame / FPS
        is_outro = t > (duration * 0.9)
        outro_progress = (t - duration * 0.9) / (duration * 0.1) if is_outro else 0
        
        # 1. Spawn novas linhas no toque
        while next_onset_idx < len(onset_times) and onset_times[next_onset_idx] <= t:
            if len(active_lines) < MAX_LINES:
                b_idx = np.random.randint(0, 4)
                color = NEON_PALETTE[np.random.randint(0, len(NEON_PALETTE))]
                active_lines.append(WhirlpoolLine(t, b_idx, color))
            next_onset_idx += 1
        
        # 2. Atualizar Geometria e Estilo
        artists = []
        for i, (lc_core, lc_glow) in enumerate(line_objects):
            if i < len(active_lines):
                line = active_lines[i]
                # Energia da banda atual
                energy = np.interp(t, time_axis, band_energies[line.band_idx])
                
                path = line.get_path(t, energy, is_outro, outro_progress)
                
                if path is not None:
                    lc_core.set_segments([path])
                    lc_glow.set_segments([path])
                    
                    # Brilho reativo (Alpha e Width)
                    alpha = 0.4 + energy * 0.6
                    width = 2.0 + energy * 4.0
                    
                    lc_core.set_alpha(alpha)
                    lc_core.set_color(line.color)
                    lc_core.set_linewidths([width])
                    
                    lc_glow.set_alpha(alpha * 0.3)
                    lc_glow.set_color(line.color)
                    lc_glow.set_linewidths([width * 3])
                else:
                    lc_core.set_alpha(0)
                    lc_glow.set_alpha(0)
            else:
                lc_core.set_alpha(0)
                lc_glow.set_alpha(0)
            
            artists.extend([lc_core, lc_glow])
            
        # Remover linhas mortas
        active_lines = [l for l in active_lines if not l.is_dead]
        
        if frame % (FPS * 5) == 0:
            print(f"Aesthetic Whirlpool: {int(frame/total_frames*100)}% | Active Lines: {len(active_lines)}")

        return artists

    print(f"🎬 Orquestrando {total_frames} frames de pura sinestesia...")
    anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/FPS, blit=True)
    
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    anim.save(temp_video, writer='ffmpeg', fps=FPS, bitrate=6000, 
              extra_args=['-vcodec', 'libx264', '-preset', 'medium', '-crf', '22', '-pix_fmt', 'yuv420p'])
    plt.close()

    if os.path.exists(output_path): os.remove(output_path)
    
    print("Sincronia Final: Fundindo Redemoinho e Áudio...")
    cmd = [
        "ffmpeg", "-y", "-i", temp_video, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if os.path.exists(temp_video): os.remove(temp_video)
    
    print(f"\n--- WHIRLPOOL CONCLUÍDO ---")
    print(f"Vídeo Master Final: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Input Audio File")
    parser.add_argument("-o", "--output", default="output_wormhole.mp4", help="Output Video File")
    args = parser.parse_args()
    
    render_aesthetic_whirlpool(args.audio, args.output)
