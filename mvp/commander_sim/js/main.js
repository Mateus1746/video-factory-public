import { Game } from './Game.js';

// Entry point
window.addEventListener('load', () => {
    // Always instantiate Game. It handles MAP_DATA or URL loading internally.
    window.gameInstance = new Game();
});