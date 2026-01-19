"""
Main Entry Point
"""
import sys
import os
import time
from sim.engine import GameEngine
from vis.renderer import Renderer
from pipeline.video_gen import VideoEncoder
from pipeline.audio_gen import mix_audio_to_video
from sim import config

def main(output_file=None):
    duration_sec = 30 # Standard Short length
    total_frames = duration_sec * config.FPS
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    temp_video = os.path.join(output_dir, "temp_silent.mp4")
    final_output = output_file if output_file else os.path.join(output_dir, "tower_defense_final.mp4")
    
    print(f"Initializing Neon Simulation -> {final_output}")
    
    # 1. Init
    engine = GameEngine()
    renderer = Renderer(headless=True)
    encoder = VideoEncoder(temp_video)
    
    # Audio Event Log: (timestamp, type)
    audio_events = []
    
    # 2. Start Recording
    encoder.start()
    
    # 3. Loop
    start_time = time.time()
    frame_idx = 0
    
    # Run until game is decided OR hard limit reached
    while engine.game_result == "PLAYING" and frame_idx < config.MAX_SIMULATION_FRAMES:
        frame_idx += 1
        current_ts = frame_idx / config.FPS
        
        # Track initial counts
        old_projs = len(engine.projectiles)
        
        # Update Logic
        engine.update()
        
        # Audio Events from Engine log
        for evt in engine.recent_events:
            # evt is (x, y, type)
            etype = evt[2]
            if etype == "kill":
                audio_events.append((current_ts, "death"))
                audio_events.append((current_ts, "coin"))
            elif etype == "base_hit":
                audio_events.append((current_ts, "death")) 
            elif etype == "explosion":
                audio_events.append((current_ts, "shot")) # Reuse shot for now, maybe deeper?
            elif etype == "airdrop":
                audio_events.append((current_ts, "coin")) # Reuse coin
        
        if len(engine.projectiles) > old_projs:
            # Check the type of the last added projectile
            if engine.projectiles:
                last_p = engine.projectiles[-1]
                if last_p.type == 'rocket':
                    audio_events.append((current_ts, "rocket"))
                else:
                    audio_events.append((current_ts, "shot"))
        
        # Render
        renderer.render(engine)
        
        # Capture
        frame_data = renderer.get_frame_data()
        encoder.write_frame(frame_data)
        
        # Check End Game
        if engine.game_over:
            print(f"Game Over triggered: {engine.game_result} at frame {frame_idx}")
            # Record a few more frames of the Game Over screen
            for _ in range(90): # 1.5 second linger
                renderer.render(engine)
                encoder.write_frame(renderer.get_frame_data())
            break

        # Stats
        if frame_idx % 120 == 0:
            elapsed = time.time() - start_time
            print(f"Frame {frame_idx} | Zombies: {len(engine.zombies)} | FPS: {frame_idx/(elapsed+0.01):.2f}")

    final_duration = frame_idx / config.FPS
            
    # 4. Finish Video
    encoder.finish()
    
    # 5. Add Audio and Polish
    print(f"Mixing Audio for duration: {final_duration:.1f}s...")
    mix_audio_to_video(temp_video, audio_events, final_output, final_duration)
    print(f"Done! Final video at: {final_output}")

if __name__ == "__main__":
    import os
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
