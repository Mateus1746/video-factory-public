import random
from .config import HEIGHT, BALANCE, FPS, DEBUG

class Director:
    def __init__(self):
        self.total_waves = 5
        self.current_wave = 1
        self.enemies_spawned_in_wave = 0
        self.enemies_per_wave = 8
        
    def calculate_enemy_stats(self, towers, wave):
        # 1. Cálculo de DPS Real (Mais preciso para o Drama)
        total_dps = 0
        ice_stacks = 0
        
        for t in towers:
            fire_rate = FPS / max(1, t.max_cooldown)
            raw_dps = t.damage * fire_rate
            
            # Ajuste por Tipo
            if hasattr(t, 'type'):
                if t.type == "fire":
                    raw_dps *= 1.5 # Assume que fogo acerta mais gente ou causa caos
                elif t.type == "ice":
                    ice_stacks += 1 # Gelo não aumenta dano, mas aumenta tempo
            
            total_dps += raw_dps
            
        if total_dps == 0: total_dps = 50
        
        # Fator de Eficiência: 70%
        # Compensa o tempo de voo dos projéteis, overkill e delay de mira.
        # Sem isso, o Diretor acha que a defesa é perfeita e manda mobs impossíveis.
        total_dps *= 0.7
        
        # 2. Definição do Inimigo
        enemy_type = "normal"
        r = random.random()
        
        # Boss Logic
        if wave == self.total_waves:
            if self.enemies_spawned_in_wave >= self.enemies_per_wave - 1:
                enemy_type = "boss"
            else:
                enemy_type = "tank" if r < 0.3 else "runner" if r < 0.6 else "normal"
        elif r < 0.2: enemy_type = "runner"
        elif r < 0.4 and wave > 2: enemy_type = "tank"

        # 3. Velocidade e Tempo de Trajeto
        speed_base = HEIGHT * BALANCE["ENEMY_SPEED_SCALING"]
        
        # Ajuste de velocidade baseada no gelo
        slow_factor = 1.0
        if ice_stacks > 0:
            slow_factor = max(0.5, 1.0 - (ice_stacks * 0.15))
            
        base_speed_mult = 1.0
        if enemy_type == "runner": base_speed_mult = 1.8
        elif enemy_type == "tank": base_speed_mult = 0.6
        elif enemy_type == "boss": base_speed_mult = 0.4
        
        final_speed = speed_base * base_speed_mult
        
        # 4. DRAMA ENGINE CORRIGIDA (Baseada em Fluxo)
        # O erro anterior era calcular HP baseado no tempo total de viagem.
        # O correto para ondas é: HP = DPS * Intervalo_de_Spawn.
        
        spawn_rate_frames = max(15, 60 - (wave * 5))
        spawn_interval_sec = spawn_rate_frames / FPS
        
        # HP Sustentável = Dano que a defesa consegue causar entre um spawn e outro
        sustainable_hp = total_dps * spawn_interval_sec
        
        # Multiplicador de Dificuldade
        # > 1.0 significa que os inimigos vão acumular (precisa de burst/área)
        # < 1.0 significa que morrem antes do próximo nascer
        
        difficulty_mult = 1.0
        
        if wave == 1: 
            # Wave 1: Fácil para farmar (morrem rápido)
            difficulty_mult = 0.6 
        elif wave == self.total_waves and enemy_type == "boss":
            # Boss é único, então ele PODE tankar o tempo de viagem inteiro
            # Volta para a lógica de "Travel Time" só para ele
            distance = HEIGHT * 0.45
            travel_time = (distance / final_speed) / FPS
            travel_time /= slow_factor
            
            # Boss deve tankar quase todo o trajeto
            drama_factor = random.uniform(0.85, 1.1) 
            hp = (total_dps * travel_time) * drama_factor
            
            if DEBUG:
                 print(f"\n👹 BOSS HP CALC: DPS {int(total_dps)} * Time {travel_time:.1f}s * Drama {drama_factor:.2f} = {int(hp)}")
            return hp, final_speed, enemy_type
        else:
            # Waves 2-4: Acumulam levemente (1.2x a 1.5x do sustentável)
            # Isso cria a "horda" sem ser impossível
            difficulty_mult = random.uniform(1.1, 1.4)

        hp = sustainable_hp * difficulty_mult
        
        # Ajuste fino para tipos
        if enemy_type == "tank": hp *= 1.4 
        if enemy_type == "runner": hp *= 0.7

        if DEBUG and random.random() < 0.1: # Log ocasional
             print(f"📊 Wave {wave} HP: {int(hp)} (Sust: {int(sustainable_hp)})")

        return hp, final_speed, enemy_type
