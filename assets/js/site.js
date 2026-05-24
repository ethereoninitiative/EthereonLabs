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

const enhanceSite = () => {
  loadBrandSigil();
  enhancePrimaryNav();

  const fallbackFooterLinks = [
    ['principles.html', 'Principles'],
    ['realm.html', 'Realm'],
    ['lumina-dashboard.html', 'Dashboard'],
    ['build.html', 'Build'],
    ['specimen.html', 'Specimen'],
    ['lexicon.html', 'Lexicon'],
    ['faq.html', 'FAQ'],
    ['updates.html', 'Updates'],
  ];

  const footerLinks = (window.ETHEREON_SITE_NAVIGATION && window.ETHEREON_SITE_NAVIGATION.secondaryFooter) || fallbackFooterLinks;

  document.querySelectorAll('.footer-row').forEach((footerRow) => {
    if (footerRow.querySelector('[data-secondary-footer-links]')) return;
    const group = document.createElement('div');
    group.className = 'footer-secondary-links';
    group.setAttribute('data-secondary-footer-links', '');
    group.innerHTML = footerLinks.map(([href, label]) => `<a href="${href}">${label}</a>`).join(' · ');
    footerRow.insertAdjacentElement('afterend', group);
  });

  const soundButton = document.querySelector('[data-sound-toggle]');
  const yearNodes = document.querySelectorAll('[data-year]');
  yearNodes.forEach((node) => {
    node.textContent = new Date().getFullYear();
  });
  const SOUND_KEY = 'ethereonlabs-sound-enabled';
  let soundEnabled = localStorage.getItem(SOUND_KEY) === 'true';
};

ensureNavData(enhanceSite);
})();
