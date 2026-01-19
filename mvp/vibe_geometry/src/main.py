import pygame
import math
import json
import argparse
import sys

# --- CONFIGURAÇÃO VISUAL ---
WIDTH, HEIGHT = 800, 800
FPS = 60
CENTER_X = WIDTH // 2
GROUND_Y = HEIGHT * 0.70  # Linha do chão (70% da tela)

# Cores
BG_COLOR = (15, 15, 20)
GROUND_COLOR = (50, 50, 60)
REFLECTION_ALPHA = 80  # Transparência do reflexo

class Player:
    def __init__(self, json_path, audio_path):
        # Carregar dados
        try:
            with open(json_path, 'r') as f:
                self.data = json.load(f)
            self.beats = self.data['beats']
            self.duration = self.data['metadata']['duration']
        except Exception as e:
            print(f"Erro ao carregar JSON: {e}")
            print("Gere o arquivo .json primeiro com: python src/analyzer.py data/<audio.mp3>")
            sys.exit(1)

        # Estado da Bola
        self.ball_pos = pygame.Vector2(CENTER_X, GROUND_Y - 50)
        self.ball_radius = 25
        self.ball_color = (255, 0, 100)  # Rosa Neon inicial
        self.trail = []
        
        # Efeitos
        self.pulse = 0.0
        self.last_beat_idx = -1
        
        # Audio
        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        self.start_ticks = pygame.time.get_ticks()

    def get_current_time(self):
        return (pygame.time.get_ticks() - self.start_ticks) / 1000.0

    def update(self):
        t = self.get_current_time()
        
        # 1. Encontrar a batida anterior e a próxima
        next_beat_idx = 0
        for i, beat in enumerate(self.beats):
            if beat['timestamp'] > t:
                next_beat_idx = i
                break
        else:
            # Fim da música
            next_beat_idx = len(self.beats)
        
        # Se ainda não começou ou acabou
        if next_beat_idx == 0 or next_beat_idx >= len(self.beats):
            # Manter bola no centro-baixo
            self.ball_pos.y = GROUND_Y - self.ball_radius - 10
            self.pulse *= 0.9
            return

        prev_beat = self.beats[next_beat_idx - 1]
        next_beat = self.beats[next_beat_idx]
        
        start_time = prev_beat['timestamp']
        end_time = next_beat['timestamp']
        
        # 2. Calcular Progresso (0.0 a 1.0)
        total_interval = end_time - start_time
        time_passed = t - start_time
        
        if total_interval <= 0:
            progress = 1.0
        else:
            progress = time_passed / total_interval
        
        progress = max(0.0, min(1.0, progress))
        
        # 3. Movimento Vertical (Pulo)
        # A bola sobe e desce em um arco parabólico entre batidas
        # No início (progress=0): bola está no chão (acabou de bater)
        # No meio (progress=0.5): bola está no topo do pulo
        # No fim (progress=1.0): bola volta ao chão para próxima batida
        
        # Parábola: y = 4 * h * p * (1 - p) onde h = altura máxima, p = progress
        max_jump_height = 200  # Pixels de altura máxima
        jump_arc = 4 * max_jump_height * progress * (1 - progress)
        
        self.ball_pos.y = GROUND_Y - self.ball_radius - jump_arc
        
        # Movimento Horizontal sutil (oscilação)
        # Usa o índice da batida para variar a posição X
        x_offset = math.sin(next_beat_idx * 1.5) * 100
        self.ball_pos.x = CENTER_X + x_offset
        
        # 4. Detectar Nova Batida -> Mudar Cor
        if next_beat_idx != self.last_beat_idx:
            self.last_beat_idx = next_beat_idx
            
            # Pegar cor do JSON (se disponível)
            color_hex = prev_beat.get('color_hex', '#FF0064').lstrip('#')
            try:
                self.ball_color = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
            except:
                self.ball_color = (255, 0, 100)
            
            self.pulse = 1.0  # Trigger visual pulse
        
        # 5. Efeito de Impacto (quando próximo do chão)
        if progress > 0.85:
            self.pulse = max(self.pulse, (progress - 0.85) * 6.6)  # 0 a 1
        else:
            self.pulse *= 0.9
            
        # 6. Rastro
        self.trail.insert(0, (pygame.Vector2(self.ball_pos), self.ball_color))
        if len(self.trail) > 15:
            self.trail.pop()

    def draw(self, screen):
        screen.fill(BG_COLOR)
        
        # --- 1. DESENHAR REFLEXO (Antes do chão) ---
        # O reflexo é a bolinha espelhada verticalmente abaixo do chão
        reflection_y = GROUND_Y + (GROUND_Y - self.ball_pos.y)
        
        # Rastro Refletido (mais suave)
        for i, (pos, color) in enumerate(self.trail):
            alpha = (REFLECTION_ALPHA - (i * 5))
            if alpha < 0:
                continue
            size = int(self.ball_radius * (1 - i / 20))
            ref_pos_y = GROUND_Y + (GROUND_Y - pos.y)
            
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color, alpha), (size, size), size)
            screen.blit(surf, (int(pos.x - size), int(ref_pos_y - size)))
        
        # Bola Refletida
        ref_surf = pygame.Surface((self.ball_radius * 2, self.ball_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(ref_surf, (*self.ball_color, REFLECTION_ALPHA), 
                           (self.ball_radius, self.ball_radius), self.ball_radius)
        screen.blit(ref_surf, (int(self.ball_pos.x - self.ball_radius), 
                               int(reflection_y - self.ball_radius)))
        
        # --- 2. DESENHAR CHÃO ---
        # Linha principal
        pygame.draw.line(screen, GROUND_COLOR, (0, int(GROUND_Y)), (WIDTH, int(GROUND_Y)), 2)
        
        # Gradiente de "desvanecimento" abaixo do chão
        for i in range(50):
            alpha = 30 - i
            if alpha < 0:
                break
            pygame.draw.line(screen, (*GROUND_COLOR[:3], alpha), 
                             (0, int(GROUND_Y) + i), (WIDTH, int(GROUND_Y) + i))
        
        # --- 3. DESENHAR RASTRO (Acima do chão) ---
        for i, (pos, color) in enumerate(self.trail):
            alpha = 200 - (i * 13)
            if alpha < 0:
                continue
            size = int(self.ball_radius * (1 - i / 20))
            
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color, alpha), (size, size), size)
            screen.blit(surf, (int(pos.x - size), int(pos.y - size)))

        # --- 4. DESENHAR BOLA PRINCIPAL ---
        # Glow externo (quando pulse ativo)
        if self.pulse > 0.1:
            glow_size = int(self.ball_radius * 2.5)
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.ball_color, int(50 * self.pulse)), 
                               (glow_size, glow_size), glow_size)
            screen.blit(glow_surf, (int(self.ball_pos.x - glow_size), 
                                    int(self.ball_pos.y - glow_size)), 
                        special_flags=pygame.BLEND_ADD)
        
        # Bola
        pygame.draw.circle(screen, self.ball_color, 
                           (int(self.ball_pos.x), int(self.ball_pos.y)), self.ball_radius)
        # Highlight
        highlight_offset = self.ball_radius // 3
        pygame.draw.circle(screen, (255, 255, 255), 
                           (int(self.ball_pos.x - highlight_offset), 
                            int(self.ball_pos.y - highlight_offset)), 
                           self.ball_radius // 3)

def main():
    parser = argparse.ArgumentParser(description="Bouncing Ball Visualizer (Deterministic)")
    parser.add_argument("audio", help="Arquivo MP3")
    parser.add_argument("json", help="Arquivo JSON (gerado pelo analyze_music.py)")
    args = parser.parse_args()

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bouncing Ball Visualizer")
    clock = pygame.time.Clock()
    
    player = Player(args.json, args.audio)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        player.update()
        player.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
