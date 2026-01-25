// Default Configuration
const DEFAULT_CONFIG = {
    SCREEN_WIDTH: 1080,
    SCREEN_HEIGHT: 1920,
    FPS: 60,
    DURATION: 180,

    COLORS: {
        BG: "#0d1117",
        PLAYER: "#00ffff",
        ENEMY: "#ff00ff",
        NEUTRAL: "#4a4d52",
        WHITE: "#ffffff",
        GRID: "#1f2937",
        PATH: "rgba(255, 255, 255, 0.05)"
    },

    SOLDIER: {
        SPEED: 4.5, 
        RADIUS: 12,
        SPAWN_INTERVAL: 30,
        SEND_PERCENT: 0.8,
        SEND_DELAY: 5
    },

    BUILDING: {
        RADIUS: 120,
        GLOW_RADIUS: 60,
        MAX_COUNT: 200
    },

    AI: {
        COOLDOWN: 45,
        ERROR_CHANCE: 0.05, 
        MIN_ATTACK_COUNT: 20,
        TARGET_DIST_WEIGHT: 0.2,
        TARGET_COUNT_WEIGHT: 0.8,
        NEUTRAL_MULTIPLIER: 1.2
    },
    
    VICTORY_DISPLAY_FRAMES: 120,
    FAST_FINISH: false,

    // Dynamic Visuals
    THEME: "NEON", 
    NAMES: { player: "BLUE", enemy: "RED" }
};

// Merge with Injected Config (from Puppeteer/Server)
const INJECTED = (typeof window !== 'undefined' && window.GAME_CONFIG) ? window.GAME_CONFIG : {};

export const CONFIG = {
    ...DEFAULT_CONFIG,
    ...INJECTED,
    // Deep merge helper could be added here if needed for nested objects, 
    // but for top-level overwrite (WIDTH, FPS) this is sufficient.
};

// Recalculate derived constants if FPS changes
if (INJECTED.FPS && INJECTED.FPS !== 60) {
    const scale = 60 / INJECTED.FPS; // If 30fps, scale is 2.0 (move 2x per frame to keep speed)
    // NOTE: Simpler approach for this codebase -> Physics is frame-based. 
    // If we drop FPS, visual speed drops unless we scale speeds.
    // Ideally, speeds should be multiplied by scale.
    CONFIG.SOLDIER.SPEED *= scale;
    // Delays are in frames, so they should be reduced (fewer frames = same time)
    CONFIG.SOLDIER.SPAWN_INTERVAL /= scale; 
    CONFIG.SOLDIER.SEND_DELAY /= scale;
    CONFIG.AI.COOLDOWN /= scale;
    CONFIG.VICTORY_DISPLAY_FRAMES /= scale;
}

if (typeof window !== 'undefined') {
    window.CONFIG = CONFIG;
}