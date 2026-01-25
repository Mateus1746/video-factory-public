from .entities import Tower
from .components import Particle, FloatingText, Shockwave
from .config import COLORS, BALANCE

class BotController:
    def __init__(self):
        self.buy_cooldown = 0
        self.merge_cooldown = 0

    def update(self, game):
        """Executa as decisões do bot com base no estado atual do jogo."""
        if game.game_over or game.victory:
            return

        if self.buy_cooldown > 0: self.buy_cooldown -= 1
        if self.merge_cooldown > 0: self.merge_cooldown -= 1

        self._handle_buying(game)
        self._handle_merging(game)

    def _handle_buying(self, game):
        """Lógica para comprar novas torres com heurística de posicionamento."""
        if game.gold >= game.tower_cost and self.buy_cooldown == 0:
            # Prioridade de Posição: Centro > Bordas
            # O Grid é 5x5. (2,2) é o centro.
            preferred_spots = sorted([(r, c) for r in range(5) for c in range(5)], 
                                     key=lambda p: abs(p[0]-2) + abs(p[1]-2))
            
            for r, c in preferred_spots:
                if not any(t.row == r and t.col == c for t in game.towers):
                    # Move Cursor
                    pos_x, pos_y = game.grid.get_pos(r, c)
                    game.cursor.move_to(pos_x, pos_y)
                    
                    # Se o cursor chegou perto, executa (simulação simplificada: executa logo, cursor corre atrás)
                    # Para ficar PERFEITO, o bot deveria esperar o cursor.
                    # Mas para "juicy", o cursor atrasado é ok.
                    
                    # Executa compra
                    game.towers.append(Tower(1, r, c, game.grid))
                    game.gold -= game.tower_cost
                    game.tower_cost = int(game.tower_cost * BALANCE["TOWER_COST_SCALE"])
                    
                    # Feedback visual/sonoro
                    game.assets.play_sfx("buy")
                    t = game.towers[-1]
                    for _ in range(10): 
                        game.particles.append(Particle(t.x, t.y, COLORS["CYAN"], 5))
                    
                    self.buy_cooldown = 15 # Aumentei cooldown para dar tempo do cursor chegar visualmente
                    return
    
    def _handle_merging(self, game):
        """Lógica para fundir torres de mesmo nível com verificação de segurança."""
        if len(game.towers) < 2 or self.merge_cooldown > 0:
            return

        # Segurança: Não fundir se tiver poucas torres, a menos que seja early game
        if len(game.towers) < 4 and game.director.current_wave > 3:
             return

        for i, t1 in enumerate(game.towers):
            for j, t2 in enumerate(game.towers):
                if i != j and t1.level == t2.level:
                    # HERANÇA DE ELEMENTO:
                    if t1.type == "standard" and t2.type != "standard":
                        t1.type = t2.type
                    # Se t2 está numa posição melhor (mais ao centro), movemos t1 para lá
                    dist_t1 = abs(t1.row-2) + abs(t1.col-2)
                    dist_t2 = abs(t2.row-2) + abs(t2.col-2)
                    
                    survivor = t1
                    sacrifice = t2
                    
                    if dist_t2 < dist_t1:
                        survivor = t2
                        sacrifice = t1
                        
                    # Move Cursor
                    game.cursor.move_to(survivor.x, survivor.y)

                    # Executa Merge
                    survivor.level += 1
                    survivor.damage *= 1.9
                    survivor.trigger_merge_effect() 
                    game.towers.remove(sacrifice)
                    
                    # Feedback visual/sonoro
                    game.assets.play_sfx("merge")
                    game.camera.shake(BALANCE["SHAKE_ON_MERGE"])
                    
                    # Shockwave
                    game.shockwaves.append(Shockwave(survivor.x, survivor.y, COLORS["CYAN"]))
                    
                    for _ in range(BALANCE["PARTICLE_COUNT_MERGE"]): 
                        game.particles.append(Particle(survivor.x, survivor.y, COLORS["GOLD"], 6))
                    game.floating_texts.append(FloatingText(
                        survivor.x, survivor.y, "MERGE!", COLORS["GOLD"], game.assets.get_font("dmg")
                    ))
                    
                    self.merge_cooldown = 20 # Mais tempo para o olho acompanhar o mouse
                    return
