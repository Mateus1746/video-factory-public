import { CONFIG } from '../../core/Config.js';

export class BackgroundRenderer {
    constructor(ctx, width, height, theme) {
        this.ctx = ctx;
        this.width = width;
        this.height = height;
        this.theme = theme;
        this.shake = 0;
        this.frame = 0;
    }

    addShake(amount) {
        this.shake = Math.min(this.shake + amount, 40);
    }

    clear() {
        this.frame++;
        
        // Reset Transform
        this.ctx.setTransform(1, 0, 0, 1, 0, 0);
        
        // Handle Shake logic
        if (this.shake > 0.1) {
            this.shake *= 0.9;
            const damping = this.shake * ((Math.random() > 0.5) ? 1 : -1);
            this.ctx.translate(Math.random() * damping, Math.random() * damping);
        }

        // Draw Background
        this.ctx.globalCompositeOperation = 'source-over';
        this.ctx.fillStyle = CONFIG.COLORS.BG;
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        this.drawGrid();

        // Switch to Additive Blending for NEON GLOW if active
        if (this.theme.bloom) {
            this.ctx.globalCompositeOperation = 'lighter';
        }
    }

    drawGrid() {
        this.ctx.lineWidth = 1;
        this.ctx.strokeStyle = CONFIG.COLORS.GRID;
        
        const scroll = (this.frame * 0.5) % 100; 
        
        this.ctx.beginPath();
        // Vertical
        for (let x = 0; x <= this.width; x += 100) {
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.height);
        }
        // Horizontal
        for (let y = scroll - 100; y <= this.height; y += 100) {
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.width, y);
        }
        this.ctx.stroke();
    }
}
