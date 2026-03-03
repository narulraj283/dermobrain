/**
 * DermoBrain.com - Main JavaScript
 * Handles: dark mode, mobile nav, search, filter tabs, dropdowns, copy link
 */

// ─── Dark Mode Toggle ───────────────────────────────
(function() {
    const toggle = document.getElementById('darkModeToggle');
    const html = document.documentElement;

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

// ─── Mobile Menu Toggle + Mobile Dropdowns ──────────
(function() {
    const menuToggle = document.getElementById('mobileMenuToggle');
    const mainNav = document.getElementById('mainNav');

    if (menuToggle && mainNav) {
        menuToggle.addEventListener('click', (e) => {
            e.stopPropagation();
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

        // Mobile dropdown toggle - tap arrow to expand, tap text to navigate
        const dropdownItems = mainNav.querySelectorAll('.has-dropdown');
        dropdownItems.forEach(item => {
            const arrow = item.querySelector('.dropdown-arrow');
            const link = item.querySelector('.nav-link');

            if (arrow && link) {
                // On mobile, clicking the arrow toggles the dropdown
                arrow.addEventListener('click', (e) => {
                    if (window.innerWidth <= 768) {
                        e.preventDefault();
                        e.stopPropagation();
                        item.classList.toggle('open');
                        // Close other open dropdowns
                        dropdownItems.forEach(other => {
                            if (other !== item) other.classList.remove('open');
                        });
                    }
                });

                // On mobile, prevent default link behavior - toggle dropdown instead
                link.addEventListener('click', (e) => {
                    if (window.innerWidth <= 768) {
                        e.preventDefault();
                        e.stopPropagation();
                        item.classList.toggle('open');
                        dropdownItems.forEach(other => {
                            if (other !== item) other.classList.remove('open');
                        });
                    }
                });
            }
        });
    }
})();

// ─── Desktop Dropdown Menus (hover + keyboard) ──────
(function() {
    if (window.innerWidth > 768) {
        const dropdowns = document.querySelectorAll('.has-dropdown');
        dropdowns.forEach(item => {
            const link = item.querySelector('.nav-link');
            const menu = item.querySelector('.dropdown-menu');
            if (!link || !menu) return;

            // Show on hover
            item.addEventListener('mouseenter', () => menu.style.display = 'block');
            item.addEventListener('mouseleave', () => menu.style.display = '');

            // Show on focus for keyboard navigation
            link.addEventListener('focus', () => menu.style.display = 'block');
            item.addEventListener('focusout', (e) => {
                if (!item.contains(e.relatedTarget)) menu.style.display = '';
            });
        });
    }
})();

// ─── Client-Side Search with Dropdown Results ───────
(function() {
    let searchIndex = [];

    // Load search index
    fetch('/assets/js/search-index.json')
        .then(r => r.json())
        .then(data => { searchIndex = data; })
        .catch(() => {});

    // Category to pillar mapping (built from known structure)
    const categoryToPillar = {
        'skin-conditions': 'medical-dermatology', 'skin-cancer': 'medical-dermatology',
        'allergies': 'medical-dermatology', 'hair-scalp': 'medical-dermatology',
        'nails': 'medical-dermatology', 'pediatric': 'medical-dermatology',
        'skin-of-color': 'medical-dermatology', 'myths': 'medical-dermatology',
        'mohs-surgery': 'surgical-dermatology', 'skin-cancer-surgery': 'surgical-dermatology',
        'procedures': 'surgical-dermatology', 'pre-post-op': 'surgical-dermatology',
        'injectables': 'cosmetic-dermatology', 'lasers': 'cosmetic-dermatology',
        'rejuvenation': 'cosmetic-dermatology', 'body-contouring': 'cosmetic-dermatology',
        'science': 'skincare', 'mens': 'skincare', 'womens': 'skincare',
        'lifestyle': 'skincare', 'procedures-az': 'surgical-dermatology'
    };

    function performSearch(query) {
        if (!query.trim()) return [];
        const q = query.toLowerCase();
        return searchIndex.filter(a =>
            a.title.toLowerCase().includes(q) ||
            a.meta_description.toLowerCase().includes(q) ||
            a.category.toLowerCase().includes(q)
        ).slice(0, 8);
    }

    function getArticleUrl(article) {
        const pillar = categoryToPillar[article.category] || 'medical-dermatology';
        return '/' + pillar + '/' + article.category + '/' + article.slug + '.html';
    }

    function showResults(results, container) {
        container.innerHTML = '';
        if (results.length === 0) {
            container.innerHTML = '<div class="search-no-results">No articles found. Try different keywords.</div>';
            container.style.display = 'block';
            return;
        }
        results.forEach(article => {
            const url = getArticleUrl(article);
            const item = document.createElement('a');
            item.href = url;
            item.className = 'search-result-item';
            item.innerHTML = '<strong>' + article.title + '</strong><span>' +
                article.category.replace(/-/g, ' ') + '</span>';
            container.appendChild(item);
        });
        container.style.display = 'block';
    }

    // Hero Search
    const heroInput = document.getElementById('heroSearch');
    const heroBtn = document.querySelector('.search-btn');

    if (heroInput) {
        // Create results dropdown - append to a wrapper outside overflow:hidden
        const resultsDiv = document.createElement('div');
        resultsDiv.className = 'search-results-dropdown';
        resultsDiv.style.display = 'none';
        // Create a relative wrapper around the search form for proper positioning
        const searchForm = heroInput.parentNode;
        const wrapper = document.createElement('div');
        wrapper.style.position = 'relative';
        wrapper.style.maxWidth = '560px';
        wrapper.style.margin = '0 auto';
        searchForm.parentNode.insertBefore(wrapper, searchForm);
        wrapper.appendChild(searchForm);
        wrapper.appendChild(resultsDiv);

        let debounceTimer;
        heroInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const q = heroInput.value.trim();
                if (q.length >= 2) {
                    showResults(performSearch(q), resultsDiv);
                } else {
                    resultsDiv.style.display = 'none';
                }
            }, 200);
        });

        heroInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const results = performSearch(heroInput.value);
                if (results.length > 0) {
                    window.location.href = getArticleUrl(results[0]);
                }
            }
        });

        if (heroBtn) {
            heroBtn.addEventListener('click', () => {
                const results = performSearch(heroInput.value);
                if (results.length > 0) {
                    window.location.href = getArticleUrl(results[0]);
                }
            });
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!heroInput.contains(e.target) && !resultsDiv.contains(e.target)) {
                resultsDiv.style.display = 'none';
            }
        });
    }
})();

