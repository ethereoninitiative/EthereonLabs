(() => {
  const root = document.querySelector('[data-psi42-interface]');
  if (!root) return;

  const styleId = 'psi42-transceiver-interface-style';
  if (!document.getElementById(styleId)) {
    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
.psi42-interface {
  position: relative;
  overflow: hidden;
}
.psi42-interface::before {
  content: '';
  position: absolute;
  inset: -35%;
  background:
    radial-gradient(circle at 25% 20%, rgba(126,240,209,0.18), transparent 32%),
    radial-gradient(circle at 74% 16%, rgba(138,164,255,0.16), transparent 34%),
    radial-gradient(circle at 50% 92%, rgba(255,224,138,0.12), transparent 38%);
  pointer-events: none;
}
.psi42-interface > * { position: relative; }
.psi42-console {
  display: grid;
  grid-template-columns: minmax(240px, 0.9fr) minmax(260px, 1.1fr);
  gap: 1rem;
  align-items: stretch;
  margin-top: 1.2rem;
}
.psi42-console textarea {
  width: 100%;
  min-height: 150px;
  resize: vertical;
  border-radius: 18px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(0,0,0,0.18);
  color: inherit;
  padding: 1rem;
  font: inherit;
  line-height: 1.55;
}
.psi42-tunes {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  margin: 0.75rem 0;
}
.psi42-tunes button,
.psi42-transmit {
  border: 1px solid rgba(255,255,255,0.18);
  border-radius: 999px;
  padding: 0.65rem 0.9rem;
  color: inherit;
  background: rgba(255,255,255,0.07);
  cursor: pointer;
}
.psi42-tunes button[aria-pressed='true'],
.psi42-transmit {
  border-color: rgba(126,240,209,0.42);
  background: rgba(126,240,209,0.09);
}
.psi42-output-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.65rem;
}
.psi42-output-tile {
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 16px;
  padding: 0.8rem;
  background: rgba(255,255,255,0.045);
}
.psi42-output-tile small {
  display: block;
  opacity: 0.7;
  margin-bottom: 0.25rem;
}
.psi42-output-value {
  font-weight: 800;
  letter-spacing: 0.02em;
}
.psi42-orb-wrap {
  display: grid;
  place-items: center;
  min-height: 170px;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 22px;
  background: rgba(0,0,0,0.12);
  margin-bottom: 0.8rem;
}
.psi42-orb {
  width: 112px;
  height: 112px;
  border-radius: 999px;
  background:
    radial-gradient(circle at 34% 26%, rgba(255,255,255,0.92), rgba(126,240,209,0.48) 18%, rgba(138,164,255,0.28) 44%, rgba(255,255,255,0) 70%),
    conic-gradient(from 20deg, rgba(126,240,209,0.22), rgba(138,164,255,0.38), rgba(255,224,138,0.22), rgba(126,240,209,0.22));
  box-shadow: 0 0 34px rgba(126,240,209,0.22), 0 0 70px rgba(138,164,255,0.16);
  transform: scale(var(--psi42-scale, 1));
  transition: transform 420ms ease, box-shadow 420ms ease, filter 420ms ease;
  filter: saturate(var(--psi42-saturation, 1));
}
.psi42-receipt {
  margin-top: 0.85rem;
  white-space: pre-wrap;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16px;
  padding: 0.85rem;
  background: rgba(0,0,0,0.18);
  color: var(--muted, #a9b7da);
  font-size: 0.9rem;
}
.psi42-mini-note {
  color: var(--muted, #a9b7da);
  font-size: 0.92rem;
}
@media (max-width: 820px) {
  .psi42-console { grid-template-columns: 1fr; }
}
    `;
    document.head.appendChild(style);
  }

  const input = root.querySelector('[data-psi42-input]');
  const transmit = root.querySelector('[data-psi42-transmit]');
  const tuneButtons = [...root.querySelectorAll('[data-psi42-tune]')];
  const orb = root.querySelector('[data-psi42-orb]');
  const receipt = root.querySelector('[data-psi42-receipt]');
  const fields = {
    signal: root.querySelector('[data-psi42-signal]'),
    shape: root.querySelector('[data-psi42-shape]'),
    drift: root.querySelector('[data-psi42-drift]'),
    recovery: root.querySelector('[data-psi42-recovery]'),
    coherence: root.querySelector('[data-psi42-coherence]'),
    phrase: root.querySelector('[data-psi42-phrase]'),
  };

  let activeTune = 'presence';
  const tunes = {
    presence: { label: 'presence', bias: 0.12, toki: 'mi awen', note: 'the signal steadies' },
    transformation: { label: 'transformation', bias: 0.06, toki: 'nasin li ante pona', note: 'the path changes without breaking' },
    expansion: { label: 'expansion', bias: 0.03, toki: 'sona li suli', note: 'the pattern opens outward' },
    blend: { label: 'blend', bias: 0.09, toki: 'nasin li kama sin', note: 'the path returns in a new shape' },
  };

  const clamp = (value, min = 0.08, max = 0.98) => Math.max(min, Math.min(max, value));
  const pct = (value) => `${Math.round(value * 100)}%`;
  const hashText = (text) => [...text].reduce((acc, char) => ((acc << 5) - acc + char.charCodeAt(0)) | 0, 2166136261) >>> 0;

  const updateTune = (name) => {
    activeTune = tunes[name] ? name : 'presence';
    tuneButtons.forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.psi42Tune === activeTune)));
  };

  const analyze = () => {
    const text = (input?.value || '').trim() || 'mi awen. nasin li kama sin.';
    const h = hashText(`${activeTune}:${text}`);
    const words = text.split(/\s+/).filter(Boolean).length;
    const vowels = (text.match(/[aeiou]/gi) || []).length;
    const anchors = ['return', 'pattern', 'path', 'work', 'awen', 'nasin', 'kama', 'sin', 'thread', 'remember'];
    const anchorHits = anchors.filter((word) => text.toLowerCase().includes(word)).length;
    const tune = tunes[activeTune];

    const base = ((h % 1000) / 1000) * 0.28 + 0.48;
    const density = clamp(words / 42, 0.05, 0.28);
    const voice = clamp(vowels / Math.max(18, text.length), 0.04, 0.18);
    const anchor = clamp(anchorHits * 0.045, 0, 0.22);

    const signal = clamp(base + tune.bias + voice);
    const shape = clamp(base + anchor + density + (activeTune === 'presence' ? 0.07 : 0));
    const drift = clamp(1 - (shape * 0.72 + signal * 0.18), 0.04, 0.72);
    const recovery = clamp((signal + shape + anchor + 0.16) / 2.25);
    const coherence = clamp((signal * 0.32) + (shape * 0.34) + (recovery * 0.26) + ((1 - drift) * 0.08));
    const receiptId = `psi42-public-${String(h).slice(0, 7)}`;

    fields.signal.textContent = pct(signal);
    fields.shape.textContent = pct(shape);
    fields.drift.textContent = pct(drift);
    fields.recovery.textContent = pct(recovery);
    fields.coherence.textContent = pct(coherence);
    fields.phrase.textContent = `${tune.toki} · ${tune.note}`;

    if (orb) {
      orb.style.setProperty('--psi42-scale', String(0.86 + coherence * 0.28));
      orb.style.setProperty('--psi42-saturation', String(0.82 + signal * 0.55));
      orb.style.boxShadow = `0 0 ${Math.round(22 + coherence * 38)}px rgba(126,240,209,0.24), 0 0 ${Math.round(48 + shape * 56)}px rgba(138,164,255,0.16)`;
    }

    if (receipt) {
      receipt.textContent = [
        `receipt: ${receiptId}`,
        `tune: ${tune.label}`,
        `signal: ${pct(signal)} | relationship shape: ${pct(shape)}`,
        `drift: ${pct(drift)} | recovery: ${pct(recovery)} | coherence: ${pct(coherence)}`,
        `boundary: public interface only; local browser witness; not runtime authority`,
      ].join('\n');
    }
  };

  tuneButtons.forEach((button) => {
    button.addEventListener('click', () => {
      updateTune(button.dataset.psi42Tune);
      analyze();
    });
  });
  transmit?.addEventListener('click', analyze);
  input?.addEventListener('input', () => window.clearTimeout(input._psi42Timer));
  input?.addEventListener('keyup', () => {
    window.clearTimeout(input._psi42Timer);
    input._psi42Timer = window.setTimeout(analyze, 360);
  });

  updateTune(activeTune);
  analyze();
})();
