import { CONFIG } from './Config.js';
import { Building, Soldier, ENTITY_EVENTS } from './Entities.js';
import { AIAgent } from './AI.js';
import { Geometry } from './Geometry.js';

export class Simulation {
    constructor() {
        this.resetState();
        
        // Cache for path blocking to optimize performance
        this.pathCache = new Map();
        this.obstacles = [];
        this.mapData = null;
        this.frameCounter = 0; // Global simulation clock
    }

    resetState() {
        this.buildings = [];
        this.soldiers = [];
        this.scheduledSoldiers = [];
        this.ais = [];
        this.teams = [];
        this.victory = null;
        this.victoryFrames = 0;
        this.finished = false;
        this.events = [];
        this.frameCounter = 0;
    }

    loadMap(mapData) {
        this.mapData = mapData;
        this.resetState();
        this.pathCache.clear();

        if (mapData.buildings) {
            this.buildings = mapData.buildings.map(b => 
                new Building(b.x, b.y, b.team.toUpperCase(), b.count, b.type)
            );
        }

        if (mapData.obstacles) {
            this.obstacles = mapData.obstacles;
        }

        // Identify unique teams (excluding NEUTRAL)
        this.teams = [...new Set(this.buildings.map(b => b.team))].filter(t => t !== 'NEUTRAL');
        
        // Initialize AI for each team
        this.ais = this.teams.map(team => new AIAgent(team));
    }

    /**
     * Main Simulation Loop Tick
     * Orchestrates the update order: Buildings -> Spawns -> Soldiers -> AI -> Victory
     */
    update() {
        if (this.finished) return;

        this.frameCounter++;
        this.events = []; 

        // Boredom Detector: After 60s, increase spawn rates exponentially
        let intensityMultiplier = 1.0;
        if (this.frameCounter > 3600) {
            // Increase by 2% every second after 60s
            const extraSeconds = (this.frameCounter - 3600) / 60;
            intensityMultiplier = 1.0 + (extraSeconds * 0.05);
        }

        this._updateBuildings(intensityMultiplier);
        this._processScheduledSpawns();
        this._updateSoldiers();
        this._updateAI();
        this._checkVictoryCondition();
    }

    _updateBuildings(intensity) {
        this.buildings.forEach(b => b.update(intensity));
    }

    _processScheduledSpawns() {
        if (this.scheduledSoldiers.length === 0) return;

        // Iterate backwards to allow safe removal
        for (let i = this.scheduledSoldiers.length - 1; i >= 0; i--) {
            let s = this.scheduledSoldiers[i];
            s.framesLeft--;
            
            if (s.framesLeft <= 0) {
                this.soldiers.push(new Soldier(s.x, s.y, s.target, s.team));
                this.scheduledSoldiers.splice(i, 1);
            }
        }
    }

    _updateSoldiers() {
        for (let i = this.soldiers.length - 1; i >= 0; i--) {
            let s = this.soldiers[i];
            const eventCode = s.update();
            
            if (s.reached) {
                this.soldiers.splice(i, 1);
                this._handleSoldierArrival(s, eventCode);
            }
        }
    }

    _handleSoldierArrival(soldier, code) {
        if (code === ENTITY_EVENTS.SOLDIER_HIT) {
            this.events.push({
                type: 'HIT',
                x: soldier.target.x,
                y: soldier.target.y,
                team: soldier.team, 
                targetTeam: soldier.target.team
            });
        } else if (code === ENTITY_EVENTS.BUILDING_CAPTURED) {
            this.events.push({
                type: 'CAPTURE',
                x: soldier.target.x,
                y: soldier.target.y,
                team: soldier.team
            });
            // Clear path cache as strategic situation changed
            // (Optional, depends on if obstacles are dynamic. Static obstacles don't change)
             this.pathCache.clear(); 
        }
    }

    _updateAI() {
        this.ais.forEach(ai => {
            const cmd = ai.update(this.buildings, (a, b) => this.isPathBlocked(a, b));
            if (cmd) {
                this.sendTroops(cmd.from, cmd.to);
            }
        });
    }

    sendTroops(from, to) {
        if (this.isPathBlocked(from, to)) return;

        let amount = Math.floor(from.count * CONFIG.SOLDIER.SEND_PERCENT);
        from.count -= amount;

        this.events.push({ type: 'SPAWN', x: from.x, y: from.y });

        // Stagger spawn
        for (let i = 0; i < amount; i++) {
            this.scheduleSoldier(from.x, from.y, to, from.team, i * CONFIG.SOLDIER.SEND_DELAY);
        }
    }

    scheduleSoldier(x, y, target, team, frameDelay) {
        this.scheduledSoldiers.push({ x, y, target, team, framesLeft: frameDelay });
    }

    _checkVictoryCondition() {
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
                this.victory = "MULTIPLE"; // Rare case
            }
            
            this.events.push({ type: 'VICTORY', winner: this.victory });

            if (CONFIG.FAST_FINISH) {
                this.finished = true;
            }
        }
    }

    isPathBlocked(p1, p2) {
        // Cache key based on rounded coordinates to reduce precise float misses
        const key = `${Math.round(p1.x)},${Math.round(p1.y)}-${Math.round(p2.x)},${Math.round(p2.y)}`;
        
        if (this.pathCache.has(key)) {
            return this.pathCache.get(key);
        }

        let blocked = false;
        if (this.obstacles) {
            for (const obs of this.obstacles) {
                if (Geometry.lineIntersectsRect(p1.x, p1.y, p2.x, p2.y, obs.x, obs.y, obs.w, obs.h)) {
                    blocked = true;
                    break;
                }
            }
        }
        
        this.pathCache.set(key, blocked);
        return blocked;
    }
}
