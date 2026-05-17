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

const enhanceSite = () => {
  const headerNormalizer = document.createElement('script');
  headerNormalizer.src = 'assets/js/header-normalizer.js';
  document.head.appendChild(headerNormalizer);

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
