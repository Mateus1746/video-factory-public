import { CONFIG } from './core/Config.js';
import { Simulation } from './core/Simulation.js';
import { Renderer } from './view/Renderer.js';
import { AudioController } from './view/Audio.js';
import { MapGenerator } from './core/MapGenerator.js';
import { CommentarySystem } from './view/CommentarySystem.js';

export class Game {
    constructor() {
        this.canvas = document.getElementById('gameCanvas') || document.querySelector('canvas');
        
        this.simulation = new Simulation();
        this.renderer = new Renderer(this.canvas); 
        this.audio = new AudioController();
        this.generator = new MapGenerator();
        this.commentary = new CommentarySystem(this.renderer);
        
        this.isReady = false;
        
        this.setupAudioInput();
        
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
        if (window.MAP_DATA) {
            this.simulation.loadMap(window.MAP_DATA);
            return;
        }

        const params = new URLSearchParams(window.location.search);
        const mapFile = params.get('map');

        if (!mapFile || mapFile === 'GENERATE') {
            console.log("🎲 Generating Procedural Map...");
            const data = this.generator.generate();
            this.simulation.loadMap(data);
            window.MAP_DATA = data;
            return;
        }

        if (mapFile) {
            try {
                let fetchPath = mapFile;
                if (!mapFile.includes('/')) fetchPath = `maps/${mapFile}`;

                const res = await fetch(fetchPath);
                if (!res.ok) throw new Error(`Failed to load ${fetchPath}`);
                const data = await res.json();
                this.simulation.loadMap(data);
                window.MAP_DATA = data; 
            } catch (e) {
                console.error("Map load error:", e);
            }
        }
    }

    step() {
        this.simulation.update();
        this.commentary.update(this.simulation);
        
        this.simulation.events.forEach(e => {
            this.renderer.handleEvent(e);
            this.audio.playEvent(e.type, e); 
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
