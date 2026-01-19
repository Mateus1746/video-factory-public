const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const express = require('express');
const { spawn } = require('child_process');

const app = express();
app.use(express.static(__dirname));

async function renderVideo(file, type, port) {
    const mapName = path.basename(file, path.extname(file));
    const finalPath = path.join(__dirname, `preview_${mapName}.mp4`);
    
    console.log(`🚀 [PREVIEW] Iniciando Captura Rápida (480p 30fps): ${file}`);
    
    const browser = await puppeteer.launch({
        executablePath: '/usr/bin/google-chrome',
        headless: "new",
        args: [
            '--no-sandbox', 
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu'
        ]
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1080, height: 1920 });

    // Espelha logs do browser para o terminal de debug
    page.on('console', msg => {
        if (msg.type() === 'log') process.stdout.write(`\n[BROWSER] ${msg.text()}\n`);
    });

    let url;
    if (type === 'JSON') {
        url = `http://localhost:${port}/index.html?map=${file}`;
    } else {
        url = `http://localhost:${port}/html_maps/${file}`;
    }

    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 90000 });
    
    // Adiciona classe rendering para garantir escala 1:1
    await page.evaluate(() => {
        document.body.classList.add('rendering');
    });
    
    // Espera o gameInstance estar pronto manualmente em vez de confiar no networkidle
    await page.waitForFunction(() => window.gameInstance && window.gameInstance.isReady, { timeout: 60000 });

    await page.evaluate(() => {
        window.MANUAL_STEPPING = true;
        // Tenta inicializar o audio se possível
        if (window.gameInstance && window.gameInstance.audio) {
            window.gameInstance.audio.init();
            window.gameInstance.audio.resume();
        }
        window.dispatchEvent(new KeyboardEvent('keydown', { key: ' ' }));
    });

    const audioPath = path.join(__dirname, 'assets', 'audio', 'battle_ambiance.mp3');
    const hasAudio = fs.existsSync(audioPath);
    
    const ffmpegArgs = [
        '-y',
        '-f', 'image2pipe',
        '-vcodec', 'mjpeg',
        '-i', '-'
    ];

    if (hasAudio) {
        console.log(`🎵 Adicionando trilha sonora: ${audioPath}`);
        ffmpegArgs.push('-stream_loop', '-1', '-i', audioPath);
        // Aplica filtro de volume na trilha de fundo para não abafar tudo (e reduzir o ruído de fundo)
        ffmpegArgs.push('-filter_complex', '[1:a]volume=0.2[bg];[0:v]copy[v]', '-map', '[v]', '-map', '[bg]');
        ffmpegArgs.push('-shortest');
    }

    ffmpegArgs.push(
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-pix_fmt', 'yuv420p',
        '-r', '30',
        '-aspect', '9:16',
        finalPath
    );

    const ffmpeg = spawn('ffmpeg', ffmpegArgs);

    console.log("Gerando rascunho em tempo real...");

    let finished = false;
    let frameCount = 0;
    const maxFrames = 5400; 

    const audioEvents = [];

    while (!finished && frameCount < maxFrames) {
        const result = await page.evaluate(() => {
            if (!window.gameInstance) return { error: "No game instance" };
            
            // Avança 2 frames de lógica por frame de vídeo (Simulação 1:1 em 30fps)
            if (window.nextFrame) {
                window.nextFrame();
                window.nextFrame();
            }

            const events = window.gameInstance.simulation.events || [];
            
            return {
                finished: (window.gameInstance.simulation && window.gameInstance.simulation.finished) || false,
                soldiers: window.gameInstance.soldiers.length,
                victory: window.gameInstance.victory,
                events: events.map(e => ({ type: e.type }))
            };
        });

        if (result.error) {
            console.error("Erro fatal no browser:", result.error);
            break;
        }

        // Registra eventos para o mixer de áudio
        if (result.events && result.events.length > 0) {
            result.events.forEach(e => {
                audioEvents.push({ type: e.type, frame: frameCount });
            });
        }

        const screenshot = await page.screenshot({ type: 'jpeg', quality: 40 });
        ffmpeg.stdin.write(screenshot);

        finished = result.finished;
        frameCount++;
        
        if (frameCount % 30 === 0 || finished) {
            const status = result.victory ? `VENCEU (${result.victory})` : 'BATALHANDO';
            const msg = `\rFrame: ${frameCount}/${maxFrames} | Unidades: ${result.soldiers} | Status: ${status}`;
            process.stdout.write(msg.padEnd(80));
        }
    }

    process.stdout.write("\n");
    console.log("🏁 Simulação finalizada. Finalizando arquivo de vídeo...");
    
    // Configura o listener antes de fechar o pipe
    const ffmpegDone = new Promise(resolve => {
        ffmpeg.on('close', (code) => {
            console.log(`🎥 FFmpeg finalizado (código ${code})`);
            resolve();
        });
    });

    ffmpeg.stdin.end();
    
    // Salva os eventos de áudio para o mixer
    const eventsPath = path.join(__dirname, 'audio_events.json');
    fs.writeFileSync(eventsPath, JSON.stringify(audioEvents));

    console.log("📦 Fechando navegador...");
    await browser.close();
    
    await ffmpegDone;

    console.log("🎵 Sincronizando SFX com o vídeo...");
    try {
        const mixerScript = path.join(__dirname, 'mix_sfx.py');
        await new Promise((resolve, reject) => {
            const py = spawn('python3', [mixerScript, eventsPath, finalPath]);
            py.on('close', (code) => code === 0 ? resolve() : reject(`Mixer falhou com código ${code}`));
        });
        console.log("✅ Áudio sincronizado com sucesso!");
    } catch (e) {
        console.error("❌ Erro na mixagem de áudio:", e);
    }

    console.log(`\n✨ SUCESSO! Preview disponível em:`);
    console.log(`📁 ${finalPath}`);
}

async function main() {
    const server = app.listen(0, async () => {
        const port = server.address().port;
        const targetMap = process.argv[2] || 'map1.html';
        
        try {
            if (targetMap.endsWith('.json')) {
                await renderVideo(targetMap, 'JSON', port);
            } else {
                await renderVideo(targetMap, 'HTML', port);
            }
        } finally {
            server.close();
        }
    });
}

main();