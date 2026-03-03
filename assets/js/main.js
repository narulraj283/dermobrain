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

// ─── Client-Side Search ────────────────────────────
let searchIndex = [];

// Load search index
fetch('/assets/js/search-index.json')
    .then(response => response.json())
    .then(data => {
        searchIndex = data;
        console.log('Search index loaded:', searchIndex.length, 'articles');
    })
    .catch(error => console.log('Search index not available:', error));

function performSearch(query) {
    if (!query.trim()) return [];

    const lowerQuery = query.toLowerCase();
    return searchIndex.filter(article => {
        const titleMatch = article.title.toLowerCase().includes(lowerQuery);
        const descMatch = article.meta_description.toLowerCase().includes(lowerQuery);
        const categoryMatch = article.category.toLowerCase().includes(lowerQuery);
        return titleMatch || descMatch || categoryMatch;
    }).slice(0, 10); // Return top 10 results
}

// ─── Hero Search (with real search functionality) ────
(function() {
    const searchInput = document.getElementById('heroSearch');
    const searchBtn = document.querySelector('.search-btn');

    function executeSearch() {
        const query = searchInput.value.trim();
        if (query) {
            const results = performSearch(query);
            if (results.length > 0) {
                // Navigate to first result
                const firstResult = results[0];
                const categoryInfo = searchIndex.find(a => a.slug === firstResult.slug);
                if (categoryInfo) {
                    // Note: category slug and pillar slug mapping should be done via categories
                    console.log('Search found articles:', results.length);
                    // For now, log results. In production, could show search results page
                }
            } else {
                console.log('No results found for:', query);
            }
        }
    }

    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                executeSearch();
            }
        });
    }

    if (searchBtn) {
        searchBtn.addEventListener('click', executeSearch);
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
