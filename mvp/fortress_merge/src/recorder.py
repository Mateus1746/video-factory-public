import pygame
import os
import threading
import queue
import time
from .config import OUTPUT_DIR, DEBUG

class VideoRecorder:
    def __init__(self, output_dir=OUTPUT_DIR):
        self.output_dir = output_dir
        self.frame_queue = queue.Queue()
        self.is_recording = False
        self.thread = None
        self.frame_count = 0
        
        # Garante que o diretório existe
        os.makedirs(self.output_dir, exist_ok=True)

    def start(self):
        """Inicia a thread de gravação."""
        self.is_recording = True
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()
        if DEBUG:
            print("🎥 [REC] Recorder started (Background Thread)")

    def stop(self):
        """Para a gravação e aguarda o processamento dos frames restantes."""
        self.is_recording = False
        if self.thread:
            if DEBUG:
                print(f"🎥 [REC] Stopping... Remaining frames: {self.frame_queue.qsize()}")
            self.thread.join()
            if DEBUG:
                print("🎥 [REC] Recording finished.")

    def capture(self, surface):
        """Captura um frame (cópia rápida em memória) e coloca na fila."""
        # .copy() é crucial! Se não fizermos cópia, o Pygame altera a surface 
        # enquanto tentamos salvar, gerando glitches ou erros.
        frame_copy = surface.copy()
        self.frame_queue.put((self.frame_count, frame_copy))
        self.frame_count += 1

    def _worker(self):
        """Loop da thread que salva os arquivos no disco."""
        while True:
            try:
                # Espera por um frame. Se a gravação parou e a fila está vazia, sai.
                idx, surface = self.frame_queue.get(timeout=1)
            except queue.Empty:
                if not self.is_recording:
                    break
                continue

            filename = os.path.join(self.output_dir, f"frame_{idx:04d}.png")
            pygame.image.save(surface, filename)
            self.frame_queue.task_done()
