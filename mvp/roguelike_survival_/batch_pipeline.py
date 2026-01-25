import sys
import subprocess
import os

def main():
    try:
        count = sys.argv[1] if len(sys.argv) > 1 else "1"
    except IndexError:
        count = "1"
        
    print(f"🚀 Launching Roguelike Manager with count={count}")
    
    # Ensure output directory exists
    output_dir = "batch_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Call manager.py render --count X --output-dir batch_output
    cmd = [
        sys.executable, "manager.py", "render",
        "--count", str(count),
        "--output-dir", output_dir
    ]
    
    subprocess.check_call(cmd)

if __name__ == "__main__":
    main()
