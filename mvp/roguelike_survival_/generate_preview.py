import os
import pygame
import numpy as np
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from src.render_engine import RenderEngine
from src.config import SCREEN_W, SCREEN_H

# CONFIG
FPS = 30
MAX_DURATION = 45 # Safety timeout
OUTPUT_FILE = "preview_render.mp4"
SCALE = 0.5    # 540x960

TARGET_W = int(SCREEN_W * SCALE)
TARGET_H = int(SCREEN_H * SCALE)
if TARGET_W % 2 != 0: TARGET_W += 1
if TARGET_H % 2 != 0: TARGET_H += 1

print(f"Initializing Preview Render ({TARGET_W}x{TARGET_H} @ {FPS}fps)...")
print(f"Simulating until VICTORY or DEFEAT (Max {MAX_DURATION}s)...")

engine = RenderEngine(TARGET_W, TARGET_H)

frames = []
t = 0.0
dt = 1.0 / FPS
max_frames = MAX_DURATION * FPS

# Simulation Loop
while t < MAX_DURATION:
    engine.step(dt)
    
    # Capture Frame
    frames.append(engine.render())
    
    # Check Stop Condition
    if engine.victory or engine.game_over:
        print(f"Game Finished at {t:.2f}s! (Victory: {engine.victory})")
        # Add a few seconds of freeze frame
        last_frame = frames[-1]
        for _ in range(FPS * 2): # 2 seconds pause
            frames.append(last_frame)
        break
    
    t += dt
    if len(frames) % 30 == 0:
        print(f"Rendered {t:.1f}s...", end='\r')

print(f"\nSimulation Complete. Total Frames: {len(frames)}")
print("Encoding Video...")

clip = ImageSequenceClip(frames, fps=FPS)
clip.write_videofile(OUTPUT_FILE, fps=FPS, codec="libx264", preset="ultrafast")

print(f"Done! Saved to {OUTPUT_FILE}")
