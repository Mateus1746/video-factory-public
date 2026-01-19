import librosa
import numpy as np
import os
import sys

def find_best_segment(file_path, duration=30, sr=22050):
    """
    Analisa o áudio para encontrar o segmento de 'duration' segundos
    com a maior densidade de energia e batidas (o 'Drop' ou Refrão).
    """
    print(f"🧠 Smart Cutter: Analisando topografia de áudio para {os.path.basename(file_path)}...")
    
    try:
        # Carrega em mono e SR menor para velocidade (precisão de corte não exige Hi-Fi)
        y, sr = librosa.load(file_path, sr=sr, mono=True)
    except Exception as e:
        print(f"❌ Erro ao carregar áudio: {e}")
        return None

    file_duration = librosa.get_duration(y=y, sr=sr)
    if file_duration <= duration:
        print("⚠️ Áudio menor que a duração alvo. Retornando clipe inteiro.")
        return (0, file_duration)

    # 1. Energia RMS (Volume Percebido)
    hop_length = 512
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    
    # 2. Força de Onset (Densidade de Batidas/Transientes)
    # Isso ajuda a diferenciar um vocal alto e sustentado de um drop rítmico
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    
    # Normalização (0 a 1) para combinar os sinais de forma justa
    def normalize(x):
        return (x - np.min(x)) / (np.max(x) - np.min(x) + 1e-6)

    # Combinamos: 60% Energia + 40% Ritmo (ajustável)
    # O foco é "Vibe", então ritmo importa muito.
    combined_score = 0.6 * normalize(rms) + 0.4 * normalize(onset_env[:len(rms)])

    # 3. Janela Deslizante (Convolution)
    # Criamos uma janela do tamanho exato em frames
    frames_per_sec = sr / hop_length
    window_size_frames = int(duration * frames_per_sec)
    
    # Kernel retangular para somar o score dentro da janela
    window_kernel = np.ones(window_size_frames)
    
    # 'same' mantém o tamanho, mas precisamos ajustar o deslocamento de fase depois
    score_trend = np.convolve(combined_score, window_kernel, mode='valid')
    
    # Encontrar o índice do pico máximo
    peak_frame_index = np.argmax(score_trend)
    
    # Converter volta para tempo
    # O convolve 'valid' remove as bordas, então o índice 0 corresponde ao início do arquivo
    start_time = peak_frame_index / frames_per_sec
    end_time = start_time + duration
    
    # Ajuste fino: Alinhar com a batida mais próxima (Downbeat) seria ideal, 
    # mas por enquanto, vamos garantir margens seguras.
    
    print(f"🎯 Alvo Localizado: {start_time:.2f}s - {end_time:.2f}s (Score Máx: {score_trend[peak_frame_index]:.2f})")
    
    return start_time, end_time

if __name__ == "__main__":
    # Teste rápido via CLI
    if len(sys.argv) < 2:
        print("Uso: python smart_cutter.py <arquivo_audio> [duracao]")
        sys.exit(1)
    
    f_path = sys.argv[1]
    dur = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    s, e = find_best_segment(f_path, duration=dur)
    print(f"Start: {s}")
    print(f"End: {e}")
