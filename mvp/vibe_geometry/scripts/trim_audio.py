import subprocess
import argparse
import sys
import os

def trim_audio(input_file, start_time, end_time, output_file):
    print(f"Trimming audio: {input_file} from {start_time} to {end_time}...")
    
    # Command: ffmpeg -i input -ss start -to end -c copy output
    # -y overwrites output file if it exists
    cmd = [
        "ffmpeg", "-y",
        "-i", input_file,
        "-ss", str(start_time),
        "-to", str(end_time),
        "-c", "copy",
        output_file
    ]
    
    try:
        # We use run with capture_output to silenta ffmpeg logs unless there's an error
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Success! Trimmed audio saved to: {output_file}")
        else:
            print(f"FFmpeg Error: {result.stderr}")
            sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trim an audio file using FFmpeg.")
    parser.add_argument("input", help="Path to input audio file")
    parser.add_argument("start", help="Start time (e.g., 30 or 00:00:30)")
    parser.add_argument("end", help="End time (e.g., 60 or 00:01:00)")
    parser.add_argument("-o", "--output", default="trimmed_audio.mp3", help="Path to output audio file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"File not found: {args.input}")
        sys.exit(1)
        
    trim_audio(args.input, args.start, args.end, args.output)
