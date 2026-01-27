import sys
import subprocess
import os

def main():
    try:
        count = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    except (IndexError, ValueError):
        count = 1
        
    print(f"🚀 Launching Fortress Merge Unified Runner with count={count}")
    
    # Ensure output directory exists (run_unified handles it, but good practice)
    output_dir = "batch_output" # Changed to match project structure
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # We will split the count between fortress and tower modes if count > 1
    fortress_count = (count + 1) // 2
    tower_count = count // 2
    
    cmds = []
    
    if fortress_count > 0:
        cmds.append([
            sys.executable, "run_unified.py", "fortress",
            "--count", str(fortress_count)
        ])
        
    if tower_count > 0:
        cmds.append([
            sys.executable, "run_unified.py", "tower",
            "--count", str(tower_count)
        ])
    
    for cmd in cmds:
        print(f"Running: {' '.join(cmd)}")
        subprocess.check_call(cmd)
        
    # Move files from output/ to ready_to_upload/ if necessary
    # run_unified.py saves to output/ by default in the current dir
    source_dir = "output"
    if os.path.exists(source_dir):
        for f in os.listdir(source_dir):
            if f.endswith(".mp4"):
                src = os.path.join(source_dir, f)
                dst = os.path.join(output_dir, f)
                os.rename(src, dst)
                print(f"Moved {f} to {output_dir}")

if __name__ == "__main__":
    main()
