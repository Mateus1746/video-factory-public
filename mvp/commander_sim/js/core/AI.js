import { CONFIG } from './Config.js';

export class AIAgent {
    constructor(team) {
        this.team = team;
        this.frameCounter = 0;
    }

    // Returns a command object or null
    update(buildings, isPathBlockedFn) {
        this.frameCounter++;
        if (this.frameCounter < CONFIG.AI.COOLDOWN) return null;

        let myBuildings = buildings.filter(b => b.team === this.team && b.count > CONFIG.AI.MIN_ATTACK_COUNT);
        if (myBuildings.length === 0) return null;

        let targets = buildings.filter(b => b.team !== this.team);
        if (targets.length === 0) return null;

        // Simple random attacker selection
        let attacker = myBuildings[Math.floor(Math.random() * myBuildings.length)];
        
        // Filter valid targets based on path blocking
        let validTargets = targets.filter(t => !isPathBlockedFn(attacker, t));

        if (validTargets.length === 0) return null;
        
        let target = this.selectTarget(validTargets, attacker);

        if (target) {
            this.frameCounter = 0;
            return { from: attacker, to: target };
        }
        return null;
    }

    selectTarget(targets, attacker) {
        let scoredTargets = targets.map(t => {
            let dx = t.x - attacker.x;
            let dy = t.y - attacker.y;
            let dist = Math.sqrt(dx * dx + dy * dy);
            
            let teamMultiplier = (t.team === 'NEUTRAL') ? CONFIG.AI.NEUTRAL_MULTIPLIER : 1.0;
            
            // Score calculation: Lower distance is better, Lower count is better (usually), but here count is +weight?
            // Original code: (dist * 0.2 + count * 0.8). 
            // Wait, usually AI wants to attack weak targets (low count) and close targets (low dist).
            // If the formula is (dist * W + count * W), then HIGHER score is "worse" target?
            // Original sorting: `scoredTargets.sort((a, b) => a.score - b.score);` -> Ascending. Smallest score first.
            // So yes, minimizing Distance and minimizing Count.
            
            let score = (dist * CONFIG.AI.TARGET_DIST_WEIGHT + t.count * CONFIG.AI.TARGET_COUNT_WEIGHT) * teamMultiplier;
            return { score, target: t };
        });

        scoredTargets.sort((a, b) => a.score - b.score);
        
        // Add some randomness so AI isn't perfectly predictable
        let idx = 0;
        if (Math.random() > (1 - CONFIG.AI.ERROR_CHANCE) && scoredTargets.length > 2) {
            idx = Math.floor(Math.random() * Math.min(3, scoredTargets.length));
        }
        
        return scoredTargets[idx].target;
    }
}
