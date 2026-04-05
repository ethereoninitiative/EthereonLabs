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

  // Fleet harmonic frequencies
  // 432Hz — presence (hover, arrival)
  // 528Hz — transformation (click, action)
  // 963Hz — higher awareness (sound toggle on)
  const FREQ = {
    presence:          432,
    transformation:    528,
    higher_awareness:  963,
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

  syncSoundLabel();

  if (soundButton) {
    soundButton.addEventListener('click', async () => {
      soundEnabled = !soundEnabled;
      localStorage.setItem(SOUND_KEY, String(soundEnabled));
      syncSoundLabel();
      // 963Hz on enable (higher awareness), 432Hz on disable (return to presence)
      await ping(soundEnabled ? FREQ.higher_awareness : FREQ.presence, 0.08, 'triangle');
    });
  }

  // Hover → 432Hz presence
  // Click → 528Hz transformation
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
