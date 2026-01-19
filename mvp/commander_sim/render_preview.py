import subprocess
import os
import sys

def render_preview(map_name=None):
    if not map_name:
        print("❌ Erro: Especifique o nome do mapa (pasta em ./frames/).")
        print("Exemplo: python3 render_preview.py duel")
        return

    frames_path = os.path.join("frames", map_name)
    if not os.path.exists(frames_path):
        print(f"❌ Erro: Pasta '{frames_path}' não encontrada.")
        return

    output_video = f"preview_{map_name}.mp4"
    print(f"🎬 Gerando PREVIEW para {map_name} (480p 30fps)...")
    
    if os.path.exists(output_video):
        os.remove(output_video)

    # FFmpeg command
    cmd = [
        "ffmpeg", "-y",
        "-framerate", "60",
        "-i", f"{frames_path}/frame_%05d.png",
        "-vf", "scale=480:-2",
        "-r", "30",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_video
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Preview gerado com sucesso: {output_video}")
    except Exception as e:
        print(f"❌ Erro ao gerar vídeo: {e}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    render_preview(target)
