import os
import argparse
import subprocess
import random

# NCS Official Uploads Playlist (Valid & Reliable)
PLAYLIST_URL = "https://www.youtube.com/playlist?list=UU_aEa8K-EOJ3D6gOs7HcyNg"

def get_random_video_from_playlist():
    """
    Fetches a random video URL from the defined playlist using yt-dlp.
    It fetches a batch of IDs (e.g., 50 random items) to avoid fetching the whole playlist every time,
    or better: fetches the whole flat list once (it's fast) and picks one.
    """
    try:
        # Fetch all IDs from the playlist (flat-playlist is fast)
        # We limit to first 100 to ensure we get popular ones, or remove limit for full randomness
        cmd = [
            "uv", "run", "yt-dlp", 
            "--flat-playlist", 
            "--get-id", 
            "--playlist-random", # Shuffle on the server side/extraction if possible, or just shuffle output
            "--playlist-end", "50", # Get 50 random candidates
            PLAYLIST_URL
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        video_ids = result.stdout.strip().split('\n')
        video_ids = [vid for vid in video_ids if vid] # Filter empty
        
        if not video_ids:
            # Fallback if fetch fails
            print("⚠️ Could not fetch playlist. Using fallback list.")
            return random.choice([
                "J2X5mJ3HDYE", "yJg-Y5byMMw", "n8X9_MgEdCg", "TW9d8vYrVFQ" 
            ])
            
        chosen_id = random.choice(video_ids)
        return f"https://www.youtube.com/watch?v={chosen_id}"
        
    except Exception as e:
        print(f"⚠️ Playlist fetch error: {e}. Using fallback.")
        return "https://www.youtube.com/watch?v=n8X9_MgEdCg"

def run_batch(count, output_dir):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_abs_dir = os.path.join(script_dir, output_dir)
    
    if not os.path.exists(output_abs_dir):
        os.makedirs(output_abs_dir)

    print(f"🏭 Starting Vibe Geometry Batch: {count} videos...")

    for i in range(count):
        print(f"\n⚡ Processing {i+1}/{count}...")
        
        retries = 0
        max_retries = 5
        success = False
        
        while not success and retries < max_retries:
            try:
                # Dynamically pick a song
                url = get_random_video_from_playlist()
                style = random.choice(["ball", "flow", "vortex"])
                
                # Random start time to make it unique even if same song
                start_time = random.randint(30, 120) 
                duration = 61 # Shorts duration

                print(f"🎵 [Attempt {retries+1}] Song: {url} | Style: {style} | Start: {start_time}s")

                cmd = [
                    "uv", "run", "pipeline.py", 
                    url, 
                    "--mode", "render",
                    "--style", style,
                    "--start", str(start_time),
                    "--duration", str(duration)
                ]
                
                # Run with CWD set to script_dir
                subprocess.run(cmd, cwd=script_dir, check=True)
                
                # Move outputs to batch_output
                downloads_dir = os.path.join(script_dir, "downloads")
                
                if os.path.exists(downloads_dir):
                    for f in os.listdir(downloads_dir):
                        if f.endswith(".mp4"):
                             src = os.path.join(downloads_dir, f)
                             dst = os.path.join(output_abs_dir, f)
                             
                             if os.path.exists(dst):
                                 base, ext = os.path.splitext(f)
                                 dst = os.path.join(output_abs_dir, f"{base}_{random.randint(1000,9999)}{ext}")
                             
                             os.rename(src, dst)
                             print(f"✅ Moved {f} to {output_dir}")
                
                success = True
                
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Failed to generate (Attempt {retries+1}/{max_retries}): {e}")
                print("♻️ Retrying with a different song...")
                retries += 1
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                retries += 1
        
        if not success:
            print(f"❌ Could not generate video {i+1} after {max_retries} attempts. Skipping.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("count", type=int, nargs="?", default=1)
    parser.add_argument("--out_dir", type=str, default="batch_output")
    args = parser.parse_args()
    
    run_batch(args.count, args.out_dir)
