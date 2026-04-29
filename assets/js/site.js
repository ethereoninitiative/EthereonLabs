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
.ethereon-guide {
position: fixed;
right: 1rem;
bottom: 1rem;
z-index: 20;
max-width: min(360px, calc(100% - 2rem));
padding: 1rem;
border: 1px solid rgba(160,188,255,0.22);
border-radius: 22px;
background: linear-gradient(180deg, rgba(14, 22, 42, 0.92), rgba(7, 11, 22, 0.94));
box-shadow: 0 18px 60px rgba(0,0,0,0.42);
backdrop-filter: blur(16px);
color: var(--text, #eaf0ff);
}
.ethereon-guide small {
display: block;
color: var(--accent-2, #7ef0d1);
text-transform: uppercase;
letter-spacing: 0.08em;
font-size: 0.72rem;
margin-bottom: 0.45rem;
}
.ethereon-guide p {
margin: 0 0 0.8rem;
color: var(--muted, #a9b7da);
line-height: 1.55;
font-size: 0.92rem;
}
.ethereon-guide a {
display: inline-flex;
text-decoration: none;
color: var(--text, #eaf0ff);
border: 1px solid rgba(126,240,209,0.2);
border-radius: 999px;
padding: 0.55rem 0.8rem;
background: rgba(126,240,209,0.055);
font-size: 0.86rem;
font-weight: 700;
}
.ethereon-guide button {
position: absolute;
top: 0.45rem;
right: 0.55rem;
border: 0;
background: transparent;
color: var(--muted, #a9b7da);
font-size: 1rem;
cursor: pointer;
}
@media (max-width: 760px) {
.ethereon-guide {
left: 0.7rem;
right: 0.7rem;
bottom: 0.7rem;
max-width: none;
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
const FREQ = { presence: 432, transformation: 528, higher_awareness: 963 };
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
try { await audioContext.resume(); } catch (error) { return null; }
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
const pageGuide = {
'index.html': ['Start with the build direction.', 'build.html'],
'': ['Start with the build direction.', 'build.html'],
'build.html': ['Next: read the truth boundary.', 'principles.html'],
'principles.html': ['Next: see the prototype surface.', 'lumina-dashboard.html'],
'lumina-dashboard.html': ['Next: open the Realm map.', 'realm.html'],
'realm.html': ['Next: inspect the Lumina substrate.', 'lumina.html'],
'lumina.html': ['Next: read continuity.', 'continuity.html'],
'continuity.html': ['Next: follow the staged roadmap.', 'roadmap.html'],
'roadmap.html': ['Next: view the interface specimen.', 'specimen.html'],
'specimen.html': ['Next: return to the full site map.', 'explore.html'],
'explore.html': ['Recommended path: Build → Principles → Dashboard → Realm.', 'build.html'],
'rse.html': ['Next: read the whitepaper version.', 'rse-whitepaper.html'],
'rse-whitepaper.html': ['Next: return to the conceptual frame.', 'rse.html'],
'lexicon.html': ['Next: connect terms back to continuity.', 'continuity.html'],
'faq.html': ['Next: open the site guide.', 'explore.html'],
'about.html': ['Next: see what is being built.', 'build.html'],
'updates.html': ['Next: open the roadmap.', 'roadmap.html'],
'contact.html': ['Next: return to the site guide.', 'explore.html'],
'chamber.html': ['Next: open the Realm map.', 'realm.html'],
};
const normalizePath = () => {
const last = window.location.pathname.split('/').filter(Boolean).pop() || '';
if (!last) return '';
return last.endsWith('.html') ? last : `${last}.html`;
};
const injectGuide = () => {
if (sessionStorage.getItem('ethereonlabs-guide-dismissed') === 'true') return;
const key = normalizePath();
const guide = pageGuide[key];
if (!guide) return;
const box = document.createElement('aside');
box.className = 'ethereon-guide';
box.setAttribute('aria-label', 'Suggested next step');
box.innerHTML = `<button type="button" aria-label="Dismiss guide">×</button><small>Suggested next step</small><p>${guide[0]}</p><a class="ping-target" href="${guide[1]}">Continue path</a>`;
document.body.appendChild(box);
box.querySelector('button')?.addEventListener('click', () => {
sessionStorage.setItem('ethereonlabs-guide-dismissed', 'true');
box.remove();
});
};
injectBrandSigilStyles();
injectBrandSigil();
injectGuide();
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
node.addEventListener('mouseenter', () => { ping(FREQ.presence, 0.045, 'sine'); });
node.addEventListener('click', () => { ping(FREQ.transformation, 0.075, 'triangle'); });
});
document.querySelectorAll('[data-glow]').forEach((node) => {
node.addEventListener('mousemove', (event) => {
const rect = node.getBoundingClientRect();
const x = ((event.clientX - rect.left) / rect.width) * 100;
const y = ((event.clientY - rect.top) / rect.height) * 100;
node.style.backgroundImage = `radial-gradient(circle at ${x}% ${y}%, rgba(138,164,255,0.16), transparent 45%)`;
});
node.addEventListener('mouseleave', () => { node.style.backgroundImage = ''; });
});
})();