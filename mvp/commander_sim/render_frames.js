const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const express = require('express');
const bodyParser = require('body-parser');

const PORT = 3000;
const app = express();

app.use(express.static(__dirname));
app.use(bodyParser.json({ limit: '10mb' }));

// Global Browser and Status Instance
let browser = null;
let serverInstance = null;
let renderStatus = {
    frameCount: 0,
    isRendering: false,
    currentMap: ""
};

async function initBrowser() {
    if (browser) return browser;
    console.log("🚀 Launching Persistent Browser...");
    browser = await puppeteer.launch({
        headless: "new",
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    });
    return browser;
}

async function renderMap(task) {
    if (!browser) await initBrowser();

    const { mapFile, type, outputDir, config } = task;
    const mapName = path.basename(mapFile, path.extname(mapFile));
    const targetDir = path.join(outputDir || __dirname, 'frames', mapName);
    
    renderStatus.isRendering = true;
    renderStatus.frameCount = 0;
    renderStatus.currentMap = mapName;

    // Config Defaults
    const width = config?.width || 1080;
    const height = config?.height || 1920;
    const fps = config?.fps || 60;
    const quality = config?.quality || 90; 
    const maxFrames = config?.maxFrames || (60 * fps); 

    // Clean/Create directory
    if (fs.existsSync(targetDir)) {
        fs.readdirSync(targetDir).forEach(f => fs.unlinkSync(path.join(targetDir, f)));
    } else {
        fs.mkdirSync(targetDir, { recursive: true });
    }

    const page = await browser.newPage();
    try {
        await page.setViewport({ width, height });

        const serverPort = serverInstance.address().port;
        let url;
        if (type === 'JSON') {
            url = `http://localhost:${serverPort}/index.html?map=${mapFile}`;
        } else {
            url = `http://localhost:${serverPort}/html_maps/${mapFile}`;
        }

        await page.evaluateOnNewDocument((cfg) => {
            window.GAME_CONFIG = {
                SCREEN_WIDTH: cfg.width,
                SCREEN_HEIGHT: cfg.height,
                FPS: cfg.fps,
                THEME: cfg.THEME,
                NAMES: cfg.NAMES
            };
            window.MANUAL_STEPPING = true; 
        }, { width, height, fps, THEME: config.THEME, NAMES: config.NAMES });

        await page.goto(url, { waitUntil: 'networkidle0' });

        await page.evaluate(() => {
            document.body.classList.add('rendering');
        });

        // Wait for Ready
        let isReady = false;
        for (let i = 0; i < 100; i++) {
            const state = await page.evaluate(() => {
                const g = window.gameInstance;
                return { exists: !!g, ready: g ? g.isReady : false };
            });
            if (state.exists && state.ready) {
                isReady = true;
                break;
            }
            await new Promise(r => setTimeout(r, 100));
        }

        if (!isReady) throw new Error("Game Engine timed out");

        // Render Loop
        let frameCount = 0;
        let finished = false;
        const audioEvents = [];
        
        // Thumbnail Logic
        let bestActionScore = -1;
        let bestFrameNumber = 0;

        while (!finished && frameCount < maxFrames) {
            const result = await page.evaluate(() => {
                if (!window.nextFrame) return { ready: false };
                window.nextFrame(); 
                
                const events = window.gameInstance.simulation.events || [];
                // Score based on dynamic elements
                const soldiersCount = window.gameInstance.simulation.soldiers.length;
                const particlesCount = window.gameInstance.renderer.particles.particles.length;
                const actionScore = soldiersCount + (particlesCount * 0.5);

                return {
                    ready: true,
                    finished: window.gameInstance.simulation.finished || false,
                    events: events.map(e => ({ type: e.type })),
                    actionScore: actionScore
                };
            });

            if (!result.ready) continue;

            // Track Best Action Frame
            if (result.actionScore > bestActionScore) {
                bestActionScore = result.actionScore;
                bestFrameNumber = frameCount;
            }

            const fileName = `frame_${frameCount.toString().padStart(5, '0')}.jpg`;
            const framePath = path.join(targetDir, fileName);
            await page.screenshot({ 
                path: framePath, 
                type: 'jpeg', 
                quality: quality 
            });

            if (result.events) {
                result.events.forEach(e => audioEvents.push({ type: e.type, frame: frameCount }));
            }

            finished = result.finished;
            frameCount++;
            renderStatus.frameCount = frameCount; 
        }

        // Save Thumbnail
        const bestFrameName = `frame_${bestFrameNumber.toString().padStart(5, '0')}.jpg`;
        const bestFramePath = path.join(targetDir, bestFrameName);
        const thumbPath = path.join(targetDir, 'thumbnail.jpg');
        if (fs.existsSync(bestFramePath)) {
            fs.copyFileSync(bestFramePath, thumbPath);
            console.log(`📸 Action Shot saved! Frame: ${bestFrameNumber} (Score: ${bestActionScore.toFixed(1)})`);
        }

        fs.writeFileSync(path.join(targetDir, 'events.json'), JSON.stringify(audioEvents, null, 2));
        
        return { success: true, frames: frameCount, outputDir: targetDir };

    } catch (e) {
        console.error("Render Error:", e);
        return { success: false, error: e.message };
    } finally {
        renderStatus.isRendering = false;
        await page.close();
    }
}

// API Routes
app.post('/render', async (req, res) => {
    const { mapFile, type, outputDir, config } = req.body;
    if (!mapFile) return res.status(400).json({ error: "Missing mapFile" });

    const result = await renderMap({ mapFile, type, outputDir, config });
    
    if (result.success) res.json(result);
    else res.status(500).json(result);
});

app.get('/progress', (req, res) => {
    res.json(renderStatus);
});

app.get('/health', (req, res) => res.send('OK'));

app.post('/shutdown', async (req, res) => {
    console.log("🛑 Shutdown requested via API");
    res.send('Shutting down...');
    if (browser) await browser.close();
    process.exit(0);
});

serverInstance = app.listen(PORT, async () => {
    console.log(`🌍 Render Server listening on port ${PORT}`);
    await initBrowser();
    console.log("✨ Browser Ready. Waiting for jobs...");
});

process.on('SIGTERM', async () => {
    if (browser) await browser.close();
    process.exit(0);
});
