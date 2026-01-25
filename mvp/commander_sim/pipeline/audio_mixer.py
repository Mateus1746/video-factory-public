import os
import json
import subprocess
import config

class AudioMixer:
    @staticmethod
    def mix(events_json, video_path, fps=60, theme="NEON"):
        if not os.path.exists(events_json):
            print(f"⚠️ Events file not found: {events_json}")
            return False

        with open(events_json, 'r') as f:
            events = json.load(f)

        print(f"🎧 Mixing Audio | FPS: {fps} | Theme: {theme}")

        # Assets Map
        sfx_assets = {
            'SPAWN': os.path.join(config.ASSETS_DIR, 'audio', 'sfx', 'spawn.wav'),
            'HIT': os.path.join(config.ASSETS_DIR, 'audio', 'sfx', 'hit.wav'),
            'CAPTURE': os.path.join(config.ASSETS_DIR, 'audio', 'sfx', 'capture.wav'),
            'VICTORY': os.path.join(config.ASSETS_DIR, 'audio', 'sfx', 'victory.wav')
        }

        valid_sfx = {k: v for k, v in sfx_assets.items() if os.path.exists(v)}
        
        # FFmpeg Command Builder
        cmd = ["ffmpeg", "-y", "-i", video_path]
        
        # Music Logic
        music_filename = f"music_{theme}.mp3"
        theme_music = os.path.join(config.ASSETS_DIR, 'audio', music_filename)
        default_music = os.path.join(config.ASSETS_DIR, 'audio', 'battle_ambiance.mp3')
        
        bg_music = theme_music if os.path.exists(theme_music) else default_music
        has_music = os.path.exists(bg_music)

        if has_music:
            cmd.extend(["-stream_loop", "-1", "-i", bg_music])

        # Inputs Setup
        sfx_input_map = {} 
        current_input_idx = 2 if has_music else 1
        
        for sfx_type, path in valid_sfx.items():
            cmd.extend(["-i", path])
            sfx_input_map[sfx_type] = current_input_idx
            current_input_idx += 1

        # Filtering Logic
        filter_parts = []
        mix_inputs = []

        if has_music:
            filter_parts.append("[1:a]volume=0.4[bg]")
            mix_inputs.append("[bg]")

        limits = {'SPAWN': 100, 'HIT': 100, 'CAPTURE': 50, 'VICTORY': 5}
        counts = {k: 0 for k in limits}
        sfx_instances = []

        for i, e in enumerate(events):
            etype = e['type']
            if etype not in sfx_input_map: continue
            if counts.get(etype, 0) >= limits.get(etype, 999): continue
            
            counts[etype] += 1
            delay = int((e['frame'] / float(fps)) * 1000)
            
            idx = sfx_input_map[etype]
            label = f"sfx_{i}"
            filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[{label}]")
            sfx_instances.append(f"[{label}]")

        if not sfx_instances and not has_music:
            print("⚠️ Nothing to mix.")
            return True

        all_mix_inputs = mix_inputs + sfx_instances
        amix_cmd = f"{''.join(all_mix_inputs)}amix=inputs={len(all_mix_inputs)}:duration=first:dropout_transition=0[outa]"
        filter_parts.append(amix_cmd)
        
        temp_video = video_path.replace(".mp4", "_temp.mp4")

        cmd.extend([
            "-filter_complex", ";".join(filter_parts),
            "-map", "0:v", "-map", "[outa]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest", temp_video
        ])

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            os.replace(temp_video, video_path)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ FFmpeg Mix Error: {e.stderr.decode()}")
            if os.path.exists(temp_video): os.remove(temp_video)
            return False
