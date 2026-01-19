import os
import subprocess
import shutil
import datetime
from utils.video_encoder import encode_video

def main():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    video_filename = f"fortress_merge_{timestamp}.mp4"
    
    batch_dir = os.path.join(os.getcwd(), "batch_output")
    tmp_dir = os.path.join(os.getcwd(), "tmp_frames")
    
    if not os.path.exists(batch_dir): os.makedirs(batch_dir)
    if os.path.exists(tmp_dir): shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)
    
    print(f"🎥 [NEXUS] Iniciando Renderização Final (1080p @ 60fps)...")
    
    env = os.environ.copy()
    env["WIDTH"] = "1080"
    env["HEIGHT"] = "1920"
    env["FPS"] = "60"
    env["HEADLESS"] = "true"
    env["OUTPUT_DIR"] = tmp_dir
    env["DURATION"] = "60"
    
    # 1. Gerar Frames
    subprocess.run(["uv", "run", "main.py"], env=env)
    
    # 2. Codificar Vídeo
    output_path = os.path.join(batch_dir, video_filename)
    encode_video(tmp_dir, output_path, fps=60)
    
    # 3. Limpeza
    print(f"🧹 [NEXUS] Limpando frames temporários...")
    shutil.rmtree(tmp_dir)
    print(f"✨ Concluído! O vídeo final está em: {output_path}")

if __name__ == "__main__":
    main()