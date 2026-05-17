(() => {
const navDataScript = document.createElement('script');
navDataScript.src = 'assets/js/site-navigation-data.js';
document.head.appendChild(navDataScript);

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

const footerStyleId = 'ethereon-footer-secondary-style';
if (!document.getElementById(footerStyleId)) {
  const style = document.createElement('style');
  style.id = footerStyleId;
  style.textContent = `.footer-secondary-links{max-width:1120px;margin:.8rem auto 0;padding:0 1.25rem;color:rgba(210,222,255,.62);font-size:.78rem;line-height:1.9}.footer-secondary-links a{color:rgba(226,236,255,.76);text-decoration:none}.footer-secondary-links a:hover{color:rgba(255,255,255,.98)}`;
  document.head.appendChild(style);
}

const soundButton = document.querySelector('[data-sound-toggle]');
const yearNodes = document.querySelectorAll('[data-year]');
const pingTargets = document.querySelectorAll('.ping-target, .button, .icon-button, .nav-links a');
yearNodes.forEach((node) => {
node.textContent = new Date().getFullYear();
});
const SOUND_KEY = 'ethereonlabs-sound-enabled';
let soundEnabled = localStorage.getItem(SOUND_KEY) === 'true';
})();
