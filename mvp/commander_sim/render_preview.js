const { spawn } = require('child_process');
const path = require('path');

const targetMap = process.argv[2] || 'map1.html';
const script = path.join(__dirname, 'render_video.js');

console.log(`🎬 Iniciando Preview Rápido para: ${targetMap}`);

const child = spawn('node', [script, targetMap], { stdio: 'inherit' });

child.on('close', (code) => {
    console.log(`Processo finalizado com código ${code}`);
});
