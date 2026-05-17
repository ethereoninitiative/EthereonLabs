(() => {
  const navs = document.querySelectorAll('.nav-links');
  const brandMarks = document.querySelectorAll('.brand-mark');

  const links = [
    ['index.html', 'Home'],
    ['principles.html', 'Principles'],
    ['realm.html', 'Realm'],
    ['lumina-dashboard.html', 'Dashboard'],
    ['build.html', 'Build'],
    ['lumina.html', 'Lumina'],
    ['continuity.html', 'Continuity'],
    ['roadmap.html', 'Roadmap'],
    ['specimen.html', 'Specimen'],
    ['harmonics.html', 'Harmonics'],
    ['rse.html', 'RSE'],
    ['rse-whitepaper.html', 'The Spiral'],
    ['lexicon.html', 'Lexicon'],
    ['faq.html', 'FAQ'],
    ['about.html', 'About'],
    ['updates.html', 'Updates'],
    ['explore.html', 'Explore'],
    ['chamber.html', 'Chamber'],
    ['contact.html', 'Contact'],
  ];

  const last = window.location.pathname.split('/').filter(Boolean).pop() || 'index.html';
  const current = last.endsWith('.html') ? last : `${last}.html`;

  navs.forEach((nav) => {
    nav.innerHTML = '';
    links.forEach(([href, label]) => {
      const a = document.createElement('a');
      a.href = href;
      a.textContent = label;
      if (href === current) a.setAttribute('aria-current', 'page');
      nav.appendChild(a);
    });
  });

  brandMarks.forEach((mark) => {
    if (mark.dataset.sigilInjected === 'true') return;
    mark.innerHTML = `
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
          <clipPath id="brandSigilClip"><rect x="1" y="1" width="50" height="50" rx="14" ry="14" /></clipPath>
        </defs>
        <rect x="1" y="1" width="50" height="50" rx="14" ry="14" fill="#07091a" stroke="rgba(138,164,255,0.14)" stroke-width="1.1" />
        <g clip-path="url(#brandSigilClip)">
          <g class="sigil-orbit-a"><ellipse cx="26" cy="26" rx="22" ry="12" fill="none" stroke="rgba(138,164,255,0.22)" stroke-width="0.6" /></g>
          <g class="sigil-orbit-b"><ellipse cx="26" cy="26" rx="12" ry="22" fill="none" stroke="rgba(126,240,209,0.18)" stroke-width="0.6" /></g>
          <g class="sigil-ring-outer"><circle cx="26" cy="26" r="21.5" fill="none" stroke="rgba(205,220,255,0.45)" stroke-width="0.75" stroke-dasharray="1.4 2.2" stroke-linecap="round" /></g>
          <g class="sigil-ring-inner"><circle cx="26" cy="26" r="18.2" fill="none" stroke="rgba(126,240,209,0.54)" stroke-width="0.7" stroke-dasharray="1 1.8" stroke-linecap="round" /></g>
          <circle cx="26" cy="26" r="8" fill="url(#brandSigilCenter)" />
          <circle cx="26" cy="26" r="7.4" fill="rgba(138,164,255,0.12)" class="sigil-bloom" />
          <text x="26" y="32.8" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="15" fill="rgba(228,238,255,0.98)" filter="url(#brandSigilGlow)" class="sigil-psi">Ψ</text>
        </g>
      </svg>`;
    mark.dataset.sigilInjected = 'true';
  });

  if (document.getElementById('ethereon-header-normalizer-style')) return;
  const style = document.createElement('style');
  style.id = 'ethereon-header-normalizer-style';
  style.textContent = `
    .site-header .nav-wrap { align-items: center !important; gap: .75rem !important; }
    .site-header .brand, .site-header .header-actions { flex: 0 0 auto !important; }
    .site-header .brand-mark {
      width: 58px !important;
      height: 58px !important;
      border-radius: 17px !important;
      border: 1px solid rgba(160,188,255,.30) !important;
      background: linear-gradient(135deg, rgba(7,10,22,.98), rgba(18,26,48,.90)) !important;
      box-shadow: inset 0 0 24px rgba(138,164,255,.18), 0 0 22px rgba(138,164,255,.12) !important;
      overflow: hidden !important;
      padding: 0 !important;
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
    }
    .site-header .brand-mark::before, .site-header .brand-mark::after { content: none !important; display: none !important; }
    .site-header .brand-sigil { display: block !important; width: 100% !important; height: 100% !important; }
    .brand-sigil .sigil-ring-outer { animation: brandSpinCw 36s linear infinite; transform-origin: 26px 26px; }
    .brand-sigil .sigil-ring-inner { animation: brandSpinCcw 22s linear infinite; transform-origin: 26px 26px; opacity: .85; }
    .brand-sigil .sigil-orbit-a { animation: brandSpinCw 70s linear infinite; transform-origin: 26px 26px; opacity: .15; }
    .brand-sigil .sigil-orbit-b { animation: brandSpinCcw 90s linear infinite; transform-origin: 26px 26px; opacity: .10; }
    .brand-sigil .sigil-bloom { animation: brandPsiPulse 3.5s ease-in-out infinite; }
    .brand-sigil .sigil-psi { animation: brandPsiGlow 3.5s ease-in-out infinite; }
    @keyframes brandSpinCw { to { transform: rotate(360deg); } }
    @keyframes brandSpinCcw { to { transform: rotate(-360deg); } }
    @keyframes brandPsiPulse { 0%,100% { opacity:.12; } 50% { opacity:.42; } }
    @keyframes brandPsiGlow { 0%,100% { opacity:.9; filter: drop-shadow(0 0 1px rgba(220,235,255,.25)); } 50% { opacity:1; filter: drop-shadow(0 0 6px rgba(220,235,255,.95)); } }
    .site-header .nav-links {
      display: flex !important;
      flex: 1 1 auto !important;
      min-width: 0 !important;
      flex-wrap: nowrap !important;
      white-space: nowrap !important;
      overflow-x: auto !important;
      overflow-y: hidden !important;
      justify-content: flex-start !important;
      scrollbar-width: none !important;
    }
    .site-header .nav-links::-webkit-scrollbar { display: none !important; }
    .site-header .nav-links a { flex: 0 0 auto !important; white-space: nowrap !important; }
    @media (max-width: 760px) {
      .site-header .nav-wrap { flex-direction: column !important; align-items: stretch !important; }
      .site-header .brand, .site-header .nav-links { width: 100% !important; }
      .site-header .brand-mark { width: 54px !important; height: 54px !important; border-radius: 16px !important; }
      .site-header .header-actions { display: none !important; }
    }
  `;
  document.head.appendChild(style);
})();
