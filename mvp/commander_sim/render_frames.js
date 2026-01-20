const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const express = require('express');
const { execSync } = require('child_process');

const app = express();
app.use(express.static(__dirname));

async function renderSimulation(file, type, port) {
    const mapName = path.basename(file, path.extname(file));
    const outputDir = path.join(__dirname, 'frames', mapName);
    const finalPath = path.join(__dirname, `final_${mapName}.mp4`);
    
    if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });
    else {
        fs.readdirSync(outputDir).forEach(f => fs.unlinkSync(path.join(outputDir, f)));
    }

    console.log(`🎥 [FINAL] Iniciando Renderização de Alta Qualidade (1080p 60fps): ${file}`);
    console.log(`ℹ️  Isso pode demorar, pois estamos capturando cada frame individualmente.`);
    
    // Use Puppeteer's bundled Chromium by default
    console.log(`Using bundled Chromium...`);

    const browser = await puppeteer.launch({
        headless: "new",
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1080, height: 1920 });

    page.on('console', msg => console.log('BROWSER LOG:', msg.text()));
    page.on('pageerror', err => console.error('BROWSER ERROR:', err.message));
    page.on('requestfailed', request => console.error('BROWSER REQUEST FAILED:', request.url(), request.failure().errorText));

    let url;
    if (type === 'JSON') {
        url = `http://localhost:${port}/index.html?map=${file}`;
    } else {
        url = `http://localhost:${port}/html_maps/${file}`;
    }

    console.log(`Abrindo URL: ${url}`);
    await page.goto(url, { waitUntil: 'networkidle0' });

    await page.evaluate(() => {
        window.MANUAL_STEPPING = true;
        document.body.classList.add('rendering'); // Remove escalas de UI
    });

    // Esperar pelo sinal de pronto
    console.log("Aguardando inicialização do motor e dados do mapa...");
    let isReady = false;
    for (let i = 0; i < 60; i++) {
        const state = await page.evaluate(() => {
            const g = window.gameInstance;
            return {
                exists: !!g,
                ready: g ? g.isReady : false,
                buildings: g ? g.buildings.length : 0
            };
        });
        
        if (state.exists && state.ready && state.buildings > 0) {
            isReady = true;
            break;
        }
        
        if (i % 10 === 0) console.log(`⏳ Aguardando... (Game: ${state.exists}, Ready: ${state.ready}, Buildings: ${state.buildings})`);
        await new Promise(r => setTimeout(r, 500));
    }

    if (!isReady) {
        console.error("❌ Erro: Motor não inicializou a tempo.");
        await browser.close();
        process.exit(1); // Force failure
    }

    let frameCount = 0;
    let finished = false;
    const audioEvents = []; // [NEW] Accumulator for audio events
    
    console.log("Processando frames...");

    while (!finished && frameCount < 1800) { 
        const result = await page.evaluate(async () => {
            if (!window.gameInstance || !window.gameInstance.isReady) return { ready: false };
            
            // 1 passo de lógica por frame de vídeo (Tempo Real)
            if (window.nextFrame) window.nextFrame();

            // [NEW] Capture events
            const events = window.gameInstance.simulation.events || [];

            return {
                ready: true,
                victory: window.gameInstance.victory !== null,
                finished: window.gameInstance.simulation.finished || false,
                buildings: window.gameInstance.buildings.length,
                soldiers: window.gameInstance.soldiers.length,
                events: events.map(e => ({ type: e.type })) // [NEW] Send events to Node context
            };
        });

        if (!result.ready) {
            await new Promise(r => setTimeout(r, 100));
            continue;
        }

        // [NEW] Store events
        if (result.events && result.events.length > 0) {
            result.events.forEach(e => {
                audioEvents.push({ type: e.type, frame: frameCount });
            });
        }

        const fileName = `frame_${frameCount.toString().padStart(5, '0')}.png`;
        await page.screenshot({ path: path.join(outputDir, fileName), type: 'png' });

        finished = result.finished;

        frameCount++;
        if (frameCount % 100 === 0) console.log(`Frame: ${frameCount} | Tropas em campo: ${result.soldiers}`);
    }

    await browser.close();

    // [NEW] Save events.json
    console.log(`✅ Frames capturados (${frameCount}). Salvando eventos de áudio...`);
    fs.writeFileSync(path.join(outputDir, 'events.json'), JSON.stringify(audioEvents, null, 2));

    console.log(`✅ Renderização de frames concluída para: ${mapName}`);
    // FFmpeg compilation is now handled by the batch python script.
}

async function main() {
    const server = app.listen(0, async () => {
        const port = server.address().port;
        const targetMap = process.argv[2] || 'map1.html';
        try {
            if (targetMap.endsWith('.json')) {
                await renderSimulation(targetMap, 'JSON', port);
            } else {
                await renderSimulation(targetMap, 'HTML', port);
            }
        } finally {
            server.close();
        }
    });
}

main();
