import os
import sys
import subprocess
import time
from pathlib import Path

# Add project root to path for 'brain' access
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

try:
    from brain.shorts_autopilot import ShortsAutopilot
except ImportError:
    print("⚠️ Warning: Could not import ShortsAutopilot. Integration disabled.")
    ShortsAutopilot = None

def generate_batch(count):
    print(f"🚀 Starting Batch Generation for Tower Defense (Count: {count})")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    batch_dir = os.path.join(script_dir, "batch_output")
    os.makedirs(batch_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    for i in range(count):
        print(f"🎬 Generating video {i+1}/{count}...")
        try:
            timestamp = int(time.time())
            target_name = os.path.join(batch_dir, f"tower_defense_{timestamp}_{i}.mp4")
            
            # 1. Run Main (Generate + Mix)
            # main.py now accepts output path
            cmd_gen = ["uv", "run", "main.py", target_name]
            subprocess.run(cmd_gen, cwd=script_dir, check=True)
            
            if os.path.exists(target_name):
                print(f"✅ Saved Final: {target_name}")
                
                # Register with Autopilot
                if ShortsAutopilot:
                    try:
                        autopilot = ShortsAutopilot()
                        autopilot.add_to_queue(video_path=os.path.abspath(target_name))
                        print(f"📡 Publisur queued: {os.path.basename(target_name)}")
                    except Exception as e:
                        print(f"⚠️ Autopilot Registration Failed: {e}")
            else:
                print(f"❌ Error: {target_name} not found.")
                
        except Exception as e:
            print(f"❌ Failed to generate video {i+1}: {e}")

if __name__ == "__main__":
    try:
        count = int(sys.argv[1])
    except:
        count = 1
    generate_batch(count)
