"""
Asset management for Marble War.
Handles loading and caching of images and sounds.
"""

import random
import subprocess
from pathlib import Path
from typing import Dict, Optional

import pygame

import config


# ============================================================================
# ASSET MANAGER
# ============================================================================

class AssetManager:
    """Centralized asset loading to eliminate duplication."""
    
    def __init__(self) -> None:
        self.powerup_images: Dict[str, pygame.Surface] = {}
        self.projectile_img: Optional[pygame.Surface] = None
        self.explosion_img: Optional[pygame.Surface] = None
        self.bomb_img: Optional[pygame.Surface] = None
        self.face_assets: Dict[str, pygame.Surface] = {}
        self.weapon_img: Optional[pygame.Surface] = None
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
    
    def load_all(self) -> None:
        """Load all game assets."""
        self._load_powerup_images()
        self._load_combat_assets()
        self._load_face_assets()
        self._load_sounds()
        self._setup_background_music()
    
    def _load_powerup_images(self) -> None:
        """Load power-up icons."""
        mapping = {
            "speed": "assets/velocidade.png",
            "size": "assets/tamanho.png",
            "clone": "assets/duplicar.png",
            "assassin": "assets/arma.png"
        }
        size = config.POWERUP_RADIUS * 2
        
        for ptype, path in mapping.items():
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, (size, size))
                self.powerup_images[ptype] = img
            except Exception as e:
                print(f"Warning: Could not load {path}: {e}")
    
    def _load_combat_assets(self) -> None:
        """Load combat-related images."""
        try:
            self.projectile_img = self._load_and_scale(
                "assets/projetil.png", 
                config.PROJECTILE_RADIUS * 4
            )
            self.explosion_img = self._load_and_scale(
                "assets/explosao.png", 
                config.MARBLE_RADIUS * 3
            )
            self.bomb_img = self._load_and_scale(
                "assets/bomba.png", 
                config.MARBLE_RADIUS * 2
            )
            # Dedicated weapon asset for rotation/scaling
            self.weapon_img = pygame.image.load("assets/arma.png").convert_alpha()
            # We'll scale it dynamically in the draw call for quality, 
            # or pre-scale it here. Let's pre-scale to a standard size.
            self.weapon_img = pygame.transform.smoothscale(
                self.weapon_img, (config.MARBLE_RADIUS*2, config.MARBLE_RADIUS*2)
            )
        except Exception as e:
            print(f"Warning: Could not load combat assets: {e}")
    
    def _load_face_assets(self) -> None:
        """Load multiple marble face images."""
        face_dir = Path("assets/caras")
        if not face_dir.exists():
            print("Warning: assets/caras directory not found.")
            return

        size = int(config.MARBLE_RADIUS * 1.5)
        for path in face_dir.glob("*.png"):
            try:
                name = path.stem
                self.face_assets[name] = self._load_and_scale(str(path), size)
            except Exception as e:
                print(f"Warning: Could not load face asset {path}: {e}")

    @staticmethod
    def _load_and_scale(path: str, size: int) -> pygame.Surface:
        """Helper to load and scale image."""
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, (size, size))
    
    def _load_sounds(self) -> None:
        """Load sound effects."""
        sound_map = {
            "collision": "assets/music/collision.wav",
            "powerup": "efeitos_sonoros/poder.mp3",
            "elimination": "assets/music/elimination.wav",
            "tictoc": "assets/music/tictoc.wav",
        }
        
        for name, path in sound_map.items():
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
            except Exception as e:
                print(f"Warning: Could not load sound {path}: {e}")
    
    def _setup_background_music(self) -> None:
        """Select and trim background music."""
        music_dir = Path("trilha_sonora")
        if not music_dir.exists():
            return
        
        mp3_files = list(music_dir.glob("*.mp3"))
        if not mp3_files:
            return
        
        chosen = random.choice(mp3_files)
        output_path = Path("assets/music/current_bg_trimmed.mp3")
        
        print(f"Selected soundtrack: {chosen.name}")
        
        # Trim silence using ffmpeg
        cmd = [
            "ffmpeg", "-y", "-i", str(chosen),
            "-af", "silenceremove=start_periods=1:start_threshold=-50dB",
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL, check=True)
            pygame.mixer.music.load(str(output_path))
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(loops=-1)
        except Exception as e:
            print(f"Warning: Could not process soundtrack: {e}")
            # Fallback to original
            try:
                pygame.mixer.music.load(str(chosen))
                pygame.mixer.music.set_volume(0.1)
                pygame.mixer.music.play(loops=-1)
            except:
                pass
