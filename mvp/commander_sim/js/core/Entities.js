import { CONFIG } from './Config.js';

export const ENTITY_EVENTS = {
    NONE: 0,
    SOLDIER_HIT: 1,
    BUILDING_CAPTURED: 2
};

export class Building {
    constructor(x, y, team, count, type = 'NORMAL') {
        this.x = x;
        this.y = y;
        this.team = team;
        this.count = count;
        this.type = type; // NORMAL, FACTORY, BUNKER
        this.lastSpawn = 0; // Managed by simulation frame count, not Date.now()
        this.frameCounter = 0;
        
        this.spawnRateMultiplier = 1;
        this.defenseMultiplier = 1;
        this.pulse = 0;

        if (this.type === 'FACTORY') this.spawnRateMultiplier = 2.0;
        if (this.type === 'BUNKER') this.defenseMultiplier = 2.0;
    }

    update() {
        if (this.pulse > 0.01) this.pulse *= 0.9;
        
        if (this.team !== 'NEUTRAL' && this.count < CONFIG.BUILDING.MAX_COUNT) {
            this.frameCounter++;
            const interval = CONFIG.SOLDIER.SPAWN_INTERVAL / this.spawnRateMultiplier;
            if (this.frameCounter >= interval) {
                this.count++;
                this.frameCounter = 0;
                this.pulse = 1.0;
            }
        }
    }
}

export class Soldier {
    constructor(x, y, targetBuilding, team) {
        this.x = x;
        this.y = y;
        this.target = targetBuilding;
        this.team = team;
        this.reached = false;
        this.hasHit = false;
    }

    // Returns an event code if something significant happened
    update() {
        if (this.reached || this.hasHit) return ENTITY_EVENTS.NONE;

        let dx = this.target.x - this.x;
        let dy = this.target.y - this.y;
        let distSq = dx * dx + dy * dy;

        // Hit detection radius squared (10 * 10 = 100)
        if (distSq < 100) { 
            this.reached = true;
            return this.hit();
        }

        let dist = Math.sqrt(distSq);
        this.x += (dx / dist) * CONFIG.SOLDIER.SPEED;
        this.y += (dy / dist) * CONFIG.SOLDIER.SPEED;

        return ENTITY_EVENTS.NONE;
    }

    hit() {
        if (this.hasHit) return ENTITY_EVENTS.NONE;
        this.hasHit = true;

        let event = ENTITY_EVENTS.SOLDIER_HIT;

        if (this.target.team === this.team) {
            this.target.count++;
        } else {
            let damage = 1;
            // Bunker defense logic
            if (this.target.type === 'BUNKER' && this.target.team !== 'NEUTRAL') {
                if (Math.random() < 0.5) damage = 0;
            }
            
            this.target.count -= damage;

            if (this.target.count < 0) {
                this.target.team = this.team;
                this.target.count = 1;
                event = ENTITY_EVENTS.BUILDING_CAPTURED;
            }
        }
        return event;
    }
}
