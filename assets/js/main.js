/**
 * DermoBrain.com - Main JavaScript
 */

// ─── Dark Mode Toggle ───────────────────────────────
(function() {
    const toggle = document.getElementById('darkModeToggle');
    const html = document.documentElement;

    // Check saved preference or system preference
    const saved = localStorage.getItem('dermobrain-theme');
    if (saved) {
        html.setAttribute('data-theme', saved);
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        html.setAttribute('data-theme', 'dark');
    }

    if (toggle) {
        toggle.addEventListener('click', () => {
            const current = html.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
            localStorage.setItem('dermobrain-theme', next);
        });
    }
})();

// ─── Mobile Menu Toggle ─────────────────────────────
(function() {
    const menuToggle = document.getElementById('mobileMenuToggle');
    const mainNav = document.getElementById('mainNav');

    if (menuToggle && mainNav) {
        menuToggle.addEventListener('click', () => {
            mainNav.classList.toggle('active');
            menuToggle.classList.toggle('active');
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!menuToggle.contains(e.target) && !mainNav.contains(e.target)) {
                mainNav.classList.remove('active');
                menuToggle.classList.remove('active');
            }
        });
    }
})();

// ─── Hero Search (placeholder functionality) ────────
(function() {
    const searchInput = document.getElementById('heroSearch');
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const query = searchInput.value.trim();
                if (query) {
                    // Will be connected to real search in Phase 3
                    console.log('Search query:', query);
                }
            }
        });
    }
})();

// ─── Smooth scroll for anchor links ─────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});
