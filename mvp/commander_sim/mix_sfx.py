import json
import subprocess
import os
import sys

def mix_sfx(events_json, video_path):
    with open(events_json, 'r') as f:
        events = json.load(f)

    # Use a temporary file for the new video
    temp_video = video_path.replace(".mp4", "_temp.mp4")
    
    # Map types to files
    sfx_map = {
        'SPAWN': 'assets/audio/sfx/spawn.wav',
        'HIT': 'assets/audio/sfx/hit.wav',
        'CAPTURE': 'assets/audio/sfx/capture.wav',
        'VICTORY': 'assets/audio/sfx/victory.wav'
    }

    # Prepare inputs for FFmpeg
    # Input 0: Video (Silent)
    cmd = ["ffmpeg", "-y", "-i", video_path]
    
    # Input 1: Background Music
    bg_music = "assets/audio/battle_ambiance.mp3"
    has_music = os.path.exists(bg_music)
    
    if has_music:
        cmd.extend(["-stream_loop", "-1", "-i", bg_music])
    
    # Limit events
    limited_events = []
    counts = {'SPAWN': 0, 'HIT': 0, 'CAPTURE': 0, 'VICTORY': 0}
    for e in events:
        etype = e['type']
        if etype not in sfx_map: continue
        
        limit = 50 if etype in ['SPAWN', 'HIT'] else 200
        if counts[etype] < limit:
            limited_events.append(e)
            counts[etype] += 1
    
    if len(sys.argv) > 3:
        fps = int(sys.argv[3])
    else:
        fps = 30

    print(f"Running FFmpeg mixer for {len(limited_events)} events at {fps} FPS...")
    
    filter_parts = []
    
    # Start SFX inputs from index 2 (0=video, 1=music)
    input_offset = 2 if has_music else 1

    for i, e in enumerate(limited_events):
        cmd.extend(["-i", sfx_map[e['type']]])
        delay = int((e['frame'] / float(fps)) * 1000)
        filter_parts.append(f"[{i+input_offset}:a]adelay={delay}|{delay}[a{i}]")

    # Construct Filter Complex
    # Start with music volume adjustment if present
    mix_inputs = []
    if has_music:
        filter_parts.insert(0, "[1:a]volume=0.4[bg]")
        mix_inputs.append("[bg]")
    
    # Add all SFX streams
    for i in range(len(limited_events)):
        mix_inputs.append(f"[a{i}]")
    
    if not mix_inputs:
        print("Nothing to mix.")
        return

    # amix
    # inputs=N
    amix_cmd = f"{''.join(mix_inputs)}amix=inputs={len(mix_inputs)}:duration=first:dropout_transition=0[outa]"
    filter_parts.append(amix_cmd)
    
    filter_complex = ";".join(filter_parts)
    
    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[outa]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        temp_video
    ])

    # print("Full Command:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    
    # Replace original with mixed version
    os.replace(temp_video, video_path)
    print("Mix successful!")

if __name__ == "__main__":
    mix_sfx(sys.argv[1], sys.argv[2])