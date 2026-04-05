(() => {
  document.querySelectorAll('[data-year]').forEach((node) => {
    node.textContent = new Date().getFullYear();
  });
  const soundButton = document.querySelector('[data-sound-toggle]');
  if (soundButton) {
    soundButton.addEventListener('click', () => {
      const pressed = soundButton.getAttribute('aria-pressed') === 'true';
      soundButton.setAttribute('aria-pressed', String(!pressed));
      soundButton.textContent = !pressed ? '✦' : '○';
    });
  }
})();
