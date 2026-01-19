import pygame
import random
import os
from src.config import SCREEN_W, SCREEN_H
from src.render_engine import RenderEngine

def main():
    # Resolution for portrait display
    width, height = SCREEN_W, SCREEN_H
    
    # Scale down for monitor viewing (since 1920 is taller than most monitors)
    display_scale = 0.5
    win_w, win_h = int(width * display_scale), int(height * display_scale)
    
    pygame.init()
    # Center window on screen
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    
    screen = pygame.display.set_mode((win_w, win_h))
    pygame.display.set_caption("Neon Survivor - Portrait")
    clock = pygame.time.Clock()
    
    engine = RenderEngine(width, height)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                if event.key == pygame.K_r: engine.reset()

        # Step Simulation
        engine.step(dt)
        
        # Render Frame
        frame_array = engine.render()
        
        # Convert numpy array to surface
        frame_surf = pygame.surfarray.make_surface(frame_array.transpose([1, 0, 2]))
        
        # Scale and Draw
        scaled_surf = pygame.transform.smoothscale(frame_surf, (win_w, win_h))
        screen.blit(scaled_surf, (0, 0))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()