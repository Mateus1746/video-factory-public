import sys
import subprocess
import os

def generate_batch(count):
    print(f"🚀 Starting Batch Generation for Velocity Odds (Count: {count})")
    
    # Use script dir for robustness
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    for i in range(count):
        print(f"🎬 Generating video {i+1}/{count}...")
        try:
            # Call the existing generation script
            cmd = ["uv", "run", "generate_video.py"]
            subprocess.run(cmd, cwd=script_dir, check=True)
            
            # Post-processing
            output_path = os.path.join(script_dir, "output_render.mp4")
            
            if os.path.exists(output_path):
                batch_dir = os.path.join(script_dir, "batch_output")
                os.makedirs(batch_dir, exist_ok=True)
                import time
                timestamp = int(time.time())
                target_name = os.path.join(batch_dir, f"velocity_{timestamp}_{i}.mp4")
                os.rename(output_path, target_name)
                print(f"✅ Saved: {target_name}")
            else:
                print(f"❌ Error: {output_path} not found after generation.")
                
        except Exception as e:
            print(f"❌ Failed to generate video {i+1}: {e}")

if __name__ == "__main__":
    try:
        count = int(sys.argv[1])
    except:
        count = 1
    generate_batch(count)

