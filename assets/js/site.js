(() => {
const soundButton = document.querySelector('[data-sound-toggle]');
const yearNodes = document.querySelectorAll('[data-year]');
const pingTargets = document.querySelectorAll('.ping-target, .button, .icon-button, .nav-links a');
yearNodes.forEach((node) => {
node.textContent = new Date().getFullYear();
});
const SOUND_KEY = 'ethereonlabs-sound-enabled';
let soundEnabled = localStorage.getItem(SOUND_KEY) === 'true';
let audioContext = null;

// === ENTRY SEQUENCING (NEW) ===
document.body.classList.add('ethereon-entry-active');

setTimeout(() => {
  document.body.classList.add('ethereon-field-awake');
}, 2800);

setTimeout(() => {
  document.body.classList.remove('ethereon-entry-pending');
  document.body.classList.add('ethereon-entry-complete');
}, 8500);

const injectBrandSigilStyles = () => {
if (document.getElementById('ethereonlabs-brand-sigil-style')) return;
const style = document.createElement('style');
style.id = 'ethereonlabs-brand-sigil-style';
style.textContent = `
.brand-mark {
width: 46px;
height: 46px;
border-radius: 14px;
border: 1px solid rgba(160, 188, 255, 0.28);
background: linear-gradient(135deg, rgba(7, 10, 22, 0.98), rgba(18, 26, 48, 0.9));
box-shadow: inset 0 0 20px rgba(138, 164, 255, 0.16), 0 0 18px rgba(138, 164, 255, 0.10);
position: relative;
display: inline-flex;
align-items: center;
justify-content: center;
overflow: hidden;
padding: 0;
flex: 0 0 auto;
}
.brand-mark::before,
.brand-mark::after {
content: none !important;
display: none !important;
}
.brand-mark > svg {
display: block;
width: 100%;
height: 100%;
}
`;
document.head.appendChild(style);
};

const injectBrandSigil = () => {
const brandMarks = document.querySelectorAll('.brand-mark');
if (!brandMarks.length) return;
const sigilMarkup = `<svg viewBox="0 0 52 52"><text x="26" y="32" text-anchor="middle" font-size="16" fill="white">Ψ</text></svg>`;
brandMarks.forEach((node) => {
if (node.dataset.sigilInjected === 'true') return;
node.innerHTML = sigilMarkup;
node.dataset.sigilInjected = 'true';
});
};

const FREQ = {
presence: 432,
transformation: 528,
higher_awareness: 963,
};

const syncSoundLabel = () => {
if (!soundButton) return;
soundButton.setAttribute('aria-pressed', String(soundEnabled));
soundButton.innerHTML = soundEnabled ? '✦' : '○';
};

const ensureAudio = async () => {
if (!audioContext) {
const AudioCtor = window.AudioContext || window.webkitAudioContext;
if (!AudioCtor) return null;
audioContext = new AudioCtor();
}
if (audioContext.state === 'suspended') {
try { await audioContext.resume(); } catch { return null; }
}
return audioContext;
};

const ping = async (freq = FREQ.presence, duration = 0.06) => {
if (!soundEnabled) return;
const ctx = await ensureAudio();
if (!ctx) return;
const osc = ctx.createOscillator();
const gain = ctx.createGain();
const now = ctx.currentTime;
osc.frequency.setValueAtTime(freq, now);
gain.gain.setValueAtTime(0.0001, now);
gain.gain.linearRampToValueAtTime(0.03, now + 0.01);
gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
osc.connect(gain);
gain.connect(ctx.destination);
osc.start(now);
osc.stop(now + duration);
};

injectBrandSigilStyles();
injectBrandSigil();
syncSoundLabel();

if (soundButton) {
soundButton.addEventListener('click', async () => {
soundEnabled = !soundEnabled;
localStorage.setItem(SOUND_KEY, String(soundEnabled));
syncSoundLabel();
await ping();
});
}

pingTargets.forEach((node) => {
node.addEventListener('mouseenter', () => ping());
node.addEventListener('click', () => ping(FREQ.transformation));
});
})();