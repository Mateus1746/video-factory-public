# 🏭 Nexus Factory: Documentação Operacional & Histórico de Correções

**Data:** 19 de Janeiro de 2026
**Status:** ✅ Operacional (Pipeline Automatizado)

---

## 1. 🔄 Workflow Padrão (O Fluxo da Fábrica)

O sistema opera em um modelo híbrido **Cloud (Geração)** + **Local (Distribuição)** para contornar limitações de hardware local e bloqueios de API.

### Passo 1: O Gatilho (Trigger) 🔫
Para iniciar a produção em massa de vídeos (todos os projetos simultaneamente):
1. Edite o arquivo `trigger_all.txt` (basta mudar o timestamp ou texto).
2. Faça o `git push`.
3. O GitHub Actions detecta a mudança e inicia o workflow `Run All Projects NOW`.

### Passo 2: A Fábrica (GitHub Actions) ☁️
*Ocorre nos servidores do GitHub (Ubuntu/Headless)*
1. **Checkout:** O código é baixado.
2. **Setup:** Python e Node.js são configurados.
3. **Instalação:** Dependências (`ffmpeg`, `requirements.txt`, `package.json`) são instaladas.
4. **Renderização:** O script `generate_video.py` roda e cria o arquivo `.mp4`.
5. **Envio para o Depósito:** O script `upload_to_drive.py` envia o vídeo gerado para uma pasta específica no seu **Google Drive**.

### Passo 3: A Ponte (Bridge Upload) 🌉
*Ocorre na sua máquina local (Background Service)*
1. O script `scripts/bridge_upload.py` roda em loop infinito (verifica a cada 60s).
2. **Monitoramento:** Ele olha a pasta do Google Drive.
3. **Detecção:** Ao encontrar um vídeo, ele identifica o projeto pelo nome do arquivo.
4. **Upload:**
   - Baixa o vídeo para uma pasta temporária.
   - Consulta `brain/video_metadata.json` para obter Título, Descrição e Tags.
   - Faz o upload para o canal do YouTube correspondente usando os tokens salvos em `brain/`.
5. **Limpeza:** Após o upload com sucesso, **apaga** o vídeo do Google Drive para evitar duplicidade.

---

## 2. 🛠️ Histórico de Erros & Soluções (Troubleshooting)

Durante a configuração, enfrentamos e resolvemos os seguintes problemas críticos:

| Projeto / Componente | Erro / Sintoma | Causa Raiz | Solução Aplicada |
|----------------------|----------------|------------|------------------|
| **commander_sim** | `npm error ENOENT ... package.json` | O `.gitignore` continha a regra `*.json`, impedindo o upload do `package.json`. | `.gitignore` ajustado para permitir configs e forçado o `git add` dos arquivos JSON. |
| **tower_defense** | `Multiple top-level packages discovered` | `pyproject.toml` mal configurado tentava empacotar a pasta de saída. | Configuração explícita no `setuptools` para incluir apenas pastas de código (`sim`, `vis`) e excluir `output`. |
| **GitHub Actions** | `cd: ... No such file or directory` | Existiam pastas duplicadas (`mvp` antigo vs `youtube_factory`) confundindo o script. | Removida a pasta legado `orquestrador/youtube/mvp` e reescrito o workflow para usar `find` dinâmico. |
| **Git Push** | `Push rejected (secrets/large file)` | Arquivos `.pickle` (tokens) e vídeos >100MB no commit. | Removidos segredos do histórico (`git rm --cached`), adicionados ao `.gitignore` e removido arquivo grande. |
| **Bridge Upload** | Vídeo `tower_defense` ignorado | ID do projeto não existia em `accounts.json`. | Adicionado `tower_defense` ao `accounts.json` (mapeado para credenciais `fortress_merge`). |
| **YouTube** | Títulos com números aleatórios | O script adicionava um timestamp `#176...` no título. | Código alterado para usar apenas o Título Base definido no metadados. |

---

## 3. 📖 Guia de Manutenção

### Como iniciar o Bridge (Local)
Se você reiniciar o computador, precisa rodar o Bridge novamente para que os vídeos saiam do Drive e vão para o YouTube:

```bash
# Rodar em background (modo silencioso)
nohup uv run python3 scripts/bridge_upload.py > bridge.log 2>&1 &

# Para verificar se está rodando:
ps aux | grep bridge_upload.py

# Para ver o que ele está fazendo:
tail -f bridge.log
```

### Como adicionar um NOVO projeto
1. Crie a pasta em `mvp/novo_projeto`.
2. Garanta que ele tenha um `generate_video.py` que gera um `output_render.mp4`.
3. Adicione o nome do projeto na matriz do arquivo `.github/workflows/run_all_now.yml`.
4. Adicione as credenciais e metadados em `brain/accounts.json` e `brain/video_metadata.json`.

---
*Gerado automaticamente pelo Nexus Agent.*
