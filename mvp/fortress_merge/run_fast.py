import os
import sys

# Configura ambiente para modo rápido (Metade da resolução)
os.environ["WIDTH"] = "540"
os.environ["HEIGHT"] = "960"
os.environ["FPS"] = "60"
os.environ["HEADLESS"] = "false" # Garante que vai mostrar na tela

print("🚀 Iniciando Fortress Merge em Modo Rápido (540x960 @ 60FPS)...")

# Importa e roda o jogo
from src.game import Game

if __name__ == "__main__":
    game = Game()
    game.run()
