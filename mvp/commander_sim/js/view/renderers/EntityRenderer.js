import { CONFIG } from '../../core/Config.js';

export class EntityRenderer {
    constructor(ctx, theme) {
        this.ctx = ctx;
        this.theme = theme;
    }

    draw(simulation, frame) {
        this.drawPaths(simulation.buildings, simulation.isPathBlocked.bind(simulation));
        simulation.buildings.forEach(b => this.drawBuilding(b, frame));
        simulation.soldiers.forEach(s => this.drawSoldier(s));
    }

    drawPaths(buildings, isPathBlockedFn) {
        if (buildings.length > 40) return;

        this.ctx.lineWidth = 3;
        this.ctx.lineCap = 'round';
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
        
        this.ctx.strokeStyle = CONFIG.COLORS.PATH;
        this.ctx.stroke();
    }

    drawBuilding(b, frame) {
        const color = CONFIG.COLORS[b.team];
        const pulse = b.pulse || 0;
        const radius = CONFIG.BUILDING.RADIUS;
        
        // 1. Outer Glow Ring
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 3 + (pulse * 5);
        this.ctx.beginPath();
        this.ctx.arc(b.x, b.y, radius + (pulse * 10), 0, Math.PI * 2);
        this.ctx.stroke();

        // 2. Inner Core (Filled)
        this.ctx.fillStyle = color;
        this.ctx.globalAlpha = 0.2 + (pulse * 0.3);
        this.ctx.beginPath();
        this.ctx.arc(b.x, b.y, radius * 0.8, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.globalAlpha = 1.0;

        // 3. Tech Ring (Spinning)
        if (b.team !== 'NEUTRAL') {
            const angle = frame * 0.02;
            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.arc(b.x, b.y, radius * 1.1, angle, angle + Math.PI);
            this.ctx.stroke();
        }

        // 4. Text
        this.ctx.globalCompositeOperation = 'source-over';
        this.ctx.fillStyle = '#ffffff';
        this.ctx.font = "bold 40px Arial";
        this.ctx.textAlign = "center";
        this.ctx.textBaseline = "middle";
        this.ctx.fillText(Math.floor(b.count), b.x, b.y);
        
        // Restore Lighter if theme supports it
        if (this.theme.bloom) this.ctx.globalCompositeOperation = 'lighter';
    }

    drawSoldier(s) {
        const color = CONFIG.COLORS[s.team];
        
        const dx = s.target.x - s.x;
        const dy = s.target.y - s.y;
        const dist = Math.sqrt(dx*dx + dy*dy) || 1;
        
        const trailLen = 15;
        const tx = s.x - (dx / dist) * trailLen;
        const ty = s.y - (dy / dist) * trailLen;

        // Draw Trail (Projectile look)
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 4;
        this.ctx.lineCap = 'round';
        this.ctx.beginPath();
        this.ctx.moveTo(tx, ty);
        this.ctx.lineTo(s.x, s.y);
        this.ctx.stroke();

        // Head Glow
        this.ctx.fillStyle = '#ffffff';
        this.ctx.beginPath();
        this.ctx.arc(s.x, s.y, 3, 0, Math.PI * 2);
        this.ctx.fill();
    }
}
