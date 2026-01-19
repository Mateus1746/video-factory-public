import os
import sys
import shutil
import time
import re

# Set headless mode
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import src.config
# Force export config
src.config.EXPORT_MODE = True
src.config.SCREEN_WIDTH = 1080
src.config.SCREEN_HEIGHT = 1920
src.config.FPS = 60

from src.engine import SimulationEngine

def run_single_simulation():
    # Debug ffmpeg
    print(f"DEBUG: Check ffmpeg -> {shutil.which('ffmpeg')}")
    
    # Use a unique temporary filename based on PID to avoid collisions
    temp_video = f"temp_video_{os.getpid()}.mp4"
    temp_audio = "simulation_audio.wav" # Engine saves to this hardcoded name
    
    print(f"--- Single Simulation PID={os.getpid()} ---")
    print(f"DEBUG: Expecting temp_video at: {os.path.abspath(temp_video)}")
    print(f"DEBUG: Expecting temp_audio at: {os.path.abspath(temp_audio)}")
    
    # try:  <-- REMOVIDO para expor o erro real
    # Initialize Engine with output filename
    engine = SimulationEngine(output_filename=temp_video)
    
    top_name = engine.battle_manager.top_name
    bot_name = engine.battle_manager.bot_name
    print(f"Matchup: {top_name} vs {bot_name}")
    
    # Run
    engine.run()
    
    # Get winner info
    winner_tag = "draw"
    if engine.battle_manager.winner_text:
        if top_name in engine.battle_manager.winner_text:
            winner_tag = "top_wins"
        elif bot_name in engine.battle_manager.winner_text:
            winner_tag = "bot_wins"
        elif "TIE" in engine.battle_manager.winner_text:
            winner_tag = "tie"
    
    # Sanitize names
    def sanitize(n): return re.sub(r'[^\w]+', '_', n).lower()
    s_top = sanitize(top_name)
    s_bot = sanitize(bot_name)
    
    base_name = f"{s_top}_vs_{s_bot}_{winner_tag}_{int(time.time())}"
    
    # Output files
    # Force standard name for CI pipeline
    final_video_name = "output_render.mp4"
    
    # Check if we have both components
    has_video = os.path.exists(temp_video)
    has_audio = os.path.exists(temp_audio)
    
    print(f"DEBUG: Current Dir: {os.getcwd()}")
    print(f"DEBUG: Directory Listing: {os.listdir('.')}")
    
    if has_video and has_audio:
        print(f"Merging audio and video into {final_video_name}...")
        # Use ffmpeg to merge
        # -c:v copy (copy video stream, no re-encode)
        # -c:a aac (encode audio to aac)
        # -shortest (finish when shortest stream ends)
        cmd = f'ffmpeg -y -v error -i {temp_video} -i {temp_audio} -c:v copy -c:a aac -shortest {final_video_name}'
        ret = os.system(cmd)
        
        if ret != 0:
            print("❌ ERROR: FFMPEG merging failed!")
            sys.exit(1)
        
        # Cleanup temps
        if os.path.exists(temp_video): os.remove(temp_video)
        if os.path.exists(temp_audio): os.remove(temp_audio)
        
        print(f"SUCCESS: Created {final_video_name}")
    elif has_video:
        print("Warning: Audio missing. Renaming video only.")
        os.rename(temp_video, final_video_name)
    else:
        print("❌ CRITICAL ERROR: No video generated. Engine failed silently?")
        sys.exit(1) # Force fail

    # except Exception as e:
    #     print(f"CRITICAL ERROR: {e}")
    #     import traceback
    #     traceback.print_exc()
    #     sys.exit(1) # Force fail
    
    # Cleanup
    try:
        import pygame
        pygame.quit()
    except:
        pass

if __name__ == "__main__":
    run_single_simulation()
