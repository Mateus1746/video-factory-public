# Sistema de Debug de Física - Simulação da Bolinha

Este diretório contém ferramentas de debugging para diagnosticar problemas de física na simulação.

## 🔍 Como Usar

### 1. Executar com Debug Ativado

```bash
uv run simulation.py --debug --json beats.json --audio audio.mp3
```

O flag `--debug` ativa:
- ✅ Logging detalhado de todos os eventos de física
- ✅ Rastreamento de raycasting (sucessos e falhas)
- ✅ Monitoramento de posição da bolinha
- ✅ Registro de colisões
- ✅ Detecção de fail-safes

### 2. Analisar os Logs

Após rodar a simulação, um arquivo `physics_debug.json` será criado com todos os eventos.

Para ver um relatório detalhado:

```bash
python analyze_physics.py
```

## 📊 O Que o Análise Mostra

### Estatísticas Gerais
- Total de frames renderizados
- Número de eventos registrados
- Contagem por tipo de evento

### Análise de Fail-Safes
- **Taxa de fail-safes**: Quantas vezes o raycasting falhou
- **Primeiros fail-safes**: Posição, velocidade e razão da falha
- **Padrões**: Se há um padrão nos fail-safes

### Análise de Raycasts
- Total de tentativas de raycasting
- Taxa de sucesso/falha
- Detalhes das primeiras falhas

### Análise de Posição da Bolinha
- **Overshoot Detection**: Detecta quando a bolinha sai do polígono
- **Distância ao centro**: Monitora se a bolinha está dentro dos limites
- **Frames problemáticos**: Lista frames onde a bolinha está fora

### Análise de Colisões
- Total de colisões
- Distribuição por parede (qual parede recebe mais impactos)

## 🐛 Problemas Comuns e Diagnósticos

### Problema: "Running Fail-Safe" constante

**Diagnóstico:**
```bash
python analyze_physics.py
```

Procure por:
- **Taxa de fail-safe > 50%**: Indica que o raycasting está quebrando sistematicamente
- **Posição de origem fora do polígono**: A bolinha pode estar começando fora
- **Direção inválida**: O vetor de velocidade pode estar com magnitude zero

**Possíveis Causas:**
1. `start_pos` está fora do polígono
2. `direction` não está normalizado ou é zero
3. O polígono mudou de tamanho/forma drasticamente (respiração muito forte)

### Problema: Bolinha atravessa paredes

**Diagnóstico:**
```bash
python analyze_physics.py
```

Procure por:
- **Overshoot**: Listará frames onde `distance_to_center > polygon_radius`
- **Colisões faltando**: Se há poucos eventos de COLLISION mas muitos FAIL_SAFE

**Possíveis Causas:**
1. Padding insuficiente (`radius * 1.1` pode não ser suficiente)
2. Control point da curva Bezier está puxando a bola para fora
3. `end_pos` está sendo calculado incorretamente

### Problema: Bolinha para no meio

**Diagnóstico:**
```bash
python analyze_physics.py
```

Procure por:
- **Progress travado**: Se `_debug_progress` não chega a 1.0
- **Timing issues**: `segment_end_time == segment_start_time`

## 📁 Arquivos do Sistema de Debug

- `physics_debugger.py`: Classe principal de logging
- `analyze_physics.py`: Analisador de logs
- `physics_debug.json`: Log gerado (criado automaticamente)
- `DEBUG_README.md`: Este arquivo

## 💡 Dicas

1. **Rode por pouco tempo**: Para debug, rode apenas 5-10 segundos para não gerar logs gigantescos
2. **Analise imediatamente**: Rode `analyze_physics.py` logo após para ver o relatório
3. **Compare com visualização**: Use `--debug` na simulação para ver overlay visual + logs
4. **Itere rápido**: Faça uma mudança → teste → analise → repita

## 🔧 Personalização

Para adicionar mais logging, edite `Ball` em `simulation.py`:

```python
# Exemplo: Log sempre que recalcular end_pos
if self.debugger:
    self.debugger.log_raycast(self.start_pos, self.vel, polygon.get_vertices(), "RECALC")
```

## 📈 Objetivo

Taxa de fail-safe ideal: **0%**
Taxa de colisões: **≈ 1 por beat**
Overshoot: **0 frames**

Se você alcançar isso, a física está perfeita! 🎯
