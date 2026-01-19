# Workflow de Geração de Vídeo (Night Mode Edition 🌙)

Este documento descreve os comandos necessários para baixar, cortar, analisar e renderizar o vídeo da bolinha sincronizada com a música.

## 1. Pipeline Completo (Recomendado)

O script `pipeline.py` automatiza todo o processo (download, corte, análise e renderização).

```bash
# Para renderizar o vídeo final diretamente (com dica de BPM para evitar erro de oitava)
uv run pipeline.py "URL_DO_YOUTUBE" --mode render --start 00:00:30 --duration 60 --bpm 75

# Para rodar a simulação interativa antes de renderizar
uv run pipeline.py "URL_DO_YOUTUBE" --mode sim --start 00:00:30 --duration 60 --bpm 75
```

**Parâmetros:**
- `--mode`: `sim` para simulação interativa ou `render` para gerar o arquivo `.mp4`.
- `--start`: Tempo de início do corte (ex: `30` ou `00:00:30`).
- `--duration`: Duração do clipe em segundos.
- `--subdiv`: Subdivisões das batidas (padrão: `1`).
- `--bpm`: **Dica de BPM** (Opcional). Ajuda o algoritmo a focar na oitava correta (ex: disparar entre 70-80 ao invés de 140-160).

---

## 2. Comandos Manuais e Auditoria

### Auditoria de Sincronia (Click Track)
Se você estiver em dúvida se as batidas foram bem detectadas, gere um arquivo de áudio com "cliques":
```bash
uv run src/beat_timer.py "downloads/audio.mp3" --bpm 75 --clicks "downloads/audio_debug.mp3"
```

### Análise Manual
```bash
uv run src/analyze_music.py "downloads/audio.mp3" -o "downloads/audio.json" --bpm 75
```

### Rodar Simulação Interativa
```bash
uv run src/main.py --audio "downloads/audio.mp3" --json "downloads/audio.json"
```

### Renderização Direta (Vertical 9:16)
Para gerar o vídeo vertical em alta resolução usando arquivos locais:
```bash
uv run src/render_video.py src/corte.mp3 src/corte.json --subdiv 1 -o rendered_video_friends.mp4
```

> [!IMPORTANT]
> Se o arquivo JSON foi gerado apenas pelo `beat_timer.py`, o visualizador usará cores baseadas no **Tom (Key)** da música. Para obter cores dinâmicas baseadas em frequências, use o comando de **Análise Manual** (`src/analyze_music.py`) antes de renderizar.

---

## Estética e UI
A simulação agora conta com um **Night Mode (Premium Dark)** por padrão, utilizando sombras neumórficas sutis para uma experiência visual mais sofisticada.

## Requisitos
- FFmpeg instalado no sistema.
- Dependências instaladas via `uv sync`.
