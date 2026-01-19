import subprocess
import os
import sys

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import FPS, FINAL_RES

def create_video():
    """
    Muxes the generated audio into the existing simulation video.
    """
    print("--- Finalizing Video (Muxing Audio) ---")
    
    input_video = "simulation.mp4"
    input_audio = "simulation_audio.wav"
    output_file = "youtube_shorts_final.mp4"
    
    if not os.path.exists(input_video):
        print(f"Error: Video file '{input_video}' not found. Run the simulation first.")
        return

    # FFmpeg Command
    # -i input_video: video stream
    # -i input_audio: audio stream
    # -c:v copy: Copy video stream without re-encoding (FAST)
    # -c:a aac: Encode audio to AAC
    # -map 0:v:0: Use video from first input
    # -map 1:a:0: Use audio from second input
    # -shortest: Stop when the shortest stream ends
    
    cmd = [
        "ffmpeg", "-y",
        "-i", input_video
    ]
    
    has_audio = False
    if os.path.exists(input_audio):
        print(f"Found audio: {input_audio}")
        cmd.extend(["-i", input_audio])
        has_audio = True
    else:
        print("Warning: Audio file not found. Output will be video only.")
        
    if has_audio:
        cmd.extend([
            "-c:v", "copy",       # Don't re-encode video
            "-c:a", "aac",        # Encode audio
            "-b:a", "192k",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest"
        ])
    else:
        # Just copy if no audio (maybe rename or just copy)
        cmd.extend(["-c", "copy"])

    cmd.append(output_file)
    
    print(f"Executing: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n--- SUCCESS! ---")
        print(f"Final video saved as: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during video processing: {e}")
    except FileNotFoundError:
        print("Error: ffmpeg not found in system path.")

if __name__ == "__main__":
    create_video()