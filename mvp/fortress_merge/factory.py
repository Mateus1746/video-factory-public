import subprocess
import os
import argparse
import random
import time
import shutil
from datetime import datetime

def generate_metadata(mode, filename):
    """Generates optimized Title, Description and Tags for YouTube Shorts."""
    
    # Templates
    titles_fortress = [
        "SATISFYING Fortress Merge - Level 99 GOD MODE! 😱 #shorts",
        "Can I Survive Wave 50? IMPOSSIBLE Fortress Defense 🛡️ #shorts",
        "Oddly Satisfying Merge Gameplay - Wait for the Nuke! ☢️ #shorts",
        "Best Strategy for Fortress Merge 2026 🏆 #shorts",
        "ASMR Defense: Perfect Grid Setup 🎧 #shorts"
    ]
    
    titles_tower = [
        "Neon Tower Defense: ROCKET LAUNCHER vs 1000 ZOMBIES! 🚀 #shorts",
        "Satisfying Zombie Horde Defense - 99.9% FAIL! 💀 #shorts",
        "Upgrading to MAX LEVEL Minigun! 🔫 #towerdefense #shorts",
        "Cyberpunk Defense: They Never Stood a Chance! 🤖 #shorts",
        "Ultimate Strategy: Sniper Wall Setup 🎯 #shorts"
    ]
    
    title = random.choice(titles_fortress) if mode == "fortress" else random.choice(titles_tower)
    
    desc = f"""
{title}

🎮 Game: {mode.upper().replace("_", " ")}
🔥 Status: Auto-Generated Gameplay
📅 Date: {datetime.now().strftime("%Y-%m-%d")}

Subscribe for daily satisfying defense videos! 
#towerdefense #strategy #gaming #mobilegames #satisfying #asmr
    """.strip()
    
    tags = "tower defense, fortress merge, strategy game, satisfying video, asmr gaming, mobile game ad, viral shorts"
    
    return title, desc, tags

def run_factory(total_count, mix_ratio=0.5):
    """
    Orchestrates the generation of mixed content.
    mix_ratio: Probability of generating Tower Defense (0.0 = All Fortress, 1.0 = All Tower)
    """
    print(f"🏭 [NEXUS FACTORY] Initializing Production Line")
    print(f"🎯 Target: {total_count} videos")
    print(f"⚖️  Mix Ratio (Tower Defense): {mix_ratio*100}%")
    
    # Pasta final para upload
    output_dir = os.path.abspath("ready_to_upload")
    os.makedirs(output_dir, exist_ok=True)
    
    success_count = 0
    
    for i in range(total_count):
        # Decisão de Pauta (Randomizada com peso)
        mode = "tower" if random.random() < mix_ratio else "fortress"
        
        # Gerar ID único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = f"Short_{i+1:03d}_{mode.upper()}_{timestamp}.mp4"
        meta_name = f"Short_{i+1:03d}_{mode.upper()}_{timestamp}.txt"
        
        print(f"\n🎬 [JOB {i+1}/{total_count}] Starting Production: {mode.upper()}")
        print(f"   📄 File: {project_name}")
        
        start_time = time.time()
        
        try:
            # Chama o executor unificado
            # Usa 'uv run' para garantir que as dependências (numpy, pygame, etc) estejam carregadas
            cmd = ["uv", "run", "run_unified.py", mode, "--output", project_name]
            
            # Captura logs para debug se falhar
            result = subprocess.run(cmd, capture_output=False, text=True, check=True)
            
            # O run_unified salva em output/, precisamos mover para ready_to_upload/
            source_path = os.path.join("output", project_name)
            dest_path = os.path.join(output_dir, project_name)
            meta_path = os.path.join(output_dir, meta_name)
            
            if os.path.exists(source_path):
                shutil.move(source_path, dest_path)
                
                # Generate Metadata
                title, desc, tags = generate_metadata(mode, project_name)
                with open(meta_path, "w") as f:
                    f.write(f"TITLE:\n{title}\n\nDESCRIPTION:\n{desc}\n\nTAGS:\n{tags}")
                
                elapsed = time.time() - start_time
                print(f"   ✅ Success! Render time: {elapsed:.1f}s")
                print(f"   📦 Stocked at: {dest_path}")
                print(f"   📝 Metadata saved to: {meta_name}")
                success_count += 1
            else:
                print(f"   ❌ Error: Output file missing at {source_path}")
                
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Production Failed: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected Error: {e}")

    print(f"\n{'='*40}")
    print(f"🏁 Factory Run Complete")
    print(f"📊 Yield: {success_count}/{total_count} Videos Ready")
    print(f"📁 Location: {output_dir}")
    print(f"{'='*40}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nexus Content Factory Controller")
    parser.add_argument("--count", "-n", type=int, default=1, help="Total videos to generate")
    parser.add_argument("--ratio", "-r", type=float, default=0.5, help="Ratio of Tower Defense videos (0.0 to 1.0)")
    
    args = parser.parse_args()
    
    run_factory(args.count, args.ratio)
