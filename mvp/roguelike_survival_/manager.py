import os
import sys
import argparse
import logging
import random
import time
import numpy as np
import multiprocessing
from functools import partial

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# --- HEADLESS CONFIGURATION ---
def setup_headless():
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    # Ensure audio doesn't crash in headless
    os.environ["SDL_AUDIODRIVER"] = "dummy"

# Defer pygame import
import pygame
from src.config import SCREEN_W, SCREEN_H, TARGET_FPS, PATH_MUSIC
from src.render_engine import RenderEngine

def mode_play(args):
    """Interactive Play Mode"""
    logger.info("Starting Interactive Mode...")
    
    width, height = SCREEN_W, SCREEN_H
    display_scale = 0.5
    win_w, win_h = int(width * display_scale), int(height * display_scale)
    
    pygame.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    
    screen = pygame.display.set_mode((win_w, win_h))
    pygame.display.set_caption("Neon Survivor - Interactive")
    clock = pygame.time.Clock()
    
    engine = RenderEngine(width, height)
    running = True
    
    while running:
        dt = clock.tick(TARGET_FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                if event.key == pygame.K_r: engine.reset()

        engine.step(dt)
        
        frame_array = engine.render()
        frame_surf = pygame.surfarray.make_surface(frame_array.transpose([1, 0, 2]))
        scaled_surf = pygame.transform.smoothscale(frame_surf, (win_w, win_h))
        
        screen.blit(scaled_surf, (0, 0))
        pygame.display.flip()
        
        if engine.game_over:
            pass

    pygame.quit()

def render_single_video(video_index, args):
    """Worker function for multiprocessing"""
    setup_headless()
    import imageio
    try:
        from moviepy.editor import AudioFileClip, VideoFileClip
        from moviepy.audio.fx.all import audio_fadeout
    except ImportError:
        # Fallback for newer moviepy versions or different structures
        from moviepy import AudioFileClip, VideoFileClip
        from moviepy.audio.fx import audio_fadeout
    
    # We must init pygame inside the process
    pygame.init()
    
    output_dir = args.output_dir
    width, height = SCREEN_W, SCREEN_H
    if args.preview:
        scale = 0.5
        width, height = int(width * scale), int(height * scale)
        if width % 2 != 0: width += 1
        if height % 2 != 0: height += 1

    engine = RenderEngine(width, height)
    temp_name = f"temp_{os.getpid()}_{video_index}.mp4"
    temp_video_path = os.path.join(output_dir, temp_name)
    
    fps = TARGET_FPS
    writer = imageio.get_writer(
        temp_video_path, 
        fps=fps, 
        codec='libx264', 
        quality=None, 
        bitrate='8000k' if not args.preview else '2000k', 
        pixelformat='yuv420p'
    )
    
    step = 0
    max_duration = args.duration
    max_steps = max_duration * fps
    
    try:
        while step < max_steps:
            dt = 1.0 / fps
            engine.step(dt)
            frame = engine.render()
            writer.append_data(frame)
            step += 1
            if engine.game_over or engine.victory:
                final_frame = engine.render()
                for _ in range(fps * 2):
                    writer.append_data(final_frame)
                break
    finally:
        writer.close()
            
    # Post-Processing
    try:
        clip = VideoFileClip(temp_video_path)
        music_candidates = []
        local_music = "assets/audio/music"
        if os.path.exists(local_music):
            music_candidates = [os.path.join(local_music, f) for f in os.listdir(local_music) if f.endswith(".mp3")]

        if music_candidates and not args.no_audio:
            music_path = random.choice(music_candidates)
            audio = AudioFileClip(music_path)
            if audio.duration < clip.duration:
                audio = audio.loop(duration=clip.duration)
            else:
                audio = audio.subclip(0, clip.duration)
            
            audio = audio_fadeout(audio, 2.0)
            audio = audio.volumex(0.1)
            clip = clip.set_audio(audio)
        
        output_filename = os.path.join(output_dir, f"render_{int(time.time())}_{video_index}.mp4")
        clip.write_videofile(
            output_filename, 
            codec="libx264", 
            audio_codec="aac", 
            logger=None, 
            preset="fast" if args.preview else "medium"
        )
        clip.close()
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        return output_filename
    except Exception as e:
        return f"Error in {video_index}: {e}"

def mode_render(args):
    """Headless Rendering Mode with Multiprocessing"""
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    num_videos = args.count
    # Use 75% of available cores to avoid total system lockup
    num_cores = max(1, int(multiprocessing.cpu_count() * 0.75))
    if args.count < num_cores: num_cores = args.count

    logger.info(f"Starting Batch Render: {num_videos} videos using {num_cores} cores.")
    
    with multiprocessing.Pool(processes=num_cores) as pool:
        render_func = partial(render_single_video, args=args)
        results = pool.map(render_func, range(num_videos))
        
    for res in results:
        logger.info(res)

def main():
    parser = argparse.ArgumentParser(description="Neon Survivor Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_play = subparsers.add_parser("play", help="Run interactive mode")

    parser_render = subparsers.add_parser("render", help="Render video to file")
    parser_render.add_argument("--count", type=int, default=1, help="Number of videos to generate")
    parser_render.add_argument("--duration", type=int, default=60, help="Max duration in seconds")
    parser_render.add_argument("--output-dir", type=str, default="output", help="Output directory")
    parser_render.add_argument("--preview", action="store_true", help="Render at lower resolution/bitrate for speed")
    parser_render.add_argument("--no-audio", action="store_true", help="Skip audio processing")

    args = parser.parse_args()

    if args.command == "play":
        mode_play(args)
    elif args.command == "render":
        mode_render(args)

if __name__ == "__main__":
    # Essential for multiprocessing on Windows and Linux
    main()