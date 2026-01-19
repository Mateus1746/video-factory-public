export class SimulationCapturer {
    constructor(canvas, audioManager) {
        this.canvas = canvas;
        this.audioManager = audioManager;
        this.isCapturing = false;
        this.frameCount = 0;
    }

    start() {
        this.isCapturing = true;
        this.frameCount = 0;
        console.log("SIMULATION_CAPTURE_START");
    }

    async captureFrame(frameCount) {
        // Envia o frame atual como string base64 para o Puppeteer
        const dataUrl = this.canvas.toDataURL('image/png');
        window.onFrameCaptured(frameCount, dataUrl);
    }

    stop() {
        this.isCapturing = false;
        window.isSimulationFinished = true;
        console.log("SIMULATION_CAPTURE_END");
    }
}