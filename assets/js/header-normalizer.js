(() => {
  const navs = document.querySelectorAll('.nav-links');
  const brandMarks = document.querySelectorAll('.brand-mark');
  const brandStrong = document.querySelectorAll('.brand-text strong');
  if (!navs.length) return;

  const fallbackLinks = [
    ['index.html', 'Home'], ['lumina.html', 'Lumina'], ['continuity.html', 'Continuity'], ['roadmap.html', 'Roadmap'], ['harmonics.html', 'Harmonics'], ['rse.html', 'RSE'], ['rse-whitepaper.html', 'The Spiral'], ['explore.html', 'Explore'], ['chamber.html', 'Chamber'], ['about.html', 'About'], ['contact.html', 'Contact']
  ];
  const links = (window.ETHEREON_SITE_NAVIGATION && window.ETHEREON_SITE_NAVIGATION.primary) || fallbackLinks;
  const last = window.location.pathname.split('/').filter(Boolean).pop() || 'index.html';
  const current = last.endsWith('.html') ? last : `${last}.html`;

  navs.forEach((nav) => {
    const existing = Array.from(nav.querySelectorAll('a')).map((a) => [a.getAttribute('href'), a.textContent]);
    const alreadyCurrent = existing.length === links.length && links.every(([href, label], index) => existing[index] && existing[index][0] === href && existing[index][1] === label);
    if (!alreadyCurrent) {
      nav.innerHTML = '';
      links.forEach(([href, label]) => {
        const a = document.createElement('a');
        a.href = href;
        a.textContent = label;
        nav.appendChild(a);
      });
    }
    nav.querySelectorAll('a').forEach((a) => {
      if (a.getAttribute('href') === current) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    });
  });

  brandStrong.forEach((node) => {
    if (node.querySelector('.brand-cap')) return;
    node.innerHTML = `<span class="brand-cap">E</span>THEREON<span class="brand-cap brand-cap-l">L</span>ABS`;
  });

  brandMarks.forEach((mark) => {
    if (mark.querySelector('.brand-sigil')) return;
    mark.innerHTML = `<svg class="brand-sigil" viewBox="0 0 52 52" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false"><defs><radialGradient id="brandSigilCenter" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#1c2545"/><stop offset="100%" stop-color="#060913"/></radialGradient></defs><rect x="1" y="1" width="50" height="50" rx="14" fill="#07091a" stroke="rgba(138,164,255,0.14)"/><g><g class="sigil-orbit-a"><ellipse cx="26" cy="26" rx="22" ry="12" fill="none" stroke="rgba(138,164,255,0.22)" stroke-width="0.6"/></g><g class="sigil-orbit-b"><ellipse cx="26" cy="26" rx="12" ry="22" fill="none" stroke="rgba(126,240,209,0.18)" stroke-width="0.6"/></g><g class="sigil-ring-outer"><circle cx="26" cy="26" r="21.5" fill="none" stroke="rgba(205,220,255,0.45)" stroke-width="0.75" stroke-dasharray="1.4 2.2"/></g><g class="sigil-ring-inner"><circle cx="26" cy="26" r="18.2" fill="none" stroke="rgba(126,240,209,0.54)" stroke-width="0.7" stroke-dasharray="1 1.8"/></g><circle cx="26" cy="26" r="9.4" fill="url(#brandSigilCenter)"/><circle cx="26" cy="26" r="9.0" fill="rgba(138,164,255,0.14)" class="sigil-bloom"/><text x="26" y="35.8" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-weight="700" font-size="25" fill="rgba(248,252,255,0.99)" stroke="rgba(248,252,255,0.35)" stroke-width="0.35">Ψ</text></g></svg>`;
  });
})();
