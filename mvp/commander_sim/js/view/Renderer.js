import { CONFIG } from '../core/Config.js';
import { ParticleSystem } from './Particles.js';

export class Renderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.canvas.width = CONFIG.SCREEN_WIDTH;
        this.canvas.height = CONFIG.SCREEN_HEIGHT;
        this.shake = 0;
        this.particles = new ParticleSystem();
    }

    handleEvent(event) {
        if (event.type === 'HIT') {
             const color = CONFIG.COLORS[event.team];
             // If enemy hit (different teams), show hit effect
             if (event.team !== event.targetTeam) {
                 this.particles.emit(event.x, event.y, CONFIG.COLORS[event.targetTeam] || '#fff', 3, 'spark');
                 // Small shake for impact
                 if (Math.random() < 0.2) this.addShake(1);
             } else {
                 // Reinforcement hit
                 this.particles.emit(event.x, event.y, color, 2, 'spark');
             }
        } else if (event.type === 'CAPTURE') {
            const color = CONFIG.COLORS[event.team];
            this.particles.emitExplosion(event.x, event.y, color);
            this.addShake(20);
        }
    }

    addShake(amount) {
        this.shake = Math.min(this.shake + amount, 50);
    }

    clear(biome = 'TECH') {
        this.ctx.setTransform(1, 0, 0, 1, 0, 0);
        
        if (this.shake > 0.5) {
            this.shake *= 0.9;
            const dx = (Math.random() - 0.5) * this.shake;
            const dy = (Math.random() - 0.5) * this.shake;
            this.ctx.translate(dx, dy);
        } else {
            this.shake = 0;
        }

        // Draw background
        this.ctx.fillStyle = CONFIG.COLORS.BG;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        this.drawGrid();
    }

    drawGrid() {
        this.ctx.strokeStyle = CONFIG.COLORS.GRID;
        this.ctx.lineWidth = 1;
        // Vertical
        for (let x = 0; x < this.canvas.width; x += 100) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }
        // Horizontal
        for (let y = 0; y < this.canvas.height; y += 100) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
    }

    draw(simulation) {
        this.clear(); // Add biome logic if needed later

        // Draw Paths
        this.drawPaths(simulation.buildings, simulation.isPathBlocked.bind(simulation));

        // Draw Buildings
        simulation.buildings.forEach(b => this.drawBuilding(b));

        // Draw Soldiers
        simulation.soldiers.forEach(s => this.drawSoldier(s));

        // Update and Draw Particles
        this.particles.update();
        this.drawParticles();

        // Draw Victory
        if (simulation.victory) {
            this.drawVictoryScreen(simulation.victory);
        }
    }

    drawPaths(buildings, isPathBlockedFn) {
        if (buildings.length > 20) return; 
        this.ctx.lineWidth = 2;
        this.ctx.strokeStyle = CONFIG.COLORS.PATH;
        this.ctx.beginPath(); 
        for (let i = 0; i < buildings.length; i++) {
            for (let j = i + 1; j < buildings.length; j++) {
                const b1 = buildings[i];
                const b2 = buildings[j];
                if (isPathBlockedFn(b1, b2)) continue;
                this.ctx.moveTo(b1.x, b1.y);
                this.ctx.lineTo(b2.x, b2.y);
            }
        }
        this.ctx.stroke();
    }

    drawBuilding(b) {
        const color = CONFIG.COLORS[b.team];
        const pulseScale = b.pulse ? b.pulse : 0;
        const radius = CONFIG.BUILDING.RADIUS + (pulseScale * 5);
        
        if (pulseScale > 0.5) {
            this.ctx.shadowBlur = CONFIG.BUILDING.GLOW_RADIUS + (pulseScale * 20);
            this.ctx.shadowColor = color;
        }

        this.ctx.fillStyle = color;
        this.ctx.beginPath();
        this.ctx.arc(b.x, b.y, radius, 0, Math.PI * 2);
        this.ctx.fill();
        
        this.ctx.shadowBlur = 0; 
        
        this.ctx.fillStyle = "rgba(0,0,0,0.3)";
        this.ctx.beginPath();
        this.ctx.arc(b.x, b.y, radius * 0.8, 0, Math.PI * 2);
        this.ctx.fill();
        
        if (pulseScale > 0.1) {
             this.ctx.strokeStyle = color;
             this.ctx.lineWidth = 2 * pulseScale;
             this.ctx.beginPath();
             this.ctx.arc(b.x, b.y, radius + (15 * (1-pulseScale)), 0, Math.PI * 2);
             this.ctx.stroke();
        }

        this.ctx.fillStyle = CONFIG.COLORS.WHITE;
        this.ctx.font = "bold 48px Inter";
        this.ctx.textAlign = "center";
        this.ctx.textBaseline = "middle";
        this.ctx.fillText(Math.floor(b.count), b.x, b.y);
    }

    drawSoldier(s) {
        const color = CONFIG.COLORS[s.team];
        this.ctx.fillStyle = color;
        this.ctx.beginPath();
        this.ctx.arc(s.x, s.y, CONFIG.SOLDIER.RADIUS, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.strokeStyle = CONFIG.COLORS.WHITE;
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
    }

    drawParticles() {
        for (const p of this.particles.particles) {
            this.ctx.globalAlpha = p.alpha;
            this.ctx.fillStyle = p.color;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            this.ctx.fill();
        }
        this.ctx.globalAlpha = 1.0;
    }

    drawVictoryScreen(winner) {
        this.ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.fillStyle = CONFIG.COLORS[winner] || "#ffffff";
        this.ctx.font = "900 80px Inter";
        this.ctx.textAlign = "center";
        this.ctx.shadowBlur = 30;
        this.ctx.shadowColor = CONFIG.COLORS[winner];
        
        const text = `${winner} WINS!`;
        this.ctx.fillText(text, this.canvas.width / 2, this.canvas.height / 2);
    }
}
