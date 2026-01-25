#!/usr/bin/env python3
"""
Batch Pipeline for Marble War (Refactored).
Orchestrates VideoGenerator and AudioRenderer for continuous production.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from video_generator import VideoGenerator
from audio_renderer import AudioRenderer

try:
    # Optional integration
    sys.path.append(str(project_root.parents[2])) # Grandparent
    from brain.shorts_autopilot import ShortsAutopilot
except ImportError:
    ShortsAutopilot = None

import sys
import time
import concurrent.futures
from pathlib import Path

# ... (imports)

def process_single_video(index, count, output_dir):
    """Worker function for parallel processing."""
    print(f"\n🎬 STARTING VIDEO {index+1}/{count}")
    
    # We need fresh instances per process
    from video_generator import VideoGenerator
    from audio_renderer import AudioRenderer
    
    video_gen = VideoGenerator()
    audio_gen = AudioRenderer()
    
    timestamp = int(time.time())
    temp_video = output_dir / f"temp_{timestamp}_{index}.mp4"
    final_video = output_dir / f"marble_war_{timestamp}_{index}.mp4"
    
    try:
        # A. Generate Video
        events = video_gen.render(temp_video)
        
        if not temp_video.exists() or temp_video.stat().st_size == 0:
            return f"❌ Video {index+1} failed."
            
        # B. Render Audio & Mux
        audio_gen.render(events, temp_video, final_video)
        
        # C. Cleanup
        if temp_video.exists():
            temp_video.unlink()
            
        return f"✨ SUCCESS: {final_video.name}"
    except Exception as e:
        return f"❌ Error in video {index+1}: {e}"

def generate_batch(count):
    print(f"🚀 Parallel Batch Pipeline: Marble War (Target: {count})")
    print("==================================================")
    
    output_dir = project_root / "batch_output"
    output_dir.mkdir(exist_ok=True)
    
    # Determine number of workers (max 2-3 given 8GB RAM constraint)
    max_workers = 2
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_single_video, i, count, output_dir) for i in range(count)]
        
        for future in concurrent.futures.as_completed(futures):
            print(f"📡 {future.result()}")

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    generate_batch(count)