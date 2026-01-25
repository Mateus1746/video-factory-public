import { CONFIG } from './Config.js';
import { Geometry } from './Geometry.js';

export class MapGenerator {
    constructor() {
        this.width = CONFIG.SCREEN_WIDTH;
        this.height = CONFIG.SCREEN_HEIGHT;
        this.padding = 150; // Keep away from edges
    }

    generate(type = 'SYMMETRIC') {
        const buildings = [];
        const obstacles = [];
        
        // 1. Setup Players (Top vs Bottom) - Safer distance from edge
        const p1Y = this.padding + 150;
        const p2Y = this.height - this.padding - 150;
        const centerX = this.width / 2;

        buildings.push({ x: centerX, y: p1Y, team: 'PLAYER', count: 10, type: 'FACTORY' });
        buildings.push({ x: centerX, y: p2Y, team: 'ENEMY', count: 10, type: 'FACTORY' });

        // 2. Generate Neutral Clusters with Radial Symmetry
        const numClusters = 4 + Math.floor(Math.random() * 4); // 4 to 7 pairs
        const minDistance = 320; // Increased from 250 to prevent visual clutter

        let attempts = 0;
        let added = 0;

        while (added < numClusters && attempts < 100) {
            attempts++;
            
            // Random position in the top half (minus center buffer)
            const x = this.padding + Math.random() * (this.width - this.padding * 2);
            const y = this.padding + 200 + Math.random() * ((this.height / 2) - 300);

            const mirrorX = this.width - x; 
            const mirrorY = this.height - y;

            // 1. Check Collision with existing
            if (this.isTooClose(x, y, buildings, minDistance)) continue;
            if (this.isTooClose(mirrorX, mirrorY, buildings, minDistance)) continue;

            // 2. Check Self-Collision (if near center)
            if (Geometry.distanceSq(x, y, mirrorX, mirrorY) < minDistance * minDistance) continue;

            const type = Math.random() > 0.8 ? 'BUNKER' : (Math.random() > 0.8 ? 'FACTORY' : 'NORMAL');
            const count = 10 + Math.floor(Math.random() * 40);

            // Add Pair
            buildings.push({ x, y, team: 'NEUTRAL', count, type });
            buildings.push({ x: mirrorX, y: mirrorY, team: 'NEUTRAL', count, type });
            added++;
        }

        // 3. Center Contest (The "Hot Zone")
        // Ensure center isn't blocked by previous random spawns (though logic above should prevent it)
        if (!this.isTooClose(centerX, this.height / 2, buildings, minDistance)) {
            const centerCount = 50;
            buildings.push({ x: centerX, y: this.height / 2, team: 'NEUTRAL', count: centerCount, type: 'BUNKER' });
        }

        return { buildings, obstacles };
    }

    isTooClose(x, y, buildings, threshold) {
        const threshSq = threshold * threshold;
        for (let b of buildings) {
            if (Geometry.distanceSq(x, y, b.x, b.y) < threshSq) return true;
        }
        return false;
    }
}
