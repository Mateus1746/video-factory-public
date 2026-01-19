import { CONFIG } from './Config.js';
import { Building, Soldier, ENTITY_EVENTS } from './Entities.js';
import { AIAgent } from './AI.js';

export class Simulation {
    constructor() {
        this.buildings = [];
        this.soldiers = [];
        this.scheduledSoldiers = [];
        this.ais = [];
        this.teams = [];
        this.victory = null;
        this.victoryFrames = 0;
        this.finished = false;
        
        // Cache for path blocking to optimize performance
        this.pathCache = new Map();
        this.obstacles = [];
        this.mapData = null;
        
        // Events queue to communicate with Renderer/Audio
        this.events = [];
    }

    loadMap(mapData) {
        this.mapData = mapData;
        this.buildings = [];
        this.soldiers = [];
        this.scheduledSoldiers = [];
        this.pathCache.clear();
        this.events = [];
        this.victory = null;
        this.victoryFrames = 0;
        this.finished = false;

        if (mapData.buildings) {
            this.buildings = mapData.buildings.map(b => 
                new Building(b.x, b.y, b.team.toUpperCase(), b.count, b.type)
            );
        }

        if (mapData.obstacles) {
            this.obstacles = mapData.obstacles;
        }

        // Identify teams
        this.teams = [...new Set(this.buildings.map(b => b.team))].filter(t => t !== 'NEUTRAL');
        
        // Initialize AI
        this.ais = this.teams.map(team => new AIAgent(team));
    }

    // Main tick function
    update() {
        if (this.finished) return;

        this.events = []; // Clear events from previous frame

        // 1. Update Buildings
        this.buildings.forEach(b => b.update());

        // 2. Spawn Scheduled Soldiers
        if (this.scheduledSoldiers.length > 0) {
            for (let i = this.scheduledSoldiers.length - 1; i >= 0; i--) {
                let s = this.scheduledSoldiers[i];
                s.framesLeft--;
                if (s.framesLeft <= 0) {
                    this.soldiers.push(new Soldier(s.x, s.y, s.target, s.team));
                    this.scheduledSoldiers.splice(i, 1);
                }
            }
        }

        // 3. Update Soldiers & Resolve Collisions
        for (let i = this.soldiers.length - 1; i >= 0; i--) {
            let s = this.soldiers[i];
            const eventCode = s.update();
            
            if (s.reached) {
                this.soldiers.splice(i, 1);
                this.handleSoldierEvent(s, eventCode);
            }
        }

        // 4. Update AI
        this.ais.forEach(ai => {
            const cmd = ai.update(this.buildings, (a, b) => this.isPathBlocked(a, b));
            if (cmd) {
                this.sendTroops(cmd.from, cmd.to);
            }
        });

        // 5. Check Victory
        this.checkVictory();
    }

    handleSoldierEvent(soldier, code) {
        if (code === ENTITY_EVENTS.SOLDIER_HIT) {
            this.events.push({
                type: 'HIT',
                x: soldier.target.x,
                y: soldier.target.y,
                team: soldier.team, // Who hit
                targetTeam: soldier.target.team // Who was hit
            });
        } else if (code === ENTITY_EVENTS.BUILDING_CAPTURED) {
            this.events.push({
                type: 'CAPTURE',
                x: soldier.target.x,
                y: soldier.target.y,
                team: soldier.team
            });
            this.pathCache.clear(); // Clear cache as game state changed significantly? (Optional)
        }
    }

    sendTroops(from, to) {
        if (this.isPathBlocked(from, to)) return;

        let amount = Math.floor(from.count * CONFIG.SOLDIER.SEND_PERCENT);
        from.count -= amount;

        this.events.push({ type: 'SPAWN', x: from.x, y: from.y });

        for (let i = 0; i < amount; i++) {
            this.scheduleSoldier(from.x, from.y, to, from.team, i * CONFIG.SOLDIER.SEND_DELAY);
        }
    }

    scheduleSoldier(x, y, target, team, frameDelay) {
        this.scheduledSoldiers.push({ x, y, target, team, framesLeft: frameDelay });
    }

    checkVictory() {
        if (this.victory) {
            this.victoryFrames++;
            if (this.victoryFrames > CONFIG.VICTORY_DISPLAY_FRAMES) { 
                this.finished = true;
            }
            return;
        }

        if (!this.teams || this.teams.length === 0) return;

        const aliveTeams = this.teams.filter(team => {
            const hasBuildings = this.buildings.some(b => b.team === team);
            const hasSoldiers = this.soldiers.some(s => s.team === team);
            return hasBuildings || hasSoldiers;
        });

        if (aliveTeams.length < this.teams.length) {
            if (aliveTeams.length === 1) {
                this.victory = aliveTeams[0];
            } else if (aliveTeams.length === 0) {
                this.victory = "NONE";
            } else {
                this.victory = "MULTIPLE"; // Should not happen in standard elimination
            }
            
            this.events.push({ type: 'VICTORY', winner: this.victory });

            if (CONFIG.FAST_FINISH) {
                this.finished = true;
            }
        }
    }

    isPathBlocked(p1, p2) {
        const key = `${Math.round(p1.x)},${Math.round(p1.y)}-${Math.round(p2.x)},${Math.round(p2.y)}`;
        if (this.pathCache.has(key)) return this.pathCache.get(key);

        let blocked = false;
        if (this.obstacles) {
            for (const obs of this.obstacles) {
                if (this.lineIntersectsRect(p1.x, p1.y, p2.x, p2.y, obs.x, obs.y, obs.w, obs.h)) {
                    blocked = true;
                    break;
                }
            }
        }
        
        this.pathCache.set(key, blocked);
        return blocked;
    }

    lineIntersectsRect(x1, y1, x2, y2, rx, ry, rw, rh) {
        // Optimization: AABB check first
        const minX = Math.min(x1, x2), maxX = Math.max(x1, x2);
        const minY = Math.min(y1, y2), maxY = Math.max(y1, y2);
        
        if (maxX < rx || minX > rx + rw || maxY < ry || minY > ry + rh) return false;

        const left = this.lineIntersectsLine(x1, y1, x2, y2, rx, ry, rx, ry + rh);
        if (left) return true;
        const right = this.lineIntersectsLine(x1, y1, x2, y2, rx + rw, ry, rx + rw, ry + rh);
        if (right) return true;
        const top = this.lineIntersectsLine(x1, y1, x2, y2, rx, ry, rx + rw, ry);
        if (top) return true;
        const bottom = this.lineIntersectsLine(x1, y1, x2, y2, rx, ry + rh, rx + rw, ry + rh);
        return bottom;
    }

    lineIntersectsLine(x1, y1, x2, y2, x3, y3, x4, y4) {
        const den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1);
        if (den === 0) return false;
        const uA = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den;
        const uB = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den;
        return (uA >= 0 && uA <= 1 && uB >= 0 && uB <= 1);
    }
}
