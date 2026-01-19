import os
import sys
import argparse
from datetime import datetime

# Import modules
# We need to add src to path to import local modules easily if running from root
sys.path.append(os.path.join(os.path.dirname(__file__)))

import content_hunter
import smart_cutter
import analyzer
import render_video_v2
from style_manager import StyleManager
# Use subprocess for the trimmer script to avoid path issues or import if easy
# scripts/trim_audio.py is outside src, let's import it via path hack or just use subprocess
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
try:
    import trim_audio
except ImportError:
    # Fallback if scripts not in path
    print("Warning: Direct import of trim_audio failed. Using subprocess.")
    trim_audio = None


    import re

def sanitize_filename(name):
    """Converts a string to a safe, SEO-friendly filename."""
    # Remove extension if present (though we usually handle base_name)
    name = os.path.splitext(name)[0]
    
    # Lowercase
    name = name.lower()
    
    # Replace spaces and common separators with hyphens
    name = re.sub(r'[_\s]+', '-', name)
    
    # Remove non-alphanumeric characters (except hyphens)
    name = re.sub(r'[^a-z0-9-]', '', name)
    
    # Remove multiple hyphens
    name = re.sub(r'-+', '-', name)
    
    # Strip leading/trailing hyphens
    name = name.strip('-')
    
    return name

def run_pipeline(query, duration=30, dry_run=False):
    print("\n" + "="*50)
    print(f"🚀 INICIANDO CICLO AUTÔNOMO: {query}")
    print("="*50 + "\n")

    video_dir = "batch_output"
    data_dir = "processing_data"

    if dry_run:
        print("🚧 MODO DRY-RUN: Simulação de roteamento. Nenhuma renderização real.")
        final_audio_path = os.path.join(data_dir, "mock_audio.mp3")
        json_path = os.path.join(data_dir, "mock_data.json")
        base_name = "mock-video-seo-optimized"
    else:
        # Create directories
        for d in [video_dir, data_dir]:
            if not os.path.exists(d):
                os.makedirs(d)

        # 1. HUNTER
        print(">>> FASE 1: AQUISIÇÃO (Hunter)")
        raw_audio = content_hunter.search_and_download(query)
        
        if not raw_audio:
            print("🛑 Pipeline abortado: Nenhum áudio novo encontrado.")
            return

        # 2. SURGEON (Smart Cut)
        print("\n>>> FASE 2: CIRURGIA (Smart Cutter)")
        timestamps = smart_cutter.find_best_segment(raw_audio, duration=duration)
        
        if not timestamps:
            print("🛑 Erro ao determinar corte.")
            return
            
        start_t, end_t = timestamps
        
        # Prepare output paths
        raw_base = os.path.basename(raw_audio)
        base_name = sanitize_filename(raw_base)
        print(f"✨ SEO Filename: '{raw_base}' -> '{base_name}'")
        
        final_audio_path = os.path.join(data_dir, f"{base_name}_cut.mp3")
        
        # 3. TRIMMER
        print(f"\n>>> FASE 3: CORTE ({start_t:.1f}s - {end_t:.1f}s)")
        if trim_audio:
            trim_audio.trim_audio(raw_audio, start_t, end_t, final_audio_path)
        else:
            # Fallback to shell execution if import failed
            cmd = ["python", "scripts/trim_audio.py", raw_audio, str(start_t), str(end_t), "-o", final_audio_path]
            import subprocess
            subprocess.run(cmd, check=True)

        # 4. ANALYZER
        print("\n>>> FASE 4: ANÁLISE ESPECTRAL")
        json_path = os.path.join(data_dir, f"{base_name}.json")
        analyzer.analyze_music(final_audio_path, json_path)

    # 5. RENDERER
    print("\n>>> FASE 5: RENDERIZAÇÃO DE VÍDEO")
    
    # Rotation Logic
    manager = StyleManager()
    style_data = manager.get_next_style()
    
    engine_type = style_data['type']
    selected_style = style_data['name']
    
    final_video_path = os.path.join(video_dir, f"{base_name}_{selected_style}.mp4")

    print(f"🎨 ESTILO SELECIONADO: [{engine_type.upper()}] {selected_style}")

    if dry_run:
        print(f"Simulando execução de: {selected_style}")
        print(f"Comando simulado: uv run src/engines/{engine_type}/{selected_style}.py {final_audio_path} -o {final_video_path}")
        return

    if engine_type == "pygame":
        render_video_v2.render_video(final_audio_path, json_path, final_video_path, theme=selected_style)
    else:
        # Matplotlib Execution via Subprocess
        # We assume the script is named exactly as the style name in src/engines/matplotlib/
        script_path = os.path.join("src", "engines", "matplotlib", f"{selected_style}.py")
        
        if not os.path.exists(script_path):
            print(f"🛑 Erro Crítico: Script Engine '{script_path}' não encontrado!")
            return

        # Call with standardized arguments: <audio> -o <output>
        cmd = ["uv", "run", script_path, final_audio_path, "-o", final_video_path]
        
        print(f"🚀 Executing Matplotlib Engine: {selected_style}")
        import subprocess
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro na renderização Matplotlib: {e}")

    print("\n" + "="*50)
    print(f"✅ CICLO COMPLETO COM SUCESSO!")
    print(f"📁 Vídeo Final: {final_video_path}")
    print("="*50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nexus V2 Autonomous Content Pipeline")
    parser.add_argument("query", nargs='?', default="phonk drift 2026", help="Search query for YouTube")
    parser.add_argument("--duration", type=int, default=30, help="Duration of the final clip in seconds")
    parser.add_argument("--count", type=int, default=1, help="Number of videos to generate (or simulate)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate style rotation without heavy rendering")
    
    args = parser.parse_args()
    
    for i in range(args.count):
        print(f"\n🌀 ITERAÇÃO {i+1}/{args.count}")
        run_pipeline(args.query, args.duration, dry_run=args.dry_run)
