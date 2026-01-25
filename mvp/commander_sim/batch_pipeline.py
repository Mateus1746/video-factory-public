import os
import sys
import json
import time
import random
import datetime
import shutil
import config
from pipeline.server import RenderServer
from pipeline.ffmpeg_utils import compile_video, mix_audio

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BATCH_OUTPUT_DIR = os.path.join(BASE_DIR, "batch_output")
FRAMES_BASE_DIR = os.path.join(BASE_DIR, "frames")
RENDER_SERVER_SCRIPT = os.path.join(BASE_DIR, "render_frames.js")

# Content Constants
THEMES = ["NEON", "MAGMA", "MATRIX", "FROST"]
PREFIXES = ["Cyber", "Iron", "Neon", "Shadow", "Solar", "Void", "Quantum", "Apex", "Crimson", "Azure"]
SUFFIXES = ["Legion", "Rebels", "Empire", "Corp", "Dynasty", "Horde", "Vanguard", "Sect", "Dominion", "Front"]

def ensure_dirs():
    if not os.path.exists(BATCH_OUTPUT_DIR): os.makedirs(BATCH_OUTPUT_DIR)
    if not os.path.exists(FRAMES_BASE_DIR): os.makedirs(FRAMES_BASE_DIR)

def generate_names():
    n1 = f"{random.choice(PREFIXES)} {random.choice(SUFFIXES)}"
    n2 = f"{random.choice(PREFIXES)} {random.choice(SUFFIXES)}"
    while n1 == n2: n2 = f"{random.choice(PREFIXES)} {random.choice(SUFFIXES)}"
    return {"player": n1, "enemy": n2}

def main():
    if 'BASE_DIR' in globals(): os.chdir(BASE_DIR)
    ensure_dirs()
    
    server = RenderServer(RENDER_SERVER_SCRIPT, BASE_DIR)
    if not server.start():
        sys.exit(1)

    try:
        limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
        print(f"🚀 Batch Protocol Started. FPS: {config.FPS}")
        
        count = 0
        while limit is None or count < limit:
            count += 1
            if limit: print(f"\n🎬 Simulation {count}/{limit}")
            
            # Content Selection
            theme = random.choice(THEMES)
            names = generate_names()
            print(f"\n🎯 Map: PROCEDURAL | Theme: {theme} | Match: {names['player']} vs {names['enemy']}")
            
            # 1. Render
            render_start = time.time()
            result = server.request_render("GENERATE", theme, names)
            
            if not result.get("success"):
                print("❌ Rendering failed. Skipping...")
                time.sleep(2)
                continue
            
            render_time = time.time() - render_start
            print(f"✅ Rendered {result.get('frames')} frames in {render_time:.1f}s")

            # Paths
            frames_path = os.path.join(FRAMES_BASE_DIR, "GENERATE")
            events_path = os.path.join(frames_path, "events.json")

            # 2. Compile Video
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_video_name = f"temp_{timestamp}.mp4"
            temp_video_path = os.path.join(BATCH_OUTPUT_DIR, temp_video_name)
            
            if not compile_video(frames_path, temp_video_path): continue

            # 3. Mix Audio
            if not mix_audio(events_path, temp_video_path, theme):
                print("⚠️ Audio mixing issue.")

            # 4. Finalize
            final_filename = f"sim_{timestamp}_{theme}_{names['player'].replace(' ', '')}_vs_{names['enemy'].replace(' ', '')}.mp4"
            final_path = os.path.join(BATCH_OUTPUT_DIR, final_filename)
            os.rename(temp_video_path, final_path)

            # 5. Generate SEO Metadata
            metadata = {
                "title": f"{names['player']} vs {names['enemy']} - {theme} World Conquest",
                "description": f"Epic procedural battle in the {theme} biome. {names['player']} faces off against {names['enemy']} in a holographic war simulation.",
                "tags": [theme, "Simulation", "AIBattle", "Procedural", names['player'], names['enemy'], "NeonJuice"],
                "stats": {
                    "frames": result.get('frames'),
                    "theme": theme,
                    "duration_sec": result.get('frames') / config.FPS
                }
            }
            meta_path = final_path.replace(".mp4", ".json")
            with open(meta_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            # 6. Copy Thumbnail to output folder
            thumb_source = os.path.join(frames_path, "thumbnail.jpg")
            if os.path.exists(thumb_source):
                shutil.copy(thumb_source, final_path.replace(".mp4", ".jpg"))
            
            print(f"✨ Finished: {final_filename}")

            # Note: Frames are cleaned by Node server on next run or overwrite.
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
    finally:
        server.stop()

if __name__ == "__main__":
    main()
