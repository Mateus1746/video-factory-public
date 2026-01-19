export class Particle {
    constructor(x, y, color, speed, life, type = 'spark') {
        this.x = x;
        this.y = y;
        this.color = color;
        this.life = life;
        this.maxLife = life;
        this.type = type; 
        
        const angle = Math.random() * Math.PI * 2;
        this.vx = Math.cos(angle) * speed * (Math.random() + 0.5);
        this.vy = Math.sin(angle) * speed * (Math.random() + 0.5);
        
        this.size = Math.random() * 3 + 2;
        this.alpha = 1;
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.life--;
        this.alpha = this.life / this.maxLife;
        this.vx *= 0.95;
        this.vy *= 0.95;
    }
}

export class ParticleSystem {
    constructor() {
        this.particles = [];
        this.maxParticles = 500;
    }

    emit(x, y, color, count = 5, type = 'spark') {
        if (this.particles.length > this.maxParticles) return;
        for (let i = 0; i < count; i++) {
            this.particles.push(new Particle(x, y, color, 3, 30 + Math.random() * 20, type));
        }
    }

    emitExplosion(x, y, color) {
        this.emit(x, y, color, 20, 'spark');
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
