import os
import argparse
import subprocess
import time
import shutil

def run_batch(count, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = "run_simulation_headless.py"
    
    print(f"Starting batch of {count} simulations...")
    
    for i in range(count):
        print(f"\n=== Batch Simulation {i+1}/{count} ===")
        
        # Run the single simulation script as a subprocess
        # This ensures a completely clean environment (memory, pygame, ffmpeg) for each run.
        try:
            # We run it in the current directory. 
            # The script outputs files to CWD. We will move them to output_dir.
            subprocess.run(["uv", "run", "--with", "pygame", script_path], cwd=script_dir, check=True)
            
            # Move generated mp4 files to output_dir
            # We look for files created in the last minute matching our pattern or just move all .mp4s
            # that are not temp files.
            
            for f in os.listdir("."):
                if f.endswith(".mp4") and "vs" in f:
                    src = f
                    dst = os.path.join(output_dir, f)
                    shutil.move(src, dst)
                    print(f"Moved {f} to {output_dir}")
                    
        except subprocess.CalledProcessError as e:
            print(f"Simulation {i+1} failed with code {e.returncode}")
        except Exception as e:
            print(f"Batch error: {e}")
            
        # Optional delay
        time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("count", type=int, nargs="?", default=1)
    parser.add_argument("--out_dir", type=str, default="batch_output")
    args = parser.parse_args()
    
    run_batch(args.count, args.out_dir)