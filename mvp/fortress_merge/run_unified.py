import argparse
import subprocess
import sys
import os
from datetime import datetime

def run_fortress(output_name):
    print("🏰 Starting Fortress Merge Simulation...")
    # Define output path
    output_path = os.path.abspath(f"output/{output_name}")
    
    # Ensure output dir exists
    os.makedirs("output", exist_ok=True)
    
    # Pass output filename directly
    cmd = [sys.executable, "generate_video.py", output_path]
    subprocess.run(cmd, check=True)
    
    if os.path.exists(output_path):
        print(f"✅ Fortress Merge video saved to: {output_path}")
    else:
        print("❌ Error: Output file not found.")

def run_tower(output_name):
    print("🗼 Starting Neon Tower Defense Simulation...")
    output_path = os.path.abspath(f"output/{output_name}")
    os.makedirs("output", exist_ok=True)
    
    # Tower Defense main.py accepts an argument for output file
    cmd = [sys.executable, "tower_defense/main.py", output_path]
    
    # We need to run this with CWD as tower_defense root? 
    # Looking at tower_defense/generate_video.py, it adds path to sys.path.
    # Let's try running from root but setting PYTHONPATH.
    
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(os.getcwd(), "tower_defense") + os.pathsep + env.get("PYTHONPATH", "")
    
    subprocess.run(cmd, env=env, check=True)
    print(f"✅ Tower Defense video saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Unified Simulation Runner")
    parser.add_argument("mode", choices=["fortress", "tower"], help="Game mode to simulate")
    parser.add_argument("--output", "-o", help="Output filename", default=None)
    parser.add_argument("--count", "-c", type=int, default=1, help="Number of videos to generate")
    
    args = parser.parse_args()
    
    os.makedirs("output", exist_ok=True)
    
    for i in range(args.count):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{args.mode}_{timestamp}_{i+1}.mp4"
        filename = args.output if args.count == 1 and args.output else default_name
        
        if args.mode == "fortress":
            run_fortress(filename)
        elif args.mode == "tower":
            run_tower(filename)

if __name__ == "__main__":
    main()
