import pygame
import numpy as np
import os
from .config import WIDTH

class AssetManager:
    def __init__(self, headless=False):
        self.headless = headless
        self.sounds = {}
        self.fonts = {}
        
        # Audio Settings
        self.sample_rate = 44100
        self.bits = 16
        
        # Initialize Mixer properly if not already
        if not pygame.mixer.get_init() and not headless:
            try:
                pygame.mixer.init(frequency=self.sample_rate, size=-self.bits, channels=2)
            except:
                pass

        self._load_assets()

    def _generate_sound(self, duration, freq_start, freq_end=None, type='sine', volume=0.5):
        """Gera um objeto pygame.mixer.Sound proceduralmente."""
        if self.headless: return None
        
        n_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n_samples, False)
        
        # Frequency Sweep Logic
        if freq_end:
            freq = freq_start * (freq_end / freq_start)**(t / duration)
        else:
            freq = freq_start
            
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        
        if type == 'sine':
            wave = np.sin(phase)
        elif type == 'square':
            wave = np.sign(np.sin(phase))
        elif type == 'noise':
            wave = np.random.uniform(-1, 1, n_samples)
        
        # Envelope (Fade Out)
        envelope = np.exp(-5 * t / duration)
        wave *= envelope * volume
        
        # Stereo & 16-bit conversion
        # Pygame expects signed 16-bit integers for mixer
        audio_data = (wave * 32767).astype(np.int16)
        stereo_data = np.column_stack((audio_data, audio_data)) # Make stereo
        
        return pygame.sndarray.make_sound(stereo_data)

    def _load_assets(self):
        # Fontes (Mantidas)
        self.fonts["ui"] = pygame.font.SysFont("Verdana", int(WIDTH * 0.030), bold=True)
        self.fonts["dmg"] = pygame.font.SysFont("Impact", int(WIDTH * 0.05))
        self.fonts["title"] = pygame.font.SysFont("Impact", int(WIDTH * 0.1), bold=True)

        # Sons Procedurais (Sem arquivos!)
        if not self.headless:
            try:
                # Shoot: Laser pew
                self.sounds["shoot"] = self._generate_sound(0.1, 800, 200, volume=0.15)
                
                # Hit: Short noise
                self.sounds["hit"] = self._generate_sound(0.05, 200, 50, type='noise', volume=0.2)
                
                # Explosion: Deep rumble noise
                self.sounds["explosion"] = self._generate_sound(0.4, 100, 20, type='noise', volume=0.4)
                
                # Merge: Magical chime up
                self.sounds["merge"] = self._generate_sound(0.3, 400, 1200, volume=0.4)
                
                # Buy: Cash register ping
                self.sounds["buy"] = self._generate_sound(0.1, 1500, 1500, volume=0.3)
                
                # Game Over: Downward slide
                self.sounds["gameover"] = self._generate_sound(1.0, 300, 50, volume=0.5)
                
                # Victory: Major chord arpeggio (Simplified to just a high ping for now)
                self.sounds["victory"] = self._generate_sound(0.8, 400, 800, volume=0.5)
                
            except Exception as e:
                print(f"⚠️ Erro ao gerar áudio procedural: {e}")

    def play_sfx(self, name):
        if not self.headless and name in self.sounds and self.sounds[name]:
            try:
                self.sounds[name].play()
            except:
                pass # Ignora erros de playback em headless simulado

    def get_font(self, name):
        return self.fonts.get(name, pygame.font.SysFont("Arial", 20))