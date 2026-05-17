(() => {
  const navs = document.querySelectorAll('.nav-links');
  const brandMarks = document.querySelectorAll('.brand-mark');
  if (!navs.length) return;
  const links = [
    ['index.html', 'Home'], ['principles.html', 'Principles'], ['realm.html', 'Realm'], ['lumina-dashboard.html', 'Dashboard'], ['build.html', 'Build'], ['lumina.html', 'Lumina'], ['continuity.html', 'Continuity'], ['roadmap.html', 'Roadmap'], ['specimen.html', 'Specimen'], ['harmonics.html', 'Harmonics'], ['rse.html', 'RSE'], ['rse-whitepaper.html', 'The Spiral'], ['lexicon.html', 'Lexicon'], ['faq.html', 'FAQ'], ['about.html', 'About'], ['updates.html', 'Updates'], ['explore.html', 'Explore'], ['chamber.html', 'Chamber'], ['contact.html', 'Contact']
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
    mark.innerHTML = `<svg class="brand-sigil" viewBox="0 0 52 52" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false"><defs><radialGradient id="brandSigilCenter" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#1c2545"/><stop offset="100%" stop-color="#060913"/></radialGradient></defs><rect x="1" y="1" width="50" height="50" rx="14" fill="#07091a" stroke="rgba(138,164,255,0.14)"/><g><g class="sigil-orbit-a"><ellipse cx="26" cy="26" rx="22" ry="12" fill="none" stroke="rgba(138,164,255,0.22)" stroke-width="0.6"/></g><g class="sigil-orbit-b"><ellipse cx="26" cy="26" rx="12" ry="22" fill="none" stroke="rgba(126,240,209,0.18)" stroke-width="0.6"/></g><g class="sigil-ring-outer"><circle cx="26" cy="26" r="21.5" fill="none" stroke="rgba(205,220,255,0.45)" stroke-width="0.75" stroke-dasharray="1.4 2.2"/></g><g class="sigil-ring-inner"><circle cx="26" cy="26" r="18.2" fill="none" stroke="rgba(126,240,209,0.54)" stroke-width="0.7" stroke-dasharray="1 1.8"/></g><circle cx="26" cy="26" r="8" fill="url(#brandSigilCenter)"/><circle cx="26" cy="26" r="7.4" fill="rgba(138,164,255,0.12)" class="sigil-bloom"/><text x="26" y="32.8" text-anchor="middle" font-family="Georgia" font-size="15" fill="rgba(228,238,255,0.98)">Ψ</text></g></svg>`;
  });
  if (document.getElementById('ethereon-header-normalizer-style')) return;
  const style = document.createElement('style');
  style.id = 'ethereon-header-normalizer-style';
  style.textContent = `.site-header .nav-wrap{align-items:center!important;gap:.75rem!important}.site-header .brand,.site-header .header-actions{flex:0 0 auto!important}.site-header .brand-mark{width:58px!important;height:58px!important;border-radius:17px!important;border:1px solid rgba(160,188,255,.30)!important;background:linear-gradient(135deg,rgba(7,10,22,.98),rgba(18,26,48,.90))!important;box-shadow:inset 0 0 24px rgba(138,164,255,.18),0 0 22px rgba(138,164,255,.12)!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;position:relative!important;overflow:hidden!important;padding:0!important}.site-header .brand-mark::before,.site-header .brand-mark::after{content:none!important;display:none!important;background:none!important;border:0!important;box-shadow:none!important}.site-header .brand-mark>*:not(.brand-sigil){display:none!important}.site-header .brand-sigil{display:block!important;width:100%!important;height:100%!important;position:relative!important;z-index:2!important}.brand-sigil .sigil-ring-outer{animation:brandSpinCw 36s linear infinite;transform-origin:26px 26px}.brand-sigil .sigil-ring-inner{animation:brandSpinCcw 22s linear infinite;transform-origin:26px 26px}.brand-sigil .sigil-orbit-a{animation:brandSpinCw 70s linear infinite;transform-origin:26px 26px}.brand-sigil .sigil-orbit-b{animation:brandSpinCcw 90s linear infinite;transform-origin:26px 26px}.brand-sigil .sigil-bloom{animation:brandPsiPulse 3.5s ease-in-out infinite}@keyframes brandSpinCw{to{transform:rotate(360deg)}}@keyframes brandSpinCcw{to{transform:rotate(-360deg)}}@keyframes brandPsiPulse{0%,100%{opacity:.12}50%{opacity:.42}}.site-header .nav-links{display:flex!important;flex:1 1 auto!important;min-width:0!important;flex-wrap:nowrap!important;white-space:nowrap!important;overflow-x:auto!important;overflow-y:hidden!important;scrollbar-width:none!important}.site-header .nav-links::-webkit-scrollbar{display:none}.site-header .nav-links a{flex:0 0 auto!important}@media(max-width:760px){.site-header .nav-wrap{flex-direction:column!important;align-items:stretch!important}.site-header .brand,.site-header .nav-links{width:100%!important}.site-header .brand-mark{width:54px!important;height:54px!important}.site-header .header-actions{display:none!important}}`;
  document.head.appendChild(style);
})();