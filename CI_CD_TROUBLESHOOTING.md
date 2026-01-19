# 🛠️ Relatório de Solução de Problemas: Pipeline CI/CD (GitHub Actions)

Este documento registra os desafios técnicos enfrentados durante a implementação da "Fábrica de Vídeos" automatizada no GitHub Actions e as soluções definitivas aplicadas.

**Data:** 18 de Janeiro de 2026
**Status:** ✅ Pipeline Operacional (7 Projetos Estáveis)

---

## 1. 📦 Erros de Build e Dependências

### Problema A: `Multiple top-level packages discovered`
**Sintoma:** O comando `pip install .` falhava com erro de "flat-layout", pois o `setuptools` confundia pastas de recursos (`assets`, `frames`, `js`) com pacotes Python.
**Projetos Afetados:** `marble war`, `commander_sim`, `tower_defense`.
**Solução:**
Configuração explícita no `pyproject.toml` para ignorar pastas não-código.
```toml
[tool.setuptools.packages.find]
where = ["."]
exclude = ["assets*", "frames*", "html_maps*", "js*", "maps*", "node_modules*"]
```
*Nota: Não usar `packages = []` junto com `packages.find`, pois causa conflito de sintaxe TOML.*

### Problema B: Dependências Locais Fantasmas
**Sintoma:** Erro `No matching distribution found for nexus-engine`.
**Causa:** O `pyproject.toml` referenciava bibliotecas locais (`path = "../../nexus_core"`) que não existem no ambiente isolado do GitHub.
**Solução:** Remover dependências locais do `pyproject.toml` ou incorporar o código necessário dentro do projeto.

---

## 2. 🌍 Ambiente de Execução (Headless)

### Problema C: Falha no Puppeteer/Chrome (`Could not find Chrome`)
**Sintoma:** O script Node.js (`commander_sim`) falhava ao tentar lançar o navegador.
**Causa:** O `npm install` padrão tentava baixar o Chromium e falhava, ou o caminho do cache não era encontrado.
**Solução:**
1. Usar `puppeteer-core` em vez de `puppeteer` (evita download do binário).
2. Apontar explicitamente para o Chrome do sistema no GitHub Actions (`/usr/bin/google-chrome`).
3. Adicionar setup robusto de Node.js no workflow.
```javascript
const executablePath = process.env.CHROME_BIN || '/usr/bin/google-chrome';
const browser = await puppeteer.launch({ executablePath, ... });
```

### Problema D: Falha de Áudio (`ALSA: Couldn't open audio device`)
**Sintoma:** Scripts Pygame falhavam imediatamente ao tentar `pygame.mixer.init()` porque servidores de CI não têm placa de som.
**Solução:**
1. Definir variável de ambiente `export SDL_AUDIODRIVER=dummy`.
2. Adicionar tratamento de erro (try/except) no código Python para fallback automático.
```python
try:
    pygame.mixer.init()
except pygame.error:
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    pygame.mixer.init()
```

---

## 3. ☁️ Upload e Armazenamento (Google Drive)

### Problema E: Cota Excedida em Service Account
**Sintoma:** Erro 403 `storageQuotaExceeded` ao tentar upload.
**Causa:** Service Accounts têm 0GB de armazenamento e não podem ser "donas" de arquivos em pastas pessoais do Drive (apenas em Workspace/Shared Drives).
**Solução Definitiva:**
Migrar para **OAuth2 com Credenciais de Usuário (`authorized_user`)**.
1. Gerar token localmente via script (`get_token.py`).
2. Salvar o JSON (com `refresh_token`) nos Secrets do GitHub.
3. Isso permite que o robô use a cota de armazenamento da sua conta pessoal.

---

## 4. 🕵️ Falhas Silenciosas de Script

### Problema F: Arquivo de Vídeo Não Encontrado
**Sintoma:** O passo de renderização dizia "sucesso", mas o upload falhava com `File not found`.
**Causa:**
1. Scripts Python apenas importavam o módulo principal mas não executavam a função (falta de `if __name__ == "__main__": run()`).
2. Erros dentro do Python eram capturados por `try...except` genéricos que apenas printavam o erro mas não encerravam o processo com `exit(1)`.
**Solução:**
1. Garantir chamada explícita da função `main()`.
2. Remover `try...except` genéricos ou adicionar `sys.exit(1)` no bloco `except`.
3. Adicionar verificação pós-execução no Workflow:
```yaml
python3 generate_video.py
ls -lh output_render.mp4  # Falha visível se o arquivo não existir
```

---

## Resumo da Arquitetura Final

1. **Workflow:** Instala dependências de sistema (`ffmpeg`, `chrome`), Python e Node.js.
2. **Setup:** Usa `npm ci` e `pip install .` (com `pyproject.toml` corrigido).
3. **Execução:** Scripts rodam em modo `headless` com drivers de áudio/vídeo `dummy`.
4. **Armazenamento:** Script Python híbrido (`upload_to_drive.py`) usa credenciais de usuário para salvar direto no Google Drive pessoal.
