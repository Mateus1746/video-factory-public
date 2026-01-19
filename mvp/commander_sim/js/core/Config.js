export const CONFIG = {
    SCREEN_WIDTH: 1080,
    SCREEN_HEIGHT: 1920,
    FPS: 60,

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
    FAST_FINISH: false
};

// Backwards compatibility for inline HTML scripts if necessary
if (typeof window !== 'undefined') {
    window.CONFIG = CONFIG;
}
