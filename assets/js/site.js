(() => {
const headerNormalizer = document.createElement('script');
headerNormalizer.src = 'assets/js/header-normalizer.js';
document.head.appendChild(headerNormalizer);

const soundButton = document.querySelector('[data-sound-toggle]');
const yearNodes = document.querySelectorAll('[data-year]');
const pingTargets = document.querySelectorAll('.ping-target, .button, .icon-button, .nav-links a');
yearNodes.forEach((node) => {
node.textContent = new Date().getFullYear();
});
const SOUND_KEY = 'ethereonlabs-sound-enabled';
let soundEnabled = localStorage.getItem(SOUND_KEY) === 'true';
})();