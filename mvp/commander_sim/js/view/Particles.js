export class Particle {
    constructor(x, y, color, speed, life, type = 'spark', text = null) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.life = life;
        this.maxLife = life;
        this.type = type; // spark, shockwave, text
        this.text = text;
        
        // Physics
        const angle = Math.random() * Math.PI * 2;
        // Shockwaves don't move, they expand
        const moveSpeed = type === 'shockwave' ? 0 : speed;
        
        this.vx = Math.cos(angle) * moveSpeed * (Math.random() + 0.5);
        this.vy = Math.sin(angle) * moveSpeed * (Math.random() + 0.5);
        
        if (type === 'text') {
            this.vx = (Math.random() - 0.5) * 1;
            this.vy = -2; // Float up
        }

        this.size = Math.random() * 3 + 2;
        if (type === 'shockwave') this.size = 5; // Start small
        
        this.alpha = 1;
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.life--;
        
        // Normalize alpha
        this.alpha = Math.max(0, this.life / this.maxLife);

        if (this.type === 'spark') {
            this.vx *= 0.92; // Friction
            this.vy *= 0.92;
            this.size *= 0.96; // Shrink
        } else if (this.type === 'shockwave') {
            this.size += 3; // Expand rapidly
            this.alpha = Math.pow(this.alpha, 2); // Fade out faster visually
        } else if (this.type === 'text') {
            this.vy *= 0.98; // Slow rise
        }
    }
}

export class ParticleSystem {
    constructor() {
        this.particles = [];
        this.maxParticles = 800;
    }

    emit(x, y, color, count = 5, type = 'spark') {
        if (this.particles.length > this.maxParticles) return;
        for (let i = 0; i < count; i++) {
            this.particles.push(new Particle(x, y, color, 4, 20 + Math.random() * 20, type));
        }
    }

    emitExplosion(x, y, color) {
        // Sparks
        this.emit(x, y, color, 15, 'spark');
        // Shockwave
        this.particles.push(new Particle(x, y, color, 0, 30, 'shockwave'));
    }
    
    emitText(x, y, text, color = '#fff') {
         this.particles.push(new Particle(x, y, color, 0, 40, 'text', text));
    }

    update() {
        for (let i = this.particles.length - 1; i >= 0; i--) {
            let p = this.particles[i];
            p.update();
            if (p.life <= 0) {
                this.particles.splice(i, 1);
            }
        }
    }
}
