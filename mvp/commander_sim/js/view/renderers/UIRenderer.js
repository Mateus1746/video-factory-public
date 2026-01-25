import { CONFIG } from '../../core/Config.js';

export class UIRenderer {
    constructor(ctx, width, height) {
        this.ctx = ctx;
        this.width = width;
        this.height = height;
    }

    draw(simulation, frame) {
        this.ctx.globalCompositeOperation = 'source-over';
        
        this.drawDominationBar(simulation);

        if (frame < 180) {
            this.drawIntro(frame);
        }

        if (simulation.victory) {
            this.drawVictoryScreen(simulation.victory);
        }
    }

    drawDominationBar(sim) {
        let pPower = 0;
        let ePower = 0;
        let nPower = 0;

        sim.buildings.forEach(b => {
            const val = b.count * 2; 
            if (b.team === 'PLAYER') pPower += val;
            else if (b.team === 'ENEMY') ePower += val;
            else nPower += val;
        });

        sim.soldiers.forEach(s => {
            if (s.team === 'PLAYER') pPower++;
            else if (s.team === 'ENEMY') ePower++;
        });

        const total = pPower + ePower + nPower || 1;
        const pPct = pPower / total;
        const ePct = ePower / total;
        
        const barH = 20;
        
        // P1 Segment
        this.ctx.fillStyle = CONFIG.COLORS.PLAYER;
        this.ctx.fillRect(0, 0, this.width * pPct, barH);
        
        // Neutral (Middle)
        this.ctx.fillStyle = CONFIG.COLORS.NEUTRAL;
        this.ctx.fillRect(this.width * pPct, 0, this.width - (this.width * (pPct + ePct)), barH); 
        
        // Enemy Segment
        this.ctx.fillStyle = CONFIG.COLORS.ENEMY;
        this.ctx.fillRect(this.width * (1 - ePct), 0, this.width * ePct, barH);
        
        // VS Indicator in center
        this.ctx.fillStyle = '#fff';
        this.ctx.fillRect((this.width/2) - 2, 0, 4, barH + 5);
    }

    drawIntro(frame) {
        const alpha = Math.min(1, (180 - frame) / 30);
        this.ctx.globalAlpha = alpha;
        
        this.ctx.font = "900 60px Inter, Arial";
        this.ctx.textAlign = "center";
        this.ctx.shadowBlur = 20;
        
        // P1 Name (Top)
        this.ctx.shadowColor = CONFIG.COLORS.PLAYER;
        this.ctx.fillStyle = CONFIG.COLORS.PLAYER;
        this.ctx.fillText(CONFIG.NAMES.player, this.width / 2, 300);
        
        this.ctx.fillStyle = "#fff";
        this.ctx.font = "italic 40px Inter, Arial";
        this.ctx.fillText("VS", this.width / 2, 360);

        // P2 Name (Bottom)
        this.ctx.shadowColor = CONFIG.COLORS.ENEMY;
        this.ctx.fillStyle = CONFIG.COLORS.ENEMY;
        this.ctx.font = "900 60px Inter, Arial";
        this.ctx.fillText(CONFIG.NAMES.enemy, this.width / 2, 420);
        
        this.ctx.globalAlpha = 1.0;
        this.ctx.shadowBlur = 0;
    }

    drawVictoryScreen(winner) {
        this.ctx.fillStyle = "rgba(13, 17, 23, 0.9)";
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        const color = CONFIG.COLORS[winner] || "#ffffff";
        
        this.ctx.shadowBlur = 40;
        this.ctx.shadowColor = color;
        this.ctx.fillStyle = color;
        this.ctx.font = "900 100px Arial";
        this.ctx.textAlign = "center";
        
        let winnerName = winner;
        if (winner === 'PLAYER') winnerName = CONFIG.NAMES.player;
        if (winner === 'ENEMY') winnerName = CONFIG.NAMES.enemy;

        const text = `${winnerName}
WINS`;
        const lines = text.split('\n');
        lines.forEach((line, i) => {
             this.ctx.fillText(line, this.width / 2, (this.height / 2) + (i * 110) - 50);
        });
        
        this.ctx.shadowBlur = 0;
    }
}
