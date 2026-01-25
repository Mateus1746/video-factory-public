import os
import sys
import subprocess
import pygame
import math
import json
import time
import random
from config import *
from simulation import Simulation
from visuals import Particle, Trail, draw_neon_arc, ScreenShake, FloatingText
from video_renderer import VelocityOddsRenderer
import sound_gen

# Global Constants
WIDTH = 1080
HEIGHT = 1920
FPS = 60

os.environ["SDL_VIDEODRIVER"] = "dummy"

def get_ffmpeg_command(output_file):
    return [
        'ffmpeg', '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo',
        '-s', f'{WIDTH}x{HEIGHT}', '-pix_fmt', 'rgb24', '-r', str(FPS),
        '-i', '-', '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23',
        '-pix_fmt', 'yuv420p', output_file
    ]

class FFMPEGRecorder:
    def __init__(self, output_file="temp_video.mp4"):
        self.output_file = output_file
        command = get_ffmpeg_command(output_file)
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        self.frame_count = 0

    def capture(self, surface):
        try:
            data = pygame.image.tobytes(surface, 'RGB')
            self.process.stdin.write(data)
            self.frame_count += 1
        except:
            self.stop()
            raise

    def stop(self):
        if self.process:
            self.process.communicate()
            self.process = None

def mux_audio_video(video_path, audio_path, output_path):
    command = ['ffmpeg', '-y', '-i', video_path, '-i', audio_path, '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0', '-shortest', output_path]
    subprocess.run(command, capture_output=True)

def main():
    start_time = time.time()
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    sim = Simulation()
    renderer = VelocityOddsRenderer(WIDTH, HEIGHT)
    
    sim.trigger_chaos(random.choice(['TURBO', 'INVERT', 'GLITCH', 'MOON']))
    
    temp_video = "temp_video.mp4"
    temp_audio = "temp_audio.wav"
    output_file = "final_output.mp4"
    
    recorder = FFMPEGRecorder(temp_video)
    particles, floating_texts = [], []
    shaker = ScreenShake()
    trails = [Trail(p.color) for p in sim.players]
    
    end_frame = None
    POST_VICTORY_FRAMES = FPS * 3 # 3 segundos de celebração final
    
    try:
        while True:
            dt = 1 / FPS
            sim.update(dt)
            shaker.update()
            current_zoom = renderer.zoom_level
            
            if sim.last_event:
                _handle_event(sim, particles, floating_texts, shaker, renderer, current_zoom)
            sim.last_event = None
            
            particles = [p for p in particles if p.life > 0]
            for p in particles: p.update()
            floating_texts = [ft for ft in floating_texts if ft.life > 0]
            for ft in floating_texts: ft.update()
            
            for idx, player in enumerate(sim.players):
                if not player.finished:
                    trails[idx].update(CENTER[0] + player.pos_x * current_zoom, CENTER[1] + player.pos_y * current_zoom)
            
            renderer.render_frame(screen, sim, particles, trails, floating_texts, shaker, recorder.frame_count)
            recorder.capture(screen)
            
                        # Condição de Fim: Todos terminaram
            
                        if sim.game_over and end_frame is None:
            
                            end_frame = recorder.frame_count
            
                            win_text = f"WINNER: {sim.winner_player.name}!"
            
                            # Adiciona o texto e garante que ele dure a celebração toda
            
                            winner_msg = FloatingText(WIDTH//2, HEIGHT//2, win_text, sim.winner_player.color, renderer.font_big)
            
                            winner_msg.life = 10.0 # Vida longa para não sumir nos 2 segundos
            
                            floating_texts.append(winner_msg)
            
                            print(f"\n🏆 Game Over! Winner: {sim.winner_player.name} (${sim.winner_player.money:,.0f})")
            
                        
            
                        # Só encerra o loop APÓS os quadros de celebração
            
                        if end_frame is not None and (recorder.frame_count - end_frame) >= POST_VICTORY_FRAMES:
            
                            break
            
            
            if recorder.frame_count > FPS * 180: break
            
            if recorder.frame_count % 60 == 0:
                print(f"\r⏳ Rendering: {recorder.frame_count} frames", end="")
                
    finally:
        recorder.stop()
        events_path = "audio_events.json"
        with open(events_path, "w") as f: json.dump(sim.audio_events, f)
        sound_gen.generate_sync_audio(events_path, temp_audio, recorder.frame_count / FPS)
        mux_audio_video(temp_video, temp_audio, output_file)
        for f in [temp_video, temp_audio, events_path]:
            if os.path.exists(f): os.remove(f)
        print(f"\n✨ Completed in {time.time() - start_time:.1f}s -> {output_file}")
        pygame.quit()

def _handle_event(sim, particles, floating_texts, shaker, renderer, zoom):
    ev_type, p_idx = sim.last_event
    p = sim.players[p_idx] if p_idx >= 0 else None
    px, py = (CENTER[0] + p.pos_x * zoom, CENTER[1] + p.pos_y * zoom) if p else CENTER
    
    if ev_type == "bounce_gain":
        for _ in range(5): particles.append(Particle(px, py, NEON_GREEN))
    elif ev_type == "bounce_loss":
        shaker.trigger(6); renderer.impact_flash = 0.3
        for _ in range(8): particles.append(Particle(px, py, NEON_RED))
    elif ev_type == "levelup":
        shaker.trigger(12); renderer.impact_flash = 0.4
        floating_texts.append(FloatingText(px, py - 40, "LEVEL UP!", p.color, renderer.font_hud))
        for _ in range(12): particles.append(Particle(px, py, p.color))
    elif ev_type == "item_collect":
        shaker.trigger(18); renderer.impact_flash = 0.6
        floating_texts.append(FloatingText(px, py - 60, f"MOD: {sim.current_chaos}", WHITE, renderer.font_team_name))
        for _ in range(20): particles.append(Particle(px, py, WHITE))
    elif ev_type == "pvp_collision":
        shaker.trigger(10)
        floating_texts.append(FloatingText(px, py, "OOF!", WHITE, renderer.font_hud))
    elif ev_type == "win":
        # Este é o evento de chegar no centro
        floating_texts.append(FloatingText(px, py - 80, "FINISHED!", p.color, renderer.font_team_name))
        renderer.impact_flash = 0.8

if __name__ == "__main__":
    main()
