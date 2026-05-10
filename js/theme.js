// Theme toggle: swaps the CSS variables defined under html[data-theme="dark"]
// in modern.css. The init script in each page's <head> applies the saved
// preference before render to avoid a flash; this file owns the click handler
// and keeps the button icon in sync.
(function () {
  const root = document.documentElement;

  function currentTheme() {
    return root.dataset.theme === 'dark' ? 'dark' : 'light';
  }

  function syncIcon() {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;
    const useEl = btn.querySelector('use');
    if (!useEl) return;
    // Show the destination, not the current state: in light mode show the moon
    // (click to go dark), in dark mode show the sun (click to go light).
    const dest = currentTheme() === 'dark' ? 'sun' : 'moon';
    useEl.setAttribute('href', '#i-' + dest);
    btn.setAttribute('aria-label', 'Switch to ' + (dest === 'sun' ? 'light' : 'dark') + ' theme');
  }

  function setTheme(t) {
    root.dataset.theme = t;
    try { localStorage.setItem('theme', t); } catch (e) {}
    syncIcon();
  }

  function init() {
    syncIcon();
    const btn = document.getElementById('theme-toggle');
    if (btn) btn.addEventListener('click', function () {
      setTheme(currentTheme() === 'dark' ? 'light' : 'dark');
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
