from .entities import Tower
from .components import Particle, FloatingText
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
        """Lógica para comprar novas torres."""
        if game.gold >= game.tower_cost and self.buy_cooldown == 0:
            # Tenta encontrar um espaço vazio no grid (5x5)
            for r in range(5):
                for c in range(5):
                    if not any(t.row == r and t.col == c for t in game.towers):
                        # Executa compra
                        game.towers.append(Tower(1, r, c, game.grid))
                        game.gold -= game.tower_cost
                        game.tower_cost = int(game.tower_cost * BALANCE["TOWER_COST_SCALE"])
                        
                        # Feedback visual/sonoro
                        game.assets.play_sfx("buy")
                        t = game.towers[-1]
                        for _ in range(10): 
                            game.particles.append(Particle(t.x, t.y, COLORS["CYAN"], 5))
                        
                        self.buy_cooldown = 5 # Pequeno respiro entre compras
                        return
    
    def _handle_merging(self, game):
        """Lógica para fundir torres de mesmo nível."""
        if len(game.towers) < 2 or self.merge_cooldown > 0:
            return

        for i, t1 in enumerate(game.towers):
            for j, t2 in enumerate(game.towers):
                if i != j and t1.level == t2.level:
                    # HERANÇA DE ELEMENTO:
                    # Se t1 é comum e t2 tem elemento, t1 herda o elemento de t2.
                    if t1.type == "standard" and t2.type != "standard":
                        t1.type = t2.type

                    # Executa Merge
                    t1.level += 1
                    t1.damage *= 1.9
                    t1.trigger_merge_effect() # Animação de Pop
                    game.towers.remove(t2)
                    
                    # Feedback visual/sonoro
                    game.assets.play_sfx("merge")
                    game.camera.shake(5)
                    for _ in range(15): 
                        game.particles.append(Particle(t1.x, t1.y, COLORS["GOLD"], 6))
                    game.floating_texts.append(FloatingText(
                        t1.x, t1.y, "MERGE!", COLORS["GOLD"], game.assets.get_font("dmg")
                    ))
                    
                    self.merge_cooldown = 10 # Evita que tudo exploda em merge ao mesmo tempo
                    return
