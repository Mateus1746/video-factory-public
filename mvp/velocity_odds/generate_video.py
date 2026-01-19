import os
import sys
import subprocess
import pygame
import math
from config import *
from simulation import Simulation
from visuals import Particle, Trail, draw_neon_arc, ScreenShake
from video_renderer import VelocityOddsRenderer

# Flags for Headless
WIDTH = 1080
HEIGHT = 1920
FPS = 60
DURATION = 60 # Default duration

os.environ["SDL_VIDEODRIVER"] = "dummy"

class FFMPEGRecorder:
    def __init__(self, output_file="output_render.mp4"):
        command = [
            'ffmpeg',
            '-y',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-s', f'{WIDTH}x{HEIGHT}',
            '-pix_fmt', 'rgb24',
            '-r', str(FPS),
            '-i', '-',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '20',
            '-pix_fmt', 'yuv420p',
            output_file
        ]
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE)
        self.frame_count = 0
        self.total_frames = FPS * DURATION

    def capture(self, surface):
        try:
            data = pygame.image.tobytes(surface, 'RGB')
            self.process.stdin.write(data)
            self.frame_count += 1
            if self.frame_count % 60 == 0:
                print(f"\r⏳ Rendering: {self.frame_count}/{self.total_frames} frames", end="")
        except Exception:
            pass

    def stop(self):
        print("\n✅ Encoding finished.")
        if self.process.stdin:
            self.process.stdin.close()
        self.process.wait()

def main():
    """Main video generation orchestration."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    # Initialize systems
    sim = Simulation()
    renderer = VelocityOddsRenderer(WIDTH, HEIGHT)
    recorder = FFMPEGRecorder()
    
    # Visual effects
    particles = []
    shaker = ScreenShake()
    trails = [Trail(p.color) for p in sim.players]
    
    # Victory tracking
    winner_frame = None
    POST_VICTORY_FRAMES = FPS * 2  # 2 seconds after victory
    MAX_FRAMES = FPS * 90  # Safety limit: 90 seconds max
    
    # Render loop
    while recorder.frame_count < recorder.total_frames:
        dt = 1 / FPS  # Fixed timestep for stability
        
        # Update simulation
        sim.update(dt)
        shaker.update()
        
        # Handle events and spawn particles
        if sim.last_event:
            _handle_event(sim, particles, shaker)
        
        sim.last_event = None
        
        # Update effects
        particles = [p for p in particles if p.life > 0]
        for p in particles:
            p.update()
        
        # Update trails
        for idx, player in enumerate(sim.players):
            if not player.finished:
                screen_x = CENTER[0] + player.pos_x
                screen_y = CENTER[1] + player.pos_y
                trails[idx].update(screen_x, screen_y)
        
        # Render frame
        renderer.render_frame(screen, sim, particles, trails, shaker, recorder.frame_count)
        
        # Capture to video
        recorder.capture(screen)
        
        # Check for winner and mark victory frame
        if sim.winner_player is not None and winner_frame is None:
            winner_frame = recorder.frame_count
            print(f"\n🏆 Winner detected at frame {winner_frame}! Adding {POST_VICTORY_FRAMES/FPS:.1f}s celebration...")
        
        # End conditions:
        # 1. If we have a winner and showed celebration (5s after victory)
        # 2. Safety limit reached (90s max)
        if winner_frame is not None and (recorder.frame_count - winner_frame) >= POST_VICTORY_FRAMES:
            print(f"\n✅ Victory celebration complete. Total frames: {recorder.frame_count}")
            break
        
        if recorder.frame_count >= MAX_FRAMES:
            print(f"\n⚠️ Safety limit reached (90s). Ending video...")
            break
    
    recorder.stop()
    pygame.quit()


def _handle_event(sim, particles, shaker):
    """Handle simulation events and spawn visual effects."""
    ev_type, p_idx = sim.last_event
    
    # Get event origin position
    if p_idx >= 0:
        p_obj = sim.players[p_idx]
        px, py = CENTER[0] + p_obj.pos_x, CENTER[1] + p_obj.pos_y
    else:
        px, py = CENTER
    
    # Spawn particles based on event type
    if ev_type == "bounce_gain":
        for _ in range(5):
            particles.append(Particle(px, py, NEON_GREEN))
    
    elif ev_type == "bounce_loss":
        shaker.trigger(4)
        for _ in range(5):
            particles.append(Particle(px, py, NEON_RED))
    
    elif ev_type == "levelup":
        shaker.trigger(10)
        for _ in range(12):
            particles.append(Particle(px, py, sim.players[p_idx].color))
    
    elif ev_type == "item_collect":
        shaker.trigger(15)
        
        # Determine chaos color
        burst_col = WHITE
        if sim.current_chaos == "INVERT":
            burst_col = COLOR_EVENT_INVERT
        elif sim.current_chaos == "TURBO":
            burst_col = COLOR_EVENT_TURBO
        elif sim.current_chaos == "MOON":
            burst_col = COLOR_EVENT_MOON
        elif sim.current_chaos == "GLITCH":
            burst_col = COLOR_EVENT_GLITCH
        
        for _ in range(20):
            particles.append(Particle(px, py, burst_col))
    
    elif ev_type == "pvp_collision":
        shaker.trigger(6)
        for _ in range(5):
            particles.append(Particle(px, py, WHITE))

if __name__ == "__main__":
    main()
