class SFXManager {
    constructor() {
        this.ctx = null;
        this.initialized = false;
    }

    init() {
        if (!this.initialized) {
            this.ctx = new (window.AudioContext || window.webkitAudioContext)();
            this.initialized = true;
        }
        if (this.ctx && this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    // ── Universal play dispatcher ──────────────────────────
    play(name) {
        try {
            this.init();
            switch (name) {
                case 'success': return this.playCorrect();
                case 'error': return this.playWrong();
                case 'xp': return this.playXpGain();
                case 'levelup': return this.playLevelUp();
                case 'wiki_sync': return this.playWikiSync();
                default: return;
            }
        } catch (e) {
            // Silently fail – audio is non-critical
        }
    }

    // ── Quest SFX ─────────────────────────────────────────
    playCorrect() {
        if (!this.ctx) return;
        // Ascending ping (C5 → E5)
        [523.25, 659.25].forEach((freq, i) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            const t = this.ctx.currentTime + i * 0.1;
            osc.type = 'sine';
            osc.frequency.value = freq;
            gain.gain.setValueAtTime(0, t);
            gain.gain.linearRampToValueAtTime(0.25, t + 0.02);
            gain.gain.exponentialRampToValueAtTime(0.001, t + 0.3);
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start(t);
            osc.stop(t + 0.35);
        });
    }

    playWrong() {
        if (!this.ctx) return;
        // Low buzz (descending)
        [220, 180].forEach((freq, i) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            const t = this.ctx.currentTime + i * 0.08;
            osc.type = 'sawtooth';
            osc.frequency.value = freq;
            gain.gain.setValueAtTime(0, t);
            gain.gain.linearRampToValueAtTime(0.15, t + 0.02);
            gain.gain.exponentialRampToValueAtTime(0.001, t + 0.25);
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start(t);
            osc.stop(t + 0.3);
        });
    }

    // ── Legacy SFX ────────────────────────────────────────
    playXpGain() {
        if (!this.ctx) return;
        const osc = this.ctx.createOscillator();
        const gainNode = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(1760, this.ctx.currentTime + 0.1);
        gainNode.gain.setValueAtTime(0, this.ctx.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.3, this.ctx.currentTime + 0.02);
        gainNode.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.5);
        osc.connect(gainNode);
        gainNode.connect(this.ctx.destination);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.5);
    }

    playLevelUp() {
        if (!this.ctx) return;
        const notes = [523.25, 659.25, 783.99, 1046.50];
        let startTime = this.ctx.currentTime;
        notes.forEach((freq) => {
            const osc = this.ctx.createOscillator();
            const gainNode = this.ctx.createGain();
            osc.type = 'triangle';
            osc.frequency.value = freq;
            gainNode.gain.setValueAtTime(0, startTime);
            gainNode.gain.linearRampToValueAtTime(0.2, startTime + 0.05);
            gainNode.gain.exponentialRampToValueAtTime(0.001, startTime + 0.3);
            osc.connect(gainNode);
            gainNode.connect(this.ctx.destination);
            osc.start(startTime);
            osc.stop(startTime + 0.3);
            startTime += 0.12;
        });
    }

    playWikiSync() {
        if (!this.ctx) return;
        const bufferSize = this.ctx.sampleRate * 0.5;
        const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const data = buffer.getChannelData(0);
        let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
        for (let i = 0; i < bufferSize; i++) {
            const white = Math.random() * 2 - 1;
            b0 = 0.99886 * b0 + white * 0.0555179; b1 = 0.99332 * b1 + white * 0.0750759;
            b2 = 0.96900 * b2 + white * 0.1538520; b3 = 0.86650 * b3 + white * 0.3104856;
            b4 = 0.55000 * b4 + white * 0.5329522; b5 = -0.7616 * b5 - white * 0.0168980;
            data[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.11;
            b6 = white * 0.115926;
        }
        const noiseSource = this.ctx.createBufferSource();
        noiseSource.buffer = buffer;
        const filter = this.ctx.createBiquadFilter();
        filter.type = 'highpass';
        filter.frequency.value = 4000;
        const gainNode = this.ctx.createGain();
        gainNode.gain.setValueAtTime(0.3, this.ctx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.4);
        noiseSource.connect(filter);
        filter.connect(gainNode);
        gainNode.connect(this.ctx.destination);
        noiseSource.start();
        noiseSource.stop(this.ctx.currentTime + 0.5);
    }
}

// Singleton export
export const sfx = new SFXManager();
