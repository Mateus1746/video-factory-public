import pygame
import os
import random
from src.config import VOL_MUSIC, VOL_SFX, PATH_MUSIC, SFX_MAP

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        for name, path in SFX_MAP.items():
            if os.path.exists(path):
                s = pygame.mixer.Sound(path)
                s.set_volume(VOL_SFX)
                self.sounds[name] = s

    def play_music(self):
        music = random.choice(PATH_MUSIC)
        if os.path.exists(music):
            pygame.mixer.music.load(music)
            pygame.mixer.music.set_volume(VOL_MUSIC)
            pygame.mixer.music.play(-1)

    def play_sfx(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def stop_music(self):
        pygame.mixer.music.stop()