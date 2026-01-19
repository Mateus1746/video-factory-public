## Arquitetura (Consolidada Web-Stack)
- **Engine (JavaScript/Canvas)**:
    - `index.html` (Base) + `style.css` (Design System Neon).
    - `js/`: Lógica modular (Renderer, AI, Entities, Config).
- **Dados & Conteúdo**:
    - `maps/`: Arquivos `.json` com dados de nível.
    - `html_maps/`: Pastas para arquivos `.html` customizados (templates de mapas únicos).
- **Pipeline de Vídeo (Node.js/Puppeteer)**:
    - `render_frames.js`: Processamento determinístico em lote de mapas JSON e HTML.
    - `render_preview.py` / `render_final_video.py`: Utilitários FFmpeg para compilação de vídeo.

## Como Usar
1. **Preview**: Abra `index.html` em qualquer navegador. Teste mapas com `?map=level1.json`.
2. **Gerar Frames**: `node render_frames.js [mapa.html|json]` (ou sem argumentos para todos).
3. **Gerar Vídeo**:
    - Preview: `python3 render_preview.py [map_name]` (ex: `duel`)
    - Final: `python3 render_final_video.py [map_name]` (ex: `duel`)

## Histórico de Refatoração
- **Migração Completa**: Código original Python (`src/`, `main.py`) removido após portabilidade total para Web-Stack.
- **Injeção de Dados**: Suporte nativo para carregamento de mapas JSON via URL Params (`?map=...`).
- **Capture Loop**: O Puppeteer agora dita o ritmo da simulação, garantindo 60fps constantes independente da carga de renderização.
