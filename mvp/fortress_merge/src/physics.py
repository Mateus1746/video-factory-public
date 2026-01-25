import math
from .config import BALANCE, COLORS
from .components import Particle, FloatingText

class PhysicsEngine:
    def __init__(self, game):
        self.game = game

    def check_collisions(self):
        """Processa colisões entre projéteis e inimigos."""
        # Iterar sobre cópia para permitir remoção segura
        for p in self.game.projectiles[:]:
            alive = p.update() # Move o projétil
            hit = False
            
            if alive:
                # Otimização simples: Verifica colisão apenas se estiver na tela
                # Poderia usar Quadtree aqui se tivéssemos >100 inimigos
                for e in self.game.enemies:
                    dist = math.hypot(e.x - p.x, e.y - p.y)
                    if dist < e.radius + 40: # 40 = hitbox aprox do projétil
                        self._resolve_hit(p, e)
                        hit = True
                        break # Projétil hitou um inimigo, não atravessa (a menos que seja perfurante - TODO)
            
            if hit or not alive:
                if p in self.game.projectiles:
                    self.game.projectiles.remove(p)

    def _resolve_hit(self, projectile, target):
        """Aplica dano e efeitos de impacto."""
        if projectile.type == "fire":
            # Dano em Área (AOE)
            self.game.assets.play_sfx("explosion")
            for neighbor in self.game.enemies:
                if math.hypot(neighbor.x - projectile.x, neighbor.y - projectile.y) < BALANCE["EXPLOSION_RADIUS"]:
                    neighbor.take_damage(projectile.damage * BALANCE["FIRE_DAMAGE_MULTIPLIER"], "fire")
            
            # FX Explosão
            for _ in range(8):
                self.game.particles.append(Particle(projectile.x, projectile.y, (255, 100, 0), 6))
                
        else:
            # Dano Único (Standard, Ice, Poison, etc)
            target.take_damage(projectile.damage, projectile.type)
            self.game.particles.append(Particle(projectile.x, projectile.y, projectile.color, 3))
        
        # Texto de Dano
        self.game.floating_texts.append(
            FloatingText(target.x, target.y - 30, f"-{int(projectile.damage)}", COLORS["WHITE"], self.game.assets.get_font("dmg"))
        )

    def check_base_damage(self):
        """Verifica se inimigos atingiram a base."""
        for e in self.game.enemies[:]:
            if e.move(): # Retorna True se chegou ao final do caminho (Base)
                self.game.base_hp -= BALANCE["ENEMY_DAMAGE_TO_BASE"]
                self.game.enemies.remove(e)
                
                # Feedback de Dano na Base
                self.game.assets.play_sfx("hit")
                self.game.camera.shake(BALANCE["SHAKE_ON_HIT"])
                for _ in range(BALANCE["PARTICLE_COUNT_HIT"]): 
                    self.game.particles.append(Particle(e.x, e.y, COLORS["RED"], BALANCE["PARTICLE_SIZE_HIT"]))
            
            elif e.hp <= 0:
                self._handle_enemy_death(e)

    def _handle_enemy_death(self, enemy):
        """Processa recompensas e FX de morte."""
        reward = BALANCE["GOLD_REWARD_BASE"] * self.game.director.current_wave
        if enemy.type == "boss": 
            reward *= BALANCE["BOSS_GOLD_MULTIPLIER"]
        
        self.game.gold += int(reward)
        self.game.enemies.remove(enemy)
        
        # COMBO System
        self.game.combo += 1
        self.game.combo_timer = 60 # 1 segundo para manter o combo
        
        # FX Morte
        self.game.assets.play_sfx("explosion")
        self.game.camera.shake(BALANCE["SHAKE_ON_KILL"])
        color = COLORS["GOLD"] if enemy.type == "boss" else COLORS["RED"]
        
        for _ in range(BALANCE["PARTICLE_COUNT_KILL"]): 
            self.game.particles.append(Particle(enemy.x, enemy.y, color, 6))
            
        self.game.floating_texts.append(
            FloatingText(enemy.x, enemy.y, f"+{int(reward)}", COLORS["GOLD"], self.game.assets.get_font("dmg"))
        )
