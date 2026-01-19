import subprocess
import os
import glob

def encode_video(input_dir, output_file, fps=60):
    print(f"🎬 [NEXUS] Codificando vídeo: {output_file}...")
    
    # Comando FFmpeg:
    # -y (sobrescrever)
    # -framerate (60fps)
    # -i (padrão de entrada dos frames)
    # -c:v libx264 (codec H.264)
    # -pix_fmt yuv420p (compatibilidade máxima YouTube)
    # -crf 18 (alta qualidade, visualmente lossless)
    
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", os.path.join(input_dir, "frame_%04d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        output_file
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"✅ Vídeo gerado com sucesso em: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no FFmpeg: {e.stderr.decode()}")
    except FileNotFoundError:
        print("❌ FFmpeg não encontrado. Certifique-se de que ele está instalado no sistema.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        encode_video(sys.argv[1], sys.argv[2])
