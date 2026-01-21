import os
import sys
import glob
import time
import shutil
import argparse

def tag_video(directory, project_name):
    # 1. Find the latest MP4 file in the directory
    search_pattern = os.path.join(directory, "*.mp4")
    files = glob.glob(search_pattern)
    
    # Filter out files that already start with the project name to avoid re-tagging
    # Also ignore temp files if any still exist
    candidates = [
        f for f in files 
        if not os.path.basename(f).startswith(project_name)
        and "temp" not in os.path.basename(f)
    ]
    
    if not candidates:
        print(f"⚠️ No new untagged MP4 files found in {directory}")
        return

    # Sort by modification time (newest first)
    candidates.sort(key=os.path.getmtime, reverse=True)
    latest_video = candidates[0]
    
    # 2. Generate new name
    # Format: ProjectName_Timestamp.mp4
    timestamp = int(time.time())
    new_filename = f"{project_name}_{timestamp}.mp4"
    new_path = os.path.join(os.path.dirname(latest_video), new_filename)
    
    # 3. Rename
    try:
        os.rename(latest_video, new_path)
        print(f"🏷️ Tagged video:\n   From: {os.path.basename(latest_video)}\n   To:   {new_filename}")
    except OSError as e:
        print(f"❌ Error renaming file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, help="Directory containing the generated video")
    parser.add_argument("--project", required=True, help="Project name (Channel Identifier)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.dir):
        print(f"❌ Directory not found: {args.dir}")
        # Don't exit with error code 1 here, just warn, so workflow continues
        sys.exit(0)
        
    tag_video(args.dir, args.project)