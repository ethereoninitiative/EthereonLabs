(() => {
const ensureNavData = (callback) => {
  if (window.ETHEREON_SITE_NAVIGATION) {
    callback();
    return;
  }
  const navDataScript = document.createElement('script');
  navDataScript.src = 'assets/js/site-navigation-data.js';
  navDataScript.onload = callback;
  navDataScript.onerror = callback;
  document.head.appendChild(navDataScript);
};

const loadBrandSigil = () => {
  if (document.querySelector('script[data-brand-sigil]')) return;
  const script = document.createElement('script');
  script.src = 'assets/js/brand-sigil.js';
  script.setAttribute('data-brand-sigil', '');
  document.head.appendChild(script);
};

const installDrydockStyles = () => {
  if (document.querySelector('style[data-ethereon-drydock-styles]')) return;
  const style = document.createElement('style');
  style.setAttribute('data-ethereon-drydock-styles', '');
  style.textContent = `
    .footer-row > .footer-brand-block {
      font-size: initial;
      display: grid;
      gap: 0.3rem;
      align-items: start;
    }
    .footer-row > .footer-brand-block::before,
    .footer-row > .footer-brand-block::after {
      content: none !important;
      display: none !important;
    }
    .footer-brand-link {
      color: var(--text);
      font-size: 0.92rem;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      text-decoration: none;
    }
    .footer-tagline {
      color: rgba(210,222,255,0.68);
      font-size: 0.84rem;
      line-height: 1.45;
      max-width: 46ch;
    }
    .footer-year {
      justify-self: end;
      color: rgba(210,222,255,0.66);
      font-size: 0.82rem;
    }
    .footer-secondary-links {
      display: flex;
      flex-wrap: wrap;
      gap: 0.45rem;
    }
    @media (max-width: 760px) {
      .footer-year { justify-self: start; font-size: 0.78rem; }
      .footer-brand-link { font-size: 0.78rem; letter-spacing: 0.09em; }
      .footer-tagline { font-size: 0.78rem; line-height: 1.42; max-width: 32ch; }
    }
  `;
  document.head.appendChild(style);
};

const normalizePath = (href) => {
  const anchor = document.createElement('a');
  anchor.href = href;
  return anchor.pathname.split('/').pop() || 'index.html';
};

const enhancePrimaryNav = () => {
  const navLinks = window.ETHEREON_SITE_NAVIGATION && window.ETHEREON_SITE_NAVIGATION.primary;
  if (!navLinks) return;
  const current = normalizePath(window.location.href);
  document.querySelectorAll('.nav-links[aria-label="Primary"]').forEach((nav) => {
    nav.innerHTML = navLinks.map(([href, label]) => {
      const isCurrent = normalizePath(href) === current;
      return `<a href="${href}"${isCurrent ? ' aria-current="page"' : ''}>${label}</a>`;
    }).join('');
  });
};

const secondaryFooterLinks = () => {
  const fallbackFooterLinks = [
    ['principles.html', 'Principles'],
    ['realm.html', 'Realm'],
    ['lumina-dashboard.html', 'Dashboard'],
    ['harmonics.html', 'Harmonics'],
    ['rse.html', 'RSE'],
    ['specimen.html', 'Specimen'],
    ['lexicon.html', 'Lexicon'],
    ['faq.html', 'FAQ'],
    ['updates.html', 'Updates'],
  ];
  return (window.ETHEREON_SITE_NAVIGATION && window.ETHEREON_SITE_NAVIGATION.secondaryFooter) || fallbackFooterLinks;
};

const enhanceFooter = () => {
  document.querySelectorAll('.footer-row').forEach((footerRow) => {
    if (!footerRow.querySelector('[data-footer-brand-block]')) {
      footerRow.innerHTML = `
        <div class="footer-brand-block" data-footer-brand-block>
          <a class="footer-brand-link" href="index.html">EthereonLabs</a>
          <span class="footer-tagline">Adaptive continuity workspaces for returning to complex work.</span>
        </div>
        <div class="footer-year">© <span data-year></span></div>
      `;
    }

    const next = footerRow.nextElementSibling;
    if (next && next.matches('[data-secondary-footer-links]')) return;

    const group = document.createElement('nav');
    group.className = 'footer-secondary-links';
    group.setAttribute('data-secondary-footer-links', '');
    group.setAttribute('aria-label', 'Secondary site links');
    group.innerHTML = secondaryFooterLinks().map(([href, label]) => `<a href="${href}">${label}</a>`).join('');
    footerRow.insertAdjacentElement('afterend', group);
  });
};

const normalizeLegacyExploreLabels = () => {
  document.querySelectorAll('a[href="explore.html"]').forEach((anchor) => {
    const text = anchor.textContent.trim();
    if (text === '← Back to Explore') anchor.textContent = '← Back to Research';
    if (text === 'Explore' && anchor.closest('.nav-links')) anchor.textContent = 'Research';
    if (text === 'Explore the system') anchor.textContent = 'Research and deeper system';
  });
};

const installSoundToggle = () => {
  const soundButton = document.querySelector('[data-sound-toggle]');
  const SOUND_KEY = 'ethereonlabs-sound-enabled';
  let soundEnabled = localStorage.getItem(SOUND_KEY) === 'true';
  let audioContext = null;

  const updateButton = () => {
    if (!soundButton) return;
    soundButton.setAttribute('aria-pressed', soundEnabled ? 'true' : 'false');
    soundButton.setAttribute('title', soundEnabled ? 'Interface sounds on' : 'Interface sounds off');
    soundButton.textContent = soundEnabled ? '●' : '○';
  };

  const ping = () => {
    if (!soundEnabled) return;
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      audioContext = audioContext || new AudioCtx();
      const oscillator = audioContext.createOscillator();
      const gain = audioContext.createGain();
      oscillator.type = 'sine';
      oscillator.frequency.setValueAtTime(528, audioContext.currentTime);
      oscillator.frequency.exponentialRampToValueAtTime(660, audioContext.currentTime + 0.06);
      gain.gain.setValueAtTime(0.0001, audioContext.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.025, audioContext.currentTime + 0.012);
      gain.gain.exponentialRampToValueAtTime(0.0001, audioContext.currentTime + 0.11);
      oscillator.connect(gain);
      gain.connect(audioContext.destination);
      oscillator.start();
      oscillator.stop(audioContext.currentTime + 0.12);
    } catch (_) {
      // Sound is optional; failures should never affect navigation.
    }
  };

  if (soundButton) {
    soundButton.addEventListener('click', () => {
      soundEnabled = !soundEnabled;
      localStorage.setItem(SOUND_KEY, soundEnabled ? 'true' : 'false');
      updateButton();
      ping();
    });
  }

  document.addEventListener('click', (event) => {
    const target = event.target.closest('.ping-target, .button, .nav-links a, .footer a');
    if (target && target !== soundButton) ping();
  });

  updateButton();
};

const enhanceSite = () => {
  installDrydockStyles();
  loadBrandSigil();
  enhancePrimaryNav();
  normalizeLegacyExploreLabels();
  enhanceFooter();

  const yearNodes = document.querySelectorAll('[data-year]');
  yearNodes.forEach((node) => {
    node.textContent = new Date().getFullYear();
  });

  installSoundToggle();
};

ensureNavData(enhanceSite);
})();
