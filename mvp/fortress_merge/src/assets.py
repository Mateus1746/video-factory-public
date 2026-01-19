import pygame
import os
from .config import WIDTH

class AssetManager:
    def __init__(self, headless=False):
        self.headless = headless
        self.sounds = {}
        self.fonts = {}
        self._load_assets()

    def _load_assets(self):
        # Fontes
        self.fonts["ui"] = pygame.font.SysFont("Verdana", int(WIDTH * 0.030), bold=True)
        self.fonts["dmg"] = pygame.font.SysFont("Impact", int(WIDTH * 0.05))
        self.fonts["title"] = pygame.font.SysFont("Impact", int(WIDTH * 0.1), bold=True)

        # Sons
        if not self.headless:
            sfx_dir = "assets/sfx"
            sound_files = ["shoot", "hit", "explosion", "merge", "buy", "gameover", "victory"]
            for name in sound_files:
                path = os.path.join(sfx_dir, f"{name}.wav")
                try:
                    if os.path.exists(path):
                        snd = pygame.mixer.Sound(path)
                        vol = 0.1 if name == "shoot" else 0.3
                        snd.set_volume(vol)
                        self.sounds[name] = snd
                except Exception as e:
                    print(f"Erro ao carregar som {name}: {e}")

    def play_sfx(self, name):
        if not self.headless and name in self.sounds:
            self.sounds[name].play()

    def get_font(self, name):
        return self.fonts.get(name, pygame.font.SysFont("Arial", 20))
