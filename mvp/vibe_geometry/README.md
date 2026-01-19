# Vibe Geometry: Unified Visualization Hub 🎵✨

Um orquestrador de visualizações de áudio de alta performance, fundindo física, matemática e música.

## 🚀 Módulos Disponíveis (Styles)

### 1. `ball` (Bouncing Ball V2 - "Social Juice")
*   **Engine:** Pygame (Real-time)
*   **Estilo:** Synthwave, Físico, Interativo.
*   **Foco:** Retenção visual para Shorts/TikTok.
*   **Features:** Squash & Stretch, Camera Shake, Dynamic Grid.

### 2. `flow` (Harmonic Flow)
*   **Engine:** Matplotlib (Offline Rendering)
*   **Estilo:** Abstrato, Matemático, 3D.
*   **Foco:** Arte generativa, relaxamento, beleza matemática.
*   **Features:** Swarm Intelligence, Flower of Life, Galaxy Spirals.

### 3. `vortex` (Dynamic Vortex)
*   **Engine:** Matplotlib (Offline Rendering)
*   **Estilo:** Cyberpunk, Agressivo, Caótico.
*   **Foco:** Drops pesados, Dubstep, Phonk.
*   **Features:** Tornado Formation, Implosion/Explosion Physics, Reactive Camera Zoom.

## 🛠️ Como Usar

### Pipeline Automático
O `pipeline.py` gerencia o download, corte e renderização para qualquer estilo.

#### Estilo "Bouncing Ball" (Padrão)
```bash
uv run pipeline.py "URL_DO_YOUTUBE" --style ball --mode sim
```

#### Estilo "Harmonic Flow" ou "Vortex"
```bash
uv run pipeline.py "URL_DO_YOUTUBE" --style flow --mode render
uv run pipeline.py "URL_DO_YOUTUBE" --style vortex --mode render
```

> **Nota:** O estilo `flow` é pesado para renderizar em tempo real, por isso recomenda-se usar `--mode render`.

### Renderização Direta
Se já tiver o áudio baixado:

```bash
# Para Ball
uv run src/render_video_v2.py downloads/audio.mp3 downloads/audio.json

# Para Flow
uv run src/engines/matplotlib/harmonic_flow.py downloads/audio.mp3 -o output_flow.mp4
```

## 📂 Estrutura do Projeto
```
/src
  /engines
    /pygame
      bouncing_ball.py  # V2 engine
    /matplotlib
      harmonic_flow.py  # Swarm/Particles 3D
      vortex.py         # (Coming soon)
      mandelbrot.py     # (Coming soon)
  analyzer.py           # Análise de áudio compartilhada
  render_video_v2.py    # Renderizador para engines Pygame
pipeline.py             # CLI Orchestrator
```