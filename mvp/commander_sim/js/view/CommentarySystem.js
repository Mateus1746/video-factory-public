import { CONFIG } from '../core/Config.js';
import { ENTITY_EVENTS } from '../core/Entities.js';

export class CommentarySystem {
    constructor(renderer) {
        this.renderer = renderer;
        this.lastCommentTime = 0;
        this.cooldown = 60; // Start ready faster (1s)
        
        this.phrases = {
            ATTACK: ["CHARGE!", "PUSH!", "GO GO!", "ATTACK!", "RUSH B!", "SEND IT!"],
            DEFEND: ["HOLD!", "DEFEND!", "NOT TODAY!", "BLOCK!", "WALL!", "NO WAY!"],
            CAPTURE: ["MINE!", "SECURED!", "EZ!", "GOTCHA!", "POWER UP!", "TAKEN!"],
            LOSE: ["OUCH!", "NOOO!", "RETREAT!", "HELP!", "RIP", "MY BASE!"]
        };
    }

    update(simulation) {
        this.lastCommentTime++;
        
        if (simulation.events.length === 0) return;

        // 1. Scan for High Priority Events (Capture/Victory)
        // These bypass cooldown restrictions partly
        const captureEvent = simulation.events.find(e => e.type === 'CAPTURE');
        if (captureEvent) {
            // Force comment if it's been at least 30 frames (0.5s) since last to avoid total spam
            if (this.lastCommentTime > 30) {
                this.spawnComment(captureEvent.x, captureEvent.y - 60, 'CAPTURE', CONFIG.COLORS[captureEvent.team]);
                return;
            }
        }

        // 2. Standard Commentary (Spawns/Combat) - Respects full cooldown
        if (this.lastCommentTime < this.cooldown) return;

        // Look for spawns
        const spawnEvent = simulation.events.find(e => e.type === 'SPAWN');
        if (spawnEvent && Math.random() < 0.20) { // Increased to 20% chance
            this.spawnComment(spawnEvent.x, spawnEvent.y - 50, 'ATTACK', CONFIG.COLORS.WHITE);
        }
    }

    spawnComment(x, y, type, color) {
        const list = this.phrases[type];
        if (!list) return;
        
        const text = list[Math.floor(Math.random() * list.length)];
        this.renderer.particles.emitText(x, y, text, color);
        
        this.lastCommentTime = 0;
        this.cooldown = 90 + Math.random() * 60; // 1.5s to 2.5s gap
    }
}
