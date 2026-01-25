export const THEMES = {
    NEON: {
        name: "NEON CITY",
        bg: "#0d1117",
        grid: "#1f2937",
        player: "#00ffff",
        enemy: "#ff1a1a", // Red instead of Purple
        neutral: "#4a4d52",
        particles: "spark",
        bloom: true
    },
    MAGMA: {
        name: "MAGMA CORE",
        bg: "#1a0505",
        grid: "#4a1010",
        player: "#ffaa00", // Orange/Gold
        enemy: "#ff0000", // Deep Red
        neutral: "#552222",
        particles: "ember", // Need to impl in particles if specific
        bloom: true
    },
    MATRIX: {
        name: "CYBER SPACE",
        bg: "#000000",
        grid: "#003300",
        player: "#00ff00",
        enemy: "#ff0000", // Glitch Red
        neutral: "#005500",
        particles: "binary", // Text particles 0/1
        bloom: false // Sharp look
    },
    FROST: {
        name: "FROST BITE",
        bg: "#05101a",
        grid: "#102a3a",
        player: "#aaddff", // Ice Blue
        enemy: "#004488", // Deep Blue
        neutral: "#2a4a5a",
        particles: "snow",
        bloom: true
    }
};

export class ThemeManager {
    static getRandomTheme() {
        const keys = Object.keys(THEMES);
        const randomKey = keys[Math.floor(Math.random() * keys.length)];
        return THEMES[randomKey];
    }

    static getTheme(name) {
        return THEMES[name] || THEMES.NEON;
    }

    static generateEmpireNames() {
        const prefixes = ["Cyber", "Iron", "Neon", "Shadow", "Solar", "Void", "Quantum", "Apex"];
        const suffixes = ["Legion", "Rebels", "Empire", "Corp", "Dynasty", "Horde", "Vanguard", "Sect"];
        
        const n1 = `${this.pick(prefixes)} ${this.pick(suffixes)}`;
        let n2 = `${this.pick(prefixes)} ${this.pick(suffixes)}`;
        while (n1 === n2) n2 = `${this.pick(prefixes)} ${this.pick(suffixes)}`;
        
        return { player: n1, enemy: n2 };
    }

    static pick(arr) {
        return arr[Math.floor(Math.random() * arr.length)];
    }
}