// ─── Filter Tabs on Category Pages ──────────────────
(function() {
    const filterTabs = document.querySelectorAll('.filter-tab');
    const articleCards = document.querySelectorAll('.articles-grid .article-card');

    if (filterTabs.length === 0 || articleCards.length === 0) return;

    // Add "All" tab at the beginning
    const container = filterTabs[0].parentNode;
    const allTab = document.createElement('button');
    allTab.className = 'filter-tab active';
    allTab.textContent = 'All';
    allTab.dataset.filter = 'all';
    container.insertBefore(allTab, filterTabs[0]);

    const allTabs = container.querySelectorAll('.filter-tab');

    allTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const filter = tab.dataset.filter;

            // Update active state
            allTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Filter articles
            articleCards.forEach(card => {
                if (filter === 'all') {
                    card.style.display = '';
                } else {
                    const subcat = card.getAttribute('data-subcategory') || '';
                    card.style.display = (subcat === filter) ? '' : 'none';
                }
            });
        });
    });
})();

// ─── Copy Link Button (toast instead of alert) ──────
(function() {
    document.querySelectorAll('.share-btn.copy-link').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const url = btn.dataset.url || window.location.href;
            navigator.clipboard.writeText(url).then(() => {
                // Show toast
                const toast = document.createElement('div');
                toast.className = 'copy-toast';
                toast.textContent = 'Link copied!';
                document.body.appendChild(toast);
                setTimeout(() => toast.classList.add('show'), 10);
                setTimeout(() => {
                    toast.classList.remove('show');
                    setTimeout(() => toast.remove(), 300);
                }, 2000);
            });
        });
    });
})();

// ─── Smooth scroll for anchor links ─────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href === '#') return;
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// ─── Make category-item cards fully clickable ────────
(function() {
    document.querySelectorAll('.category-item').forEach(card => {
        const link = card.querySelector('a');
        if (link) {
            card.style.cursor = 'pointer';
            card.addEventListener('click', (e) => {
                if (e.target.tagName !== 'A') {
                    window.location.href = link.href;
                }
            });
        }
    });
})();
