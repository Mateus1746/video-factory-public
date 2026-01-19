# Contexto do Projeto: Roguelike Survival Pygame

## 📅 Última Atualização: 2026-01-07
## 🎯 Objetivo Atual: Estruturação de Assets e Identidade Visual/Sonora

---

## 📂 Estrutura de Arquivos Criada
- `assets/sprites/player/`: Sprites do personagem principal.
- `assets/sprites/enemies/`: Sprites para mobs (Slimes, Esqueletos, Bosses).
- `assets/audio/music/`: Trilhas sonoras (Menu, Gameplay, Hordas).
- `assets/audio/sfx/`: Efeitos sonoros (Hit, Death, Level Up, Weapon Fire).

## 💡 Definições de Design (Roadmap de Assets)

### 🎨 Visual (Sprites)
1. **Player:** "Sobrevivente Arcano". Cores de alto contraste (Capa Vermelha). Animações planejadas: Idle, Run, Attack, Death.
2. **Mobs:**
   - Tier 1: Slimes/Morcegos (Fodder).
   - Tier 2: Golems (Tanks com feedback de dano "white-flash").
   - Tier 3: Arqueiros/Magos (Ranged).
   - Boss: Necromante (Grande escala, aura visual).

### 🔊 Áudio (Soundscape)
1. **Música:** Evolutiva. BPM médio no início, camadas de percussão adicionais conforme o tempo de sobrevivência aumenta.
2. **SFX:** 
   - Feedback de dano grave para o player.
   - Sons de morte curtos e satisfatórios ("Pop").
   - Variação de pitch (0.9x - 1.1x) em disparos de armas para evitar repetitividade.

## 🛠️ Status Técnico
- Diretórios criados fisicamente no sistema.
- Gerenciador de pacotes: `uv`.
- Engine: `pygame`.

## 🚀 Próximos Passos
1. **Placeholders:** Gerar sprites básicos (quadrados/círculos coloridos) para testar a lógica de renderização.
2. **Carregamento:** Implementar sistema de `AssetManager` em Python para carregar essas pastas automaticamente.
3. **Lógica de Áudio:** Configurar o mixer do Pygame para suportar as variações de pitch sugeridas.
