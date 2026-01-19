import os
import sys
import subprocess
import random
import shutil
import glob

def main():
    """
    Standardized Video Generator for GitHub Actions.
    1. Selects a random map.
    2. Renders frames using Node.js (puppeteer).
    3. Compiles frames to output_render.mp4 using FFmpeg.
    4. Cleans up temporary frames.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    render_script = os.path.join(base_dir, "render_frames.js")
    output_video = os.path.join(base_dir, "output_render.mp4")
    frames_base_dir = os.path.join(base_dir, "frames")
    
    print("🚀 Commander Sim Factory Generator")
    
    # 1. Select Random Map
    maps_dir = os.path.join(base_dir, "maps")
    html_maps_dir = os.path.join(base_dir, "html_maps")
    maps = []
    
    if os.path.exists(maps_dir):
        maps.extend([f for f in os.listdir(maps_dir) if f.endswith(".json")])
    if os.path.exists(html_maps_dir):
        maps.extend([f for f in os.listdir(html_maps_dir) if f.endswith(".html") and f != "index.html"])
        
    if not maps:
        print("❌ No maps found in maps/ or html_maps/!")
        sys.exit(1)
        
    selected_map = random.choice(maps)
    print(f"🎯 Selected Map: {selected_map}")

    # 2. Render Frames (Node.js)
    # Check for node_modules
    if not os.path.exists(os.path.join(base_dir, "node_modules")):
        print("⚠️ node_modules not found! Attempting 'npm install'...")
        try:
            subprocess.run(["npm", "install"], cwd=base_dir, check=True)
        except Exception as e:
            print(f"❌ npm install failed: {e}")
            # Try to continue anyway, maybe global packages? unlikely.
            sys.exit(1)

    print("📸 Rendering frames (Node.js)...")
    try:
        subprocess.run(["node", render_script, selected_map], cwd=base_dir, check=True)
    except subprocess.CalledProcessError:
        print("❌ Rendering failed")
        sys.exit(1)
        
    # Determine where frames were saved
    # render_frames.js uses path.basename(map) to create folder
    map_name_no_ext = os.path.splitext(os.path.basename(selected_map))[0]
    frames_dir = os.path.join(frames_base_dir, map_name_no_ext)
    
    if not os.path.exists(frames_dir):
        print(f"❌ Frames directory not found at: {frames_dir}")
        sys.exit(1)

    # 3. Compile Video with FFmpeg
    print("🎬 Compiling video (FFmpeg)...")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", "60",
        "-i", os.path.join(frames_dir, "frame_%05d.png"),
        "-vf", "scale=1080:1920",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        output_video
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ Video created: {output_video}")
    except subprocess.CalledProcessError:
        print("❌ FFmpeg encoding failed")
        sys.exit(1)

    # 4. Cleanup
    print("🧹 Cleaning up frames...")
    try:
        shutil.rmtree(frames_dir)
    except Exception as e:
        print(f"⚠️ Cleanup failed: {e}")

if __name__ == "__main__":
    main()