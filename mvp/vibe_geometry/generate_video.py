import os
import subprocess
import sys
import random
import yt_dlp
import shutil

# Force headless
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

def download_random_song(base_dir):
    """Downloads a random song from playlist.txt using yt-dlp"""
    playlist_path = os.path.join(base_dir, "playlist.txt")
    
    if not os.path.exists(playlist_path):
        print("⚠️ playlist.txt not found. Using default logic.")
        return None
        
    with open(playlist_path, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    if not urls:
        print("⚠️ Playlist empty.")
        return None
        
    url = random.choice(urls)
    print(f"🎵 Selected URL: {url}")
    
    output_template = os.path.join(base_dir, "temp_music.%(ext)s")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            return os.path.join(base_dir, "temp_music.mp3")
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None

def main():
    print("🚀 Vibe Geometry: Jukebox Factory Generator")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_video = os.path.join(base_dir, "output_render.mp4")
    
    # 1. Get Audio (Download or Default)
    audio_path = download_random_song(base_dir)
    
    # Fallback to local default if download fails
    if not audio_path or not os.path.exists(audio_path):
        fallback = os.path.join(base_dir, "default_track.mp3")
        if os.path.exists(fallback):
            print("⚠️ Using fallback local track.")
            audio_path = fallback
        else:
            print("❌ No audio source found (Download failed and no default_track.mp3).")
            sys.exit(1)
            
    # 2. Analyze Audio
    json_path = audio_path.replace(".mp3", ".json")
    analyzer_script = os.path.join(base_dir, "src", "analyzer.py")
    
    print(f"📊 Analyzing beat map for: {os.path.basename(audio_path)}...")
    try:
        subprocess.run([sys.executable, analyzer_script, audio_path, "-o", json_path], check=True)
    except subprocess.CalledProcessError:
        print("❌ Analysis failed.")
        sys.exit(1)
    
    # 3. Render Video
    render_script = os.path.join(base_dir, "src", "render_video_v2.py")
    print("🎬 Rendering video visualization...")
    
    try:
        subprocess.run([
            sys.executable, render_script, 
            audio_path, 
            json_path, 
            "-o", output_video
        ], check=True)
        print(f"✅ Video successfully rendered: {output_video}")
    except subprocess.CalledProcessError:
        print("❌ Rendering failed.")
        sys.exit(1)
        
    # 4. Cleanup Temp Files (Optional but good for CI)
    if "temp_music" in audio_path:
        try:
            os.remove(audio_path)
            os.remove(json_path)
            print("🧹 Temp music files cleaned.")
        except:
            pass

if __name__ == "__main__":
    main()
