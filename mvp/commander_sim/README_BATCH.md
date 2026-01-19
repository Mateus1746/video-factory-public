# Gerador de Simulações em Lote (Batch Generator)

Este script automatiza a criação de vídeos de simulação prontos para o YouTube (1080p, 60fps, com áudio).

## Como Usar

Certifique-se de estar no diretório raiz do projeto e ter o `uv` instalado.

```bash
uv run batch_generator.py
```

## O que ele faz?

1.  **Seleção Inteligente de Mapas**: Escolhe mapas aleatoriamente, mas dá prioridade aos que foram menos utilizados, garantindo variedade. Evita repetir o mesmo mapa duas vezes seguidas.
2.  **Renderização**: Gera frames em alta qualidade (1080p) usando o `render_frames.js`.
3.  **Compilação**: Une os frames em um vídeo MP4 a 60fps usando `ffmpeg`.
4.  **Áudio**: Adiciona efeitos sonoros (SFX) e música de fundo sincronizados com os eventos da batalha usando `mix_sfx.py`.
5.  **Organização**: Salva o resultado final na pasta `batch_output` com nome carimbado pelo horário (ex: `sim_20231027_120000_map1.mp4`) e limpa os arquivos temporários.

## Configuração

Você pode ajustar as configurações editando o início do arquivo `batch_generator.py`:

-   `BATCH_OUTPUT_DIR`: Pasta de saída.
-   `HISTORY_FILE`: Arquivo que guarda o histórico de uso dos mapas.

## Requisitos

-   Python 3 (gerenciado pelo `uv`)
-   Node.js (para o Puppeteer)
-   FFmpeg instalado e acessível no terminal.
