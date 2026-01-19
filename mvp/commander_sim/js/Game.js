import { CONFIG } from './core/Config.js';
import { Simulation } from './core/Simulation.js';
import { Renderer } from './view/Renderer.js';
import { AudioController } from './view/Audio.js';

export class Game {
    constructor() {
        this.canvas = document.getElementById('gameCanvas') || document.querySelector('canvas');
        
        this.simulation = new Simulation();
        this.renderer = new Renderer(this.canvas);
        this.audio = new AudioController();
        
        this.isReady = false;
        
        // Setup initial interaction for Audio Context
        this.setupAudioInput();
        
        // Expose for external tools (Puppeteer)
        window.gameInstance = this;
        window.nextFrame = () => this.step();
        
        this.loadLevel().then(() => {
            this.isReady = true;
            console.log("GAME_ENGINE_READY");
            this.loop();
        });
    }

    setupAudioInput() {
        const resume = () => {
            this.audio.init();
            this.audio.resume();
            document.removeEventListener('click', resume);
            document.removeEventListener('keydown', resume);
        };
        document.addEventListener('click', resume);
        document.addEventListener('keydown', resume);
    }

    async loadLevel() {
        // 1. Check for global data (HTML maps)
        if (window.MAP_DATA) {
            this.simulation.loadMap(window.MAP_DATA);
            return;
        }

        // 2. Check for URL parameter (JSON maps)
        const params = new URLSearchParams(window.location.search);
        const mapFile = params.get('map');

        if (mapFile) {
            try {
                // Adjust path: assume maps are in maps/ or relative root?
                // The server serves root. 'maps/level1.json'
                // If mapFile is just 'level1.json', we might need 'maps/level1.json'
                // But usually the param would be full path or we try both.
                // Let's assume the param includes the folder or we prepend 'maps/' if missing.
                let fetchPath = mapFile;
                if (!mapFile.includes('/')) fetchPath = `maps/${mapFile}`;

                const res = await fetch(fetchPath);
                if (!res.ok) throw new Error(`Failed to load ${fetchPath}`);
                const data = await res.json();
                this.simulation.loadMap(data);
                window.MAP_DATA = data; // Cache it
            } catch (e) {
                console.error("Map load error:", e);
            }
        } else {
            console.warn("No MAP_DATA and no 'map' param.");
        }
    }

    // Single step of logic + render
    step() {
        this.simulation.update();
        
        // Process events
        this.simulation.events.forEach(e => {
            this.renderer.handleEvent(e);
            this.audio.playEvent(e.type, e); // Audio maps types differently if needed
        });

        this.renderer.draw(this.simulation);
    }

    loop() {
        if (window.MANUAL_STEPPING) return;

        this.step();
        requestAnimationFrame(() => this.loop());
    }
    
    // Getters for Puppeteer compatibility
    get victory() { return this.simulation.victory; }
    get soldiers() { return this.simulation.soldiers; }
    get buildings() { return this.simulation.buildings; }
    get victoryFrames() { return this.simulation.victoryFrames; }
}
