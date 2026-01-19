import pygame
from .config import WIDTH, HEIGHT, COLORS

class Grid:
    def __init__(self, rows=5, cols=5):
        self.rows = rows
        self.cols = cols
        
        # Dimensões e Layout (Centralizado)
        self.cell_size = WIDTH * 0.14
        self.gap = WIDTH * 0.02
        
        self.width_pixels = (self.cols * (self.cell_size + self.gap)) - self.gap
        self.height_pixels = (self.rows * (self.cell_size + self.gap)) - self.gap
        
        self.start_x = (WIDTH - self.width_pixels) // 2
        self.start_y = HEIGHT // 2 + (HEIGHT * 0.15)

    def get_pos(self, row, col):
        """Retorna o centro (x, y) da célula especificada."""
        x = self.start_x + col * (self.cell_size + self.gap) + self.cell_size // 2
        y = self.start_y + row * (self.cell_size + self.gap) + self.cell_size // 2
        return x, y

    def draw(self, surface, offset):
        """Desenha o grid na tela com suporte a offset de câmera."""
        ox, oy = offset
        for r in range(self.rows):
            for c in range(self.cols):
                cx, cy = self.get_pos(r, c)
                # Converter centro para topo-esquerda para desenhar rect
                rect_x = cx - self.cell_size // 2 + ox
                rect_y = cy - self.cell_size // 2 + oy
                
                pygame.draw.rect(
                    surface, 
                    COLORS["GRID"], 
                    (rect_x, rect_y, self.cell_size, self.cell_size), 
                    border_radius=8
                )
