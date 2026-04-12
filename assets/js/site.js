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
@media (max-width: 760px) {
.brand-mark {
width: 42px;
height: 42px;
border-radius: 13px;
}
}
`;
document.head.appendChild(style);
};
const injectBrandSigil = () => {
const brandMarks = document.querySelectorAll('.brand-mark');
if (!brandMarks.length) return;
const sigilMarkup = `
<svg class="brand-sigil" viewBox="0 0 52 52" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
<defs>
<radialGradient id="brandSigilCenter" cx="50%" cy="50%" r="50%">
<stop offset="0%" stop-color="#1c2545" />
<stop offset="100%" stop-color="#060913" />
</radialGradient>
<filter id="brandSigilGlow" x="-80%" y="-80%" width="260%" height="260%">
<feGaussianBlur in="SourceGraphic" stdDeviation="1.2" result="b" />
<feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
</filter>
<filter id="brandSigilArmGlow" x="-40%" y="-40%" width="180%" height="180%">
<feGaussianBlur in="SourceGraphic" stdDeviation="0.8" result="b" />
<feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
</filter>
<clipPath id="brandSigilClip"><rect x="1" y="1" width="50" height="50" rx="14" ry="14" /></clipPath>
<style>
.brand-sigil .sigil-ring-outer { animation: brandSpinCw 36s linear infinite; transform-origin: 26px 26px; }
.brand-sigil .sigil-ring-inner { animation: brandSpinCcw 22s linear infinite; transform-origin: 26px 26px; opacity: 0.85; }
.brand-sigil .sigil-triskelion { animation: brandSpinCw 120s linear infinite; transform-origin: 26px 26px; }
.brand-sigil .sigil-arm-1 { animation: brandBreathe 5s ease-in-out infinite; transform-origin: 26px 26px; }
.brand-sigil .sigil-arm-2 { animation: brandBreathe 5s ease-in-out infinite 1.66s; transform-origin: 26px 26px; }
.brand-sigil .sigil-arm-3 { animation: brandBreathe 5s ease-in-out infinite 3.33s; transform-origin: 26px 26px; }
.brand-sigil .sigil-inner { animation: brandSpinCcw 55s linear infinite; transform-origin: 26px 26px; opacity: 0.58; }
.brand-sigil .sigil-inner-1 { animation: brandBreatheInner 4s ease-in-out infinite; transform-origin: 26px 26px; }
.brand-sigil .sigil-inner-2 { animation: brandBreatheInner 4s ease-in-out infinite 1.33s; transform-origin: 26px 26px; }
.brand-sigil .sigil-inner-3 { animation: brandBreatheInner 4s ease-in-out infinite 2.66s; transform-origin: 26px 26px; }
.brand-sigil .sigil-orbit-a { animation: brandSpinCw 70s linear infinite; transform-origin: 26px 26px; opacity: 0.15; }
.brand-sigil .sigil-orbit-b { animation: brandSpinCcw 90s linear infinite; transform-origin: 26px 26px; opacity: 0.10; }
.brand-sigil .sigil-bloom { animation: brandPsiPulse 3.5s ease-in-out infinite; }
.brand-sigil .sigil-psi { animation: brandPsiGlow 3.5s ease-in-out infinite; }
@keyframes brandSpinCw { to { transform: rotate(360deg); } }
@keyframes brandSpinCcw { to { transform: rotate(-360deg); } }
@keyframes brandBreathe { 0%, 100% { opacity: 0.72; filter: drop-shadow(0 0 1px rgba(200, 218, 255, 0.18)); } 50% { opacity: 1; filter: drop-shadow(0 0 4px rgba(200, 218, 255, 0.48)); } }
@keyframes brandBreatheInner { 0%, 100% { opacity: 0.48; } 50% { opacity: 0.9; } }
@keyframes brandPsiPulse { 0%, 100% { opacity: 0.10; } 50% { opacity: 0.38; } }
@keyframes brandPsiGlow { 0%, 100% { opacity: 0.86; filter: drop-shadow(0 0 1px rgba(220, 235, 255, 0.25)); } 50% { opacity: 1; filter: drop-shadow(0 0 6px rgba(220, 235, 255, 0.95)); } }
</style>
</defs>
<rect x="1" y="1" width="50" height="50" rx="14" ry="14" fill="#07091a" stroke="rgba(138,164,255,0.14)" stroke-width="1.1" />
<g clip-path="url(#brandSigilClip)">
<g class="sigil-orbit-a"><ellipse cx="26" cy="26" rx="22" ry="12" fill="none" stroke="rgba(138,164,255,0.22)" stroke-width="0.6" /></g>
<g class="sigil-orbit-b"><ellipse cx="26" cy="26" rx="12" ry="22" fill="none" stroke="rgba(126,240,209,0.18)" stroke-width="0.6" /></g>
<g class="sigil-ring-outer"><circle cx="26" cy="26" r="21.5" fill="none" stroke="rgba(205,220,255,0.45)" stroke-width="0.75" stroke-dasharray="1.4 2.2" stroke-linecap="round" /></g>
<g class="sigil-ring-inner"><circle cx="26" cy="26" r="18.2" fill="none" stroke="rgba(126,240,209,0.54)" stroke-width="0.7" stroke-dasharray="1 1.8" stroke-linecap="round" /></g>
<g class="sigil-triskelion" filter="url(#brandSigilArmGlow)" transform="scale(0.1)">
<g class="sigil-arm-1"><path d="M 260 260 C 265 248, 272 240, 280 234 C 292 225, 306 224, 314 232 C 326 244, 322 262, 310 272 C 296 283, 278 280, 270 268 C 262 257, 264 244, 272 237 C 280 230, 292 232, 297 240 C 302 249, 298 260, 291 264 C 284 268, 276 264, 275 258 C 274 253, 278 249, 283 250 C 287 251, 288 256, 285 259" fill="none" stroke="rgba(210,225,255,0.9)" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" /></g>
<g class="sigil-arm-2"><path d="M 260 260 C 249 265, 239 270, 232 278 C 222 290, 221 305, 230 312 C 243 323, 261 317, 270 304 C 280 290, 276 272, 263 265 C 251 259, 238 263, 233 273 C 228 283, 232 295, 241 299 C 250 303, 260 298, 263 290 C 266 282, 261 275, 255 274 C 249 273, 246 278, 248 283 C 250 288, 255 289, 259 286" fill="none" stroke="rgba(210,225,255,0.9)" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" /></g>
<g class="sigil-arm-3"><path d="M 260 260 C 271 255, 280 248, 283 238 C 287 224, 281 211, 270 208 C 255 204, 243 214, 242 228 C 241 243, 252 254, 265 254 C 278 254, 287 244, 286 232 C 285 221, 276 215, 267 217 C 258 219, 253 227, 255 235 C 257 243, 264 247, 271 244 C 278 241, 280 234, 277 228 C 274 222, 268 220, 263 223" fill="none" stroke="rgba(210,225,255,0.9)" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" /></g>
</g>
<g class="sigil-inner" transform="scale(0.1)">
<g class="sigil-inner-1"><path d="M 260 260 C 263 253, 268 249, 274 248 C 281 247, 286 251, 286 258 C 286 265, 281 270, 274 269 C 267 268, 263 263, 264 257 C 265 252, 269 249, 274 251 C 278 253, 279 258, 276 261" fill="none" stroke="rgba(126,240,209,0.86)" stroke-width="6" stroke-linecap="round" /></g>
<g class="sigil-inner-2"><path d="M 260 260 C 254 263, 249 268, 249 274 C 249 281, 254 286, 261 285 C 268 284, 272 279, 270 272 C 268 265, 262 262, 256 264 C 251 266, 249 271, 252 276 C 254 280, 259 281, 263 278" fill="none" stroke="rgba(126,240,209,0.86)" stroke-width="6" stroke-linecap="round" /></g>
<g class="sigil-inner-3"><path d="M 260 260 C 263 254, 260 247, 254 245 C 248 243, 243 248, 244 255 C 245 262, 251 266, 258 264 C 265 262, 268 256, 265 250 C 262 244, 256 243, 251 246 C 247 249, 246 254, 249 258" fill="none" stroke="rgba(126,240,209,0.86)" stroke-width="6" stroke-linecap="round" /></g>
</g>
<circle cx="26" cy="26" r="6.2" fill="url(#brandSigilCenter)" />
<circle cx="26" cy="26" r="5.5" fill="rgba(138,164,255,0.12)" class="sigil-bloom" />
<text x="26" y="31" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="10.5" fill="rgba(228,238,255,0.95)" filter="url(#brandSigilGlow)" class="sigil-psi">Ψ</text>
</g>
</svg>
`;
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
soundButton.setAttribute('title', soundEnabled ? 'Interface sounds on' : 'Interface sounds off');
soundButton.innerHTML = soundEnabled ? '✦' : '○';
};
const ensureAudio = async () => {
if (!audioContext) {
const AudioCtor = window.AudioContext || window.webkitAudioContext;
if (!AudioCtor) return null;
audioContext = new AudioCtor();
}
if (audioContext.state === 'suspended') {
try {
await audioContext.resume();
} catch (error) {
return null;
}
}
return audioContext;
};
const ping = async (freq = FREQ.presence, duration = 0.06, type = 'sine') => {
if (!soundEnabled) return;
const ctx = await ensureAudio();
if (!ctx) return;
const oscillator = ctx.createOscillator();
const gain = ctx.createGain();
const now = ctx.currentTime;
oscillator.type = type;
oscillator.frequency.setValueAtTime(freq, now);
oscillator.frequency.linearRampToValueAtTime(freq * 1.08, now + duration);
gain.gain.setValueAtTime(0.0001, now);
gain.gain.linearRampToValueAtTime(0.035, now + 0.01);
gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
oscillator.connect(gain);
gain.connect(ctx.destination);
oscillator.start(now);
oscillator.stop(now + duration + 0.02);
};
injectBrandSigilStyles();
injectBrandSigil();
syncSoundLabel();
if (soundButton) {
soundButton.addEventListener('click', async () => {
soundEnabled = !soundEnabled;
localStorage.setItem(SOUND_KEY, String(soundEnabled));
syncSoundLabel();
await ping(soundEnabled ? FREQ.higher_awareness : FREQ.presence, 0.08, 'triangle');
});
}
pingTargets.forEach((node) => {
node.addEventListener('mouseenter', () => {
ping(FREQ.presence, 0.045, 'sine');
});
node.addEventListener('click', () => {
ping(FREQ.transformation, 0.075, 'triangle');
});
});
document.querySelectorAll('[data-glow]').forEach((node) => {
node.addEventListener('mousemove', (event) => {
const rect = node.getBoundingClientRect();
const x = ((event.clientX - rect.left) / rect.width) * 100;
const y = ((event.clientY - rect.top) / rect.height) * 100;
node.style.backgroundImage = `radial-gradient(circle at ${x}% ${y}%, rgba(138,164,255,0.16), transparent 45%)`;
});
node.addEventListener('mouseleave', () => {
node.style.backgroundImage = '';
});
});
})();