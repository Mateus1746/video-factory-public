import os
import sys
import json
import random
import time
import subprocess
import shutil
import datetime
import glob

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BATCH_OUTPUT_DIR = os.path.join(BASE_DIR, "batch_output")
FRAMES_BASE_DIR = os.path.join(BASE_DIR, "frames")
HISTORY_FILE = os.path.join(BASE_DIR, "batch_history.json")
MAPS_DIR = os.path.join(BASE_DIR, "maps")
HTML_MAPS_DIR = os.path.join(BASE_DIR, "html_maps")
RENDER_SCRIPT = os.path.join(BASE_DIR, "render_frames.js")
MIX_SCRIPT = os.path.join(BASE_DIR, "mix_sfx.py")

def ensure_dirs():
    if not os.path.exists(BATCH_OUTPUT_DIR):
        os.makedirs(BATCH_OUTPUT_DIR)
    if not os.path.exists(FRAMES_BASE_DIR):
        os.makedirs(FRAMES_BASE_DIR)

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def get_available_maps():
    maps = []
    # JSON maps in maps/
    if os.path.exists(MAPS_DIR):
        for f in os.listdir(MAPS_DIR):
            if f.endswith(".json"):
                maps.append(f)
    
    # HTML maps in html_maps/
    if os.path.exists(HTML_MAPS_DIR):
        for f in os.listdir(HTML_MAPS_DIR):
            if f.endswith(".html") and f != "index.html": # Avoid utility htmls if any
                maps.append(f)
    
    return maps

def select_next_map(history, last_map):
    maps = get_available_maps()
    if not maps:
        print("❌ No maps found!")
        sys.exit(1)

    # Initialize history for new maps
    for m in maps:
        if m not in history:
            history[m] = 0

    # Filter out the very last map to avoid immediate repetition (if we have > 1 map)
    candidates = [m for m in maps if m != last_map]
    if not candidates:
        candidates = maps

    # Weighted random based on usage (fewer uses = higher weight)
    # Weight = 1 / (usage + 1)
    weights = [1.0 / (history[m] + 1) for m in candidates]
    
    chosen_map = random.choices(candidates, weights=weights, k=1)[0]
    return chosen_map

def run_step(step_name, command):
    print(f"🔹 [{step_name}] Running: {' '.join(command)}")
    try:
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ [{step_name}] Failed: {e}")
        return False

def main():
    if 'BASE_DIR' in globals(): os.chdir(BASE_DIR)
    ensure_dirs()
    history = load_history()
    last_map = None

    # Parse arguments
    limit = None
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            pass # Ignore if not a number

    print("🚀 Starting Batch Generation Protocol...")
    print(f"📂 Output: {os.path.abspath(BATCH_OUTPUT_DIR)}")
    
    if limit:
        print(f"🎯 Goal: Generate {limit} simulations")
    else:
        print(f"∞ Mode: Generating indefinitely (Ctrl+C to stop)")

    count = 0
    while limit is None or count < limit:
        count += 1
        if limit:
            print(f"\n🎬 Simulation {count}/{limit}")
        
        current_map = select_next_map(history, last_map)
        print(f"\n🎯 Selected Map: {current_map} (Used: {history.get(current_map, 0)} times)")
        
        # 1. Generate Frames & Events
        # Node script expects just the filename
        if not run_step("Render Frames", ["node", RENDER_SCRIPT, current_map]):
            time.sleep(5)
            continue

        # Determine paths
        map_basename = os.path.splitext(current_map)[0]
        # render_frames.js creates a folder with the map basename
        # Caution: If input is 'maps/level1.json', render_frames logic does `path.basename`.
        # So 'level1.json' -> 'level1'. 'html_maps/duel.html' -> 'duel'.
        frame_dir_name = os.path.splitext(os.path.basename(current_map))[0]
        frames_path = os.path.join(FRAMES_BASE_DIR, frame_dir_name)
        events_path = os.path.join(frames_path, "events.json")

        if not os.path.exists(frames_path) or not os.path.exists(events_path):
            print(f"❌ Error: Frames or events not found at {frames_path}")
            continue

        # 2. Compile Video (Silent)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_video_name = f"temp_{timestamp}.mp4"
        temp_video_path = os.path.join(BATCH_OUTPUT_DIR, temp_video_name)
        
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-framerate", "60",
            "-i", os.path.join(frames_path, "frame_%05d.png"),
            "-vf", "scale=1080:1920",
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "slow",
            "-pix_fmt", "yuv420p",
            temp_video_path
        ]

        if not run_step("Compile Video", ffmpeg_cmd):
            continue

        # 3. Mix Audio
        if not run_step("Mix Audio", ["uv", "run", MIX_SCRIPT, events_path, temp_video_path, "60"]): # Using 'uv run' for python environment safety
             print("⚠️ Audio mixing failed, but video exists. Continuing...")

        # 4. Finalize
        final_filename = f"sim_{timestamp}_{frame_dir_name}.mp4"
        final_path = os.path.join(BATCH_OUTPUT_DIR, final_filename)
        os.rename(temp_video_path, final_path)
        
        print(f"✅ Finished: {final_path}")

        # 5. Cleanup Frames
        print("🧹 Cleaning up frames...")
        shutil.rmtree(frames_path)

        # Update History
        history[current_map] = history.get(current_map, 0) + 1
        save_history(history)
        last_map = current_map

        print("⏳ Cooldown 5s...")
        time.sleep(5)

if __name__ == "__main__":
    main()
