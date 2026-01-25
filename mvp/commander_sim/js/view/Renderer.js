import { CONFIG } from '../core/Config.js';
import { ParticleSystem } from './Particles.js';
import { ThemeManager } from './ThemeManager.js';
import { BackgroundRenderer } from './renderers/BackgroundRenderer.js';
import { EntityRenderer } from './renderers/EntityRenderer.js';
import { UIRenderer } from './renderers/UIRenderer.js';

export class Renderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.canvas.width = CONFIG.SCREEN_WIDTH;
        this.canvas.height = CONFIG.SCREEN_HEIGHT;
        
        // State
        this.frame = 0;
        
        // Theme
        this.theme = ThemeManager.getTheme(CONFIG.THEME || 'NEON');
        console.log(`🎨 Renderer initialized with Theme: ${this.theme.name}`);
        this.applyThemeColors();

        // Sub-Renderers
        this.bgRenderer = new BackgroundRenderer(this.ctx, this.canvas.width, this.canvas.height, this.theme);
        this.entityRenderer = new EntityRenderer(this.ctx, this.theme);
        this.uiRenderer = new UIRenderer(this.ctx, this.canvas.width, this.canvas.height);
        
        // Particles
        this.particles = new ParticleSystem();
    }

    applyThemeColors() {
        CONFIG.COLORS.BG = this.theme.bg;
        CONFIG.COLORS.GRID = this.theme.grid;
        CONFIG.COLORS.PLAYER = this.theme.player;
        CONFIG.COLORS.ENEMY = this.theme.enemy;
        CONFIG.COLORS.NEUTRAL = this.theme.neutral;
    }

    handleEvent(event) {
        if (event.type === 'HIT') {
             const isEnemy = event.team !== event.targetTeam;
             const color = CONFIG.COLORS[event.team];
             
             if (isEnemy) {
                 this.particles.emit(event.x, event.y, CONFIG.COLORS[event.targetTeam] || '#fff', 4, 'spark');
                 if (Math.random() < 0.15) this.bgRenderer.addShake(1.5);
             } else {
                 this.particles.emit(event.x, event.y, color, 2, 'spark');
             }
        } else if (event.type === 'CAPTURE') {
            const color = CONFIG.COLORS[event.team];
            this.particles.emitExplosion(event.x, event.y, color);
            this.bgRenderer.addShake(15);
        }
    }

    draw(simulation) {
        this.frame++;
        
        // 1. Background & Grid (Handles Shake & Clear)
        this.bgRenderer.clear();

        // 2. Entities (Paths, Buildings, Soldiers)
        this.entityRenderer.draw(simulation, this.frame);

        // 3. Particles
        this.particles.update();
        this.drawParticles();

        // 4. UI (Domination, Intro, Victory)
        this.uiRenderer.draw(simulation, this.frame);
    }

    drawParticles() {
        for (const p of this.particles.particles) {
            this.ctx.globalAlpha = p.alpha;
            
            if (p.type === 'shockwave') {
                this.ctx.strokeStyle = p.color;
                this.ctx.lineWidth = 4 * p.alpha;
                this.ctx.beginPath();
                this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                this.ctx.stroke();
            } else if (p.type === 'text') {
                this.ctx.globalCompositeOperation = 'source-over';
                this.ctx.fillStyle = p.color;
                this.ctx.font = "bold 30px Arial";
                this.ctx.fillText(p.text, p.x, p.y);
                if (this.theme.bloom) this.ctx.globalCompositeOperation = 'lighter';
            } else {
                this.ctx.fillStyle = p.color;
                this.ctx.beginPath();
                this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                this.ctx.fill();
            }
        }
        this.ctx.globalAlpha = 1.0;
    }
}
