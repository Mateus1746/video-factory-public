import sys
import subprocess
import os

def generate_batch(count):
    print(f"🚀 Starting Batch Generation for Fortress Merge (Count: {count})")
    
    for i in range(count):
        print(f"🎬 Generating video {i+1}/{count}...")
        try:
            # Call the existing generation script
            # We use 'uv run' ensuring dependencies are met if needed, or just python relative
            script_dir = os.path.dirname(os.path.abspath(__file__))
            cmd = ["uv", "run", "generate_video.py"]
            subprocess.run(cmd, cwd=script_dir, check=True)
            
            # Post-processing: Move output_render.mp4 to batch_output with unique name
            output_path = os.path.join(script_dir, "output_render.mp4")
            if os.path.exists(output_path):
                batch_dir = os.path.join(script_dir, "batch_output")
                os.makedirs(batch_dir, exist_ok=True)
                import time
                timestamp = int(time.time())
                target_name = os.path.join(batch_dir, f"fortress_{timestamp}_{i}.mp4")
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
