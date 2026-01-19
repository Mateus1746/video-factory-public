import yt_dlp
import os
import subprocess
import argparse
import sys

def download_audio(url, output_dir="downloads"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Template for output filename
    output_template = os.path.join(output_dir, '%(title)s.%(ext)s')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_template,
        'quiet': False,
    }

    print(f"Downloading audio from: {url}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # yt-dlp might change extension to mp3 because of postprocessor
        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        mp3_filename = base + ".mp3"
        return mp3_filename

def run_pipeline(url, action="sim", start=None, duration=None, subdiv=1, bpm=None, style="ball"):
    try:
        # 1. Download
        mp3_path = download_audio(url)
        print(f"Download complete: {mp3_path}")
        
        # 2. Trim if needed
        if start or duration:
            trimmed_path = mp3_path.replace(".mp3", "_trimmed.mp3")
            print(f"Trimming audio: start={start}, duration={duration}")
            
            cmd = ["ffmpeg", "-y"]
            if start: cmd.extend(["-ss", str(start)])
            if duration: cmd.extend(["-t", str(duration)])
            cmd.extend(["-i", mp3_path, "-acodec", "copy", trimmed_path])
            
            subprocess.run(cmd, check=True)
            mp3_path = trimmed_path # Use the trimmed version for next steps

        # 4. Choose action based on style
        if style == "ball":
            # Ball V2 requires external analysis JSON
            json_path = mp3_path.replace(".mp3", ".json")
            print(f"Analyzing music for Ball Engine...")
            analyze_cmd = [sys.executable, "src/analyzer.py", mp3_path, "-o", json_path]
            if bpm:
                analyze_cmd.extend(["--bpm", str(bpm)])
            subprocess.run(analyze_cmd, check=True)

            if action == "sim":
                print(f"Starting Interactive Ball Simulation...")
                subprocess.run([sys.executable, "src/engines/pygame/bouncing_ball.py", mp3_path, json_path])
            elif action == "render":
                video_out = mp3_path.replace(".mp3", f"_ball.mp4")
                print(f"Starting Ball Video Rendering...")
                # Note: render_video_v2.py logic needs to be aware of the new location of bouncing_ball or imported correctly
                # Since we moved visualizer_v2 to engines/pygame/bouncing_ball.py, we should update render call too
                # However, for now, let's assume the user runs the pipeline which should call a render script that imports the right engine
                # Or simpler: Call the engine directly if it supports rendering, or a specific render script.
                # Current render_video_v2.py imports visualizer_v2. We need to fix that file too.
                # For now, let's point to the old render script location but we will need to update it next.
                subprocess.run([sys.executable, "src/render_video_v2.py", mp3_path, json_path, "-o", video_out])
                print(f"Video Exported: {video_out}")

        elif style in ["flow", "vortex"]:
            # Matplotlib Engines (Offline Render)
            script_map = {
                "flow": "src/engines/matplotlib/harmonic_flow.py",
                "vortex": "src/engines/matplotlib/vortex.py"
            }
            script_path = script_map.get(style)
            
            if action == "sim":
                print(f"⚠️  Style '{style}' is render-only. Switching to render mode preview...")
            
            video_out = mp3_path.replace(".mp3", f"_{style}.mp4")
            print(f"🚀 Starting {style.title()} Engine Rendering...")
            
            cmd = [sys.executable, script_path, mp3_path, "-o", video_out]
            subprocess.run(cmd, check=True)
            print(f"✅ Video Exported: {video_out}")

    except Exception as e:
        print(f"Error in pipeline: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube to Music Simulation Pipeline")
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("--mode", choices=["sim", "render"], default="sim", help="Action to perform after download")
    parser.add_argument("--style", choices=["ball", "flow", "vortex"], default="ball", help="Visualization Style")
    parser.add_argument("--start", help="Start time (e.g. 30 or 00:00:30)")
    parser.add_argument("--duration", help="Duration in seconds (e.g. 61)")
    parser.add_argument("--subdiv", type=int, default=1, help="Beat subdivisions (1, 2, 4, 8)")
    parser.add_argument("--bpm", type=float, help="BPM Hint to avoid octave errors")
    
    args = parser.parse_args()
    
    # Ensure dependencies like ffmpeg are available
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except:
        print("Error: FFmpeg is required for this pipeline. Please install it.")
        sys.exit(1)
        
    run_pipeline(args.url, args.mode, args.start, args.duration, args.subdiv, args.bpm, style=args.style)
