import os
import sys
import subprocess
import pygame

# 1. Configuração de Alta Performance
WIDTH = 1080
HEIGHT = 1920
FPS = 60
DURATION = 60 # Segundos de simulação

# Define variáveis de ambiente ANTES de importar o jogo
os.environ["WIDTH"] = str(WIDTH)
os.environ["HEIGHT"] = str(HEIGHT)
os.environ["FPS"] = str(FPS)
os.environ["HEADLESS"] = "true" # O jogo não vai abrir janela
os.environ["SDL_VIDEODRIVER"] = "dummy" # Renderização via software sem monitor

print(f"🚀 Iniciando Pipeline de Renderização: {WIDTH}x{HEIGHT} @ {FPS}fps")

# 2. Importa o Jogo
try:
    from src.game import Game
except ImportError:
    # Caso esteja rodando da raiz
    sys.path.append(os.getcwd())
    from src.game import Game

# 3. Gravador Otimizado (Pipe direto para FFMPEG)
class FFMPEGRecorder:
    def __init__(self, output_file="output_render.mp4"):
        command = [
            'ffmpeg',
            '-y', # Sobrescrever
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-s', f'{WIDTH}x{HEIGHT}', # Tamanho
            '-pix_fmt', 'rgb24',
            '-r', str(FPS),
            '-i', '-', # Input do Pipe
            '-c:v', 'libx264',
            '-preset', 'medium', # Equilíbrio entre velocidade e compressão
            '-crf', '20', # Alta qualidade visual (18-22 é o ideal)
            '-pix_fmt', 'yuv420p',
            output_file
        ]
        
        print(f"🎥 Iniciando FFMPEG: {' '.join(command)}")
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE)
        self.frame_count = 0
        self.total_frames = FPS * DURATION

    def start(self):
        pass # Processo já iniciou no init

    def capture(self, surface):
        # Extrai os bytes crus da surface (Muito rápido)
        # O Pygame guarda internamente como buffer, tobytes é otimizado
        data = pygame.image.tobytes(surface, 'RGB')
        try:
            self.process.stdin.write(data)
            self.frame_count += 1
            
            # Feedback de progresso
            if self.frame_count % 60 == 0:
                sys.stdout.write(f"\r⏳ Renderizando: {self.frame_count}/{self.total_frames} frames ({(self.frame_count/self.total_frames)*100:.1f}%)")
                sys.stdout.flush()
                
        except BrokenPipeError:
            print("\n❌ Erro: FFMPEG fechou o pipe inesperadamente.")

    def stop(self):
        print("\n✅ Finalizando codificação...")
        if self.process.stdin:
            self.process.stdin.close()
        self.process.wait()

# 4. Execução
if __name__ == "__main__":
    output_filename = sys.argv[1] if len(sys.argv) > 1 else "output_render.mp4"
    game = Game()
    
    # Injeção de Dependência: Troca o gravador padrão pelo nosso FFMPEGRecorder
    if hasattr(game.recorder, 'stop'):
        game.recorder.stop()
        
    game.recorder = FFMPEGRecorder(output_filename)
    
    # Sobrescreve a lógica de loop para garantir limite de tempo
    # Em vez de chamar game.run(), vamos fazer o loop manual para ter controle total
    print("⚡ Iniciando Simulação...")
    
    try:
        while game.running and game.recorder.frame_count < FPS * DURATION:
            game.clock.tick() # Não limitamos o FPS da simulação aqui, queremos que rode o mais rápido possível
            game.update()
            game.draw()
            
            # Checagem de segurança (Game Over/Victory)
            # Se quiser gravar até o fim do tempo mesmo após vitória, comente abaixo
            if not game.running:
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário.")
    finally:
        game.recorder.stop()
        pygame.quit()
