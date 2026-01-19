#!/usr/bin/env python3
"""
Batch Pipeline for Marble War Video Generation.
Uses streaming rendering (no frames/ directory).
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add project root for brain access
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

try:
    from brain.shorts_autopilot import ShortsAutopilot
except ImportError:
    print("⚠️ Warning: Could not import ShortsAutopilot. Integration disabled.")
    ShortsAutopilot = None

def generate_batch(count):
    print(f"🚀 Batch Pipeline: Marble War (Count: {count})")
    
    script_dir = Path(__file__).parent
    batch_dir = script_dir / "batch_output"
    batch_dir.mkdir(exist_ok=True)

    for i in range(count):
        print(f"\n{'='*50}")
        print(f"🎬 VIDEO {i+1}/{count}")
        print(f"{'='*50}\n")
        
        try:
            # 1. Generate Video (Streaming)
            print("▶️ Running generate_video.py...")
            subprocess.run(["uv", "run", "generate_video.py"], cwd=script_dir, check=True)
            
            # 2. Render Audio
            print("▶️ Running render_audio.py...")
            subprocess.run(["uv", "run", "render_audio.py"], cwd=script_dir, check=True)
            
            # 3. Move final output
            final_video = script_dir / "final_with_audio.mp4"
            
            if final_video.exists():
                timestamp = int(time.time())
                target = batch_dir / f"marble_war_{timestamp}_{i}.mp4"
                final_video.rename(target)
                print(f"✅ Saved: {target.name}")
                
                # Register with Autopilot
                if ShortsAutopilot:
                    try:
                        autopilot = ShortsAutopilot()
                        autopilot.add_to_queue(video_path=str(target.absolute()))
                        print(f"📡 Queued for upload!")
                    except Exception as e:
                        print(f"⚠️ Autopilot failed: {e}")
                
                # Cleanup
                for tmp in ["output_render.mp4", "audio_events.json"]:
                    tmp_path = script_dir / tmp
                    if tmp_path.exists():
                        tmp_path.unlink()
            else:
                print(f"❌ Error: {final_video} not found")
                
        except Exception as e:
            print(f"❌ Failed video {i+1}: {e}")

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    generate_batch(count)
