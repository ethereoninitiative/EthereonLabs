(() => {
  const FREQUENCIES = {
    '432': 216,
    '528': 264,
    '963': 321,
    blend: 240
  };

  let audioContext;
  let oscillator;
  let gain;
  let enabled = false;

  function detectHarmonic() {
    const harmonic = document.querySelector('[data-weather-harmonic]')?.textContent || '';
    if (harmonic.includes('432')) return '432';
    if (harmonic.includes('528')) return '528';
    if (harmonic.includes('963')) return '963';
    return 'blend';
  }

  function ensureAudio() {
    if (audioContext) return;
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    oscillator = audioContext.createOscillator();
    gain = audioContext.createGain();
    oscillator.type = 'sine';
    gain.gain.value = 0.0001;
    oscillator.connect(gain);
    gain.connect(audioContext.destination);
    oscillator.start();
  }

  function updateTone() {
    if (!enabled || !oscillator || !gain) return;
    const harmonic = detectHarmonic();
    const frequency = FREQUENCIES[harmonic] || FREQUENCIES.blend;
    const now = audioContext.currentTime;
    oscillator.frequency.setTargetAtTime(frequency, now, 0.08);
    gain.gain.setTargetAtTime(0.025, now, 0.2);
  }

  function stopTone() {
    if (!gain || !audioContext) return;
    gain.gain.setTargetAtTime(0.0001, audioContext.currentTime, 0.15);
  }

  function toggleAudio(button) {
    enabled = !enabled;
    ensureAudio();
    if (audioContext.state === 'suspended') audioContext.resume();
    button.setAttribute('aria-pressed', enabled ? 'true' : 'false');
    button.textContent = enabled ? 'Harmonic audio on' : 'Harmonic audio off';
    if (enabled) updateTone();
    else stopTone();
  }

  function install() {
    const controls = document.querySelector('.weather-controls');
    if (!controls || controls.querySelector('[data-harmonic-audio-toggle]')) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.dataset.harmonicAudioToggle = 'true';
    button.setAttribute('aria-pressed', 'false');
    button.textContent = 'Harmonic audio off';
    button.addEventListener('click', () => toggleAudio(button));
    controls.appendChild(button);

    const observer = new MutationObserver(() => updateTone());
    const target = document.querySelector('[data-weather-harmonic]');
    if (target) observer.observe(target, { childList: true, characterData: true, subtree: true });
  }

  document.addEventListener('DOMContentLoaded', install);
})();
