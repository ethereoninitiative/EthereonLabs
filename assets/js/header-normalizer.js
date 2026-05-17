(() => {
  const navs = document.querySelectorAll('.nav-links');
  if (!navs.length) return;

  const links = [
    ['index.html', 'Home'],
    ['principles.html', 'Principles'],
    ['realm.html', 'Realm'],
    ['lumina-dashboard.html', 'Dashboard'],
    ['build.html', 'Build'],
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

  if (document.getElementById('ethereon-header-normalizer-style')) return;
  const style = document.createElement('style');
  style.id = 'ethereon-header-normalizer-style';
  style.textContent = `
    .site-header .nav-wrap { align-items: center !important; gap: .75rem !important; }
    .site-header .brand, .site-header .header-actions { flex: 0 0 auto !important; }
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
      .site-header .header-actions { display: none !important; }
    }
  `;
  document.head.appendChild(style);
})();
