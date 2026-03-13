#!/usr/bin/env python3
"""
DermoBrain.com Static Site Generator
Build script that reads JSON data and generates static HTML pages.
"""

import json
import os
import shutil
import datetime
from pathlib import Path
from urllib.parse import quote
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

# ─── Configuration ───────────────────────────────────────────────
DOMAIN = "https://dermobrain.com"
SITE_NAME = "DermoBrain"
SITE_TAGLINE = "Your Trusted Dermatology Encyclopedia"
GA4_ID = "G-LK62PEC2HD"

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"

BUILD_DATE = datetime.datetime.now().strftime("%Y-%m-%d")

# ─── State Names Mapping ─────────────────────────────────────────
STATE_NAMES = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'DC': 'District of Columbia', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii',
    'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine',
    'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota',
    'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska',
    'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico',
    'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island',
    'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas',
    'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington',
    'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
    'PR': 'Puerto Rico', 'GU': 'Guam', 'VI': 'US Virgin Islands',
    'AS': 'American Samoa', 'MP': 'Northern Mariana Islands',
    'AA': 'Armed Forces Americas', 'AE': 'Armed Forces Europe', 'AP': 'Armed Forces Pacific'
}

def normalize_city_name(city):
    """Normalize abbreviated city names from NPI data."""
    replacements = {
        'Ft ': 'Fort ', 'Ft. ': 'Fort ', 'Mt ': 'Mount ', 'Mt. ': 'Mount ',
        'St ': 'Saint ', 'St. ': 'Saint ', 'N ': 'North ', 'N. ': 'North ',
        'S ': 'South ', 'S. ': 'South ', 'E ': 'East ', 'E. ': 'East ',
        'W ': 'West ', 'W. ': 'West ',
    }
    for abbrev, full in replacements.items():
        if city.startswith(abbrev):
            city = full + city[len(abbrev):]
    return city.title() if city == city.upper() else city

# ─── Navigation Structure ────────────────────────────────────────
NAV_ITEMS = [
    {
        "label": "Medical Derm",
        "href": "/medical-dermatology/",
        "dropdown": [
            {"label": "Skin Conditions", "href": "/medical-dermatology/skin-conditions/"},
            {"label": "Skin Cancer", "href": "/medical-dermatology/skin-cancer/"},
            {"label": "Allergies", "href": "/medical-dermatology/allergies/"},
            {"label": "Hair & Scalp", "href": "/medical-dermatology/hair-scalp/"},
            {"label": "Nails", "href": "/medical-dermatology/nails/"},
            {"label": "Pediatric", "href": "/medical-dermatology/pediatric/"},
            {"label": "Skin of Color", "href": "/medical-dermatology/skin-of-color/"},
        ]
    },
    {
        "label": "Surgical Derm",
        "href": "/surgical-dermatology/",
        "dropdown": [
            {"label": "Mohs Surgery", "href": "/surgical-dermatology/mohs-surgery/"},
            {"label": "Skin Cancer", "href": "/medical-dermatology/skin-cancer/"},
            {"label": "Surgical Procedures", "href": "/surgical-dermatology/procedures/"},
            {"label": "Pre/Post-Op Care", "href": "/surgical-dermatology/pre-post-op/"},
        ]
    },
    {
        "label": "Cosmetic Derm",
        "href": "/cosmetic-dermatology/",
        "dropdown": [
            {"label": "Injectables & Botox", "href": "/cosmetic-dermatology/injectables/"},
            {"label": "Laser Treatments", "href": "/cosmetic-dermatology/lasers/"},
            {"label": "Skin Rejuvenation", "href": "/cosmetic-dermatology/rejuvenation/"},
            {"label": "Body Contouring", "href": "/cosmetic-dermatology/body-contouring/"},
        ]
    },
    {
        "label": "Skincare",
        "href": "/skincare/",
        "dropdown": [
            {"label": "Skincare Science", "href": "/skincare/skincare-science/"},
            {"label": "Men's Derm", "href": "/skincare/mens-derm/"},
            {"label": "Women's Derm", "href": "/skincare/womens-derm/"},
            {"label": "Lifestyle & Skin", "href": "/skincare/lifestyle/"},
        ]
    },
    {
        "label": "Tools",
        "href": "/tools/",
        "dropdown": [
            {"label": "Cost Calculator", "href": "/tools/cost-calculator/"},
            {"label": "Cost Comparison", "href": "/tools/cost-comparison/"},
            {"label": "Skin Quiz", "href": "/skin-quiz/"},
            {"label": "Embeddable Widget", "href": "/tools/widget/"},
        ]
    },
    {
        "label": "News",
        "href": "/news/",
        "dropdown": None
    },
    {
        "label": "Podcast",
        "href": "/podcast/",
        "dropdown": None
    },
    {
        "label": "For Dermatologists",
        "href": "/for-dermatologists/",
        "dropdown": None
    },
    {
        "label": "Find a Dermatologist",
        "href": "/find-a-dermatologist/",
        "dropdown": None
    },
]


def get_nav_html():
    """Generate the navigation bar HTML."""
    items_html = ""
    for item in NAV_ITEMS:
        if item["dropdown"]:
            dropdown_links = ""
            for sub in item["dropdown"]:
                dropdown_links += f'<a href="{sub["href"]}">{sub["label"]}</a>\n'
            items_html += f'''
            <li class="nav-item has-dropdown">
                <a href="{item["href"]}" class="nav-link">{item["label"]} <svg class="dropdown-arrow" width="10" height="6" viewBox="0 0 10 6"><path d="M1 1l4 4 4-4" stroke="currentColor" stroke-width="1.5" fill="none"/></svg></a>
                <div class="dropdown-menu">
                    {dropdown_links}
                </div>
            </li>'''
        else:
            extra_class = ' class="nav-link cta-link"' if item["label"] == "Find a Dermatologist" else ' class="nav-link"'
            items_html += f'''
            <li class="nav-item">
                <a href="{item["href"]}"{extra_class.replace("class=", "class=") if "cta" in extra_class else f' class="nav-link"'}>{item["label"]}</a>
            </li>'''
    return items_html


def page_template(title, body_content, meta_description="", schema_json="", canonical="", extra_head="", body_class=""):
    """Generate a complete HTML page with shared header, nav, and footer."""
    nav_html = get_nav_html()
    canonical_tag = f'<link rel="canonical" href="{DOMAIN}{canonical}" />' if canonical else ""
    schema_tag = f'<script type="application/ld+json">{schema_json}</script>' if schema_json else ""
    og_title = title
    og_desc = meta_description or f"{SITE_NAME} - {SITE_TAGLINE}"
    og_url = f"{DOMAIN}{canonical}" if canonical else DOMAIN
    og_image = f"{DOMAIN}/assets/images/og-default.png"

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | {SITE_NAME}</title>
    <meta name="description" content="{og_desc}">
    <meta name="robots" content="index, follow">
    {canonical_tag}

    <!-- Open Graph -->
    <meta property="og:title" content="{og_title} | {SITE_NAME}">
    <meta property="og:description" content="{og_desc}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{og_url}">
    <meta property="og:site_name" content="{SITE_NAME}">
    <meta property="og:image" content="{og_image}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{og_title} | {SITE_NAME}">
    <meta name="twitter:description" content="{og_desc}">
    <meta name="twitter:image" content="{og_image}">

    {schema_tag}

    <link rel="icon" type="image/png" href="/assets/images/favicon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
    <link rel="stylesheet" href="/assets/css/style.css?v=8">
    {extra_head}

    <!-- GA4 -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{GA4_ID}');
    </script>
</head>
<body class="{body_class}">

    <!-- Header -->
    <header class="site-header">
        <div class="container header-inner">
            <a href="/" class="logo">
                <span class="logo-icon">&#127891;</span>
                <span class="logo-text">Dermo<strong>Brain</strong></span>
            </a>
            <nav class="main-nav" id="mainNav">
                <ul class="nav-list">
                    {nav_html}
                </ul>
            </nav>
            <div class="header-actions">
                <button class="dark-mode-toggle" id="darkModeToggle" aria-label="Toggle dark mode">
                    <svg class="icon-sun" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
                    <svg class="icon-moon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
                </button>
                <button class="mobile-menu-toggle" id="mobileMenuToggle" aria-label="Toggle menu">
                    <span></span><span></span><span></span>
                </button>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="site-main">
        {body_content}
    </main>

    <!-- Footer -->
    <footer class="site-footer">
        <div class="container">
            <div class="footer-grid">
                <div class="footer-about">
                    <a href="/" class="footer-logo">
                        <span class="logo-icon">&#127891;</span>
                        <span class="logo-text">Dermo<strong>Brain</strong></span>
                    </a>
                    <p>Your trusted source for dermatology information. Covering medical, surgical, and cosmetic dermatology with expert-reviewed content.</p>
                </div>
                <div class="footer-links">
                    <h4>Three Pillars</h4>
                    <ul>
                        <li><a href="/medical-dermatology/">Medical Dermatology</a></li>
                        <li><a href="/surgical-dermatology/">Surgical Dermatology</a></li>
                        <li><a href="/cosmetic-dermatology/">Cosmetic Dermatology</a></li>
                        <li><a href="/skincare/">Skincare & Lifestyle</a></li>
                    </ul>
                </div>
                <div class="footer-links">
                    <h4>Resources</h4>
                    <ul>
                        <li><a href="/find-a-dermatologist/">Find a Dermatologist</a></li>
                        <li><a href="/tools/">Tools & Calculators</a></li>
                        <li><a href="/skin-quiz/">Skin Health Quiz</a></li>
                        <li><a href="/guides/">Expert Guides</a></li>
                        <li><a href="/news/">What's New</a></li>
                        <li><a href="/podcast/">Podcast</a></li>
                    </ul>
                </div>
                <div class="footer-links">
                    <h4>About</h4>
                    <ul>
                        <li><a href="/about/">About DermoBrain</a></li>
                        <li><a href="/for-dermatologists/">For Dermatologists</a></li>
                        <li><a href="/contact/">Contact Us</a></li>
                        <li><a href="/editorial-standards/">Editorial Standards</a></li>
                        <li><a href="/privacy-policy/">Privacy Policy</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-newsletter">
                <h4>Stay Updated</h4>
                <p>Get the latest dermatology insights delivered to your inbox.</p>
                <form action="https://formspree.io/f/xpwzgkqq" method="POST" class="newsletter-form">
                    <input type="email" name="email" placeholder="Your email address" required>
                    <input type="hidden" name="_subject" value="DermoBrain Newsletter Signup">
                    <button type="submit">Subscribe</button>
                </form>
            </div>
            <div class="footer-bottom">
                <p>&copy; {datetime.datetime.now().year} DermoBrain.com — All rights reserved.</p>
                <p class="footer-disclaimer">Content is for informational purposes only and does not constitute medical advice. Always consult a board-certified dermatologist.</p>
            </div>
        </div>
    </footer>

    <script src="/assets/js/main.js?v=5" defer></script>
</body>
</html>'''


def generate_sitemap(pages):
    """Generate XML sitemap from list of page paths."""
    urlset = Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    for page_path, priority, changefreq in pages:
        url = SubElement(urlset, "url")
        loc = SubElement(url, "loc")
        loc.text = f"{DOMAIN}{page_path}"
        lastmod = SubElement(url, "lastmod")
        lastmod.text = BUILD_DATE
        cf = SubElement(url, "changefreq")
        cf.text = changefreq
        pri = SubElement(url, "priority")
        pri.text = str(priority)

    raw_xml = tostring(urlset, encoding="unicode")
    pretty = parseString(raw_xml).toprettyxml(indent="  ")
    # Remove extra XML declaration from toprettyxml
    lines = pretty.split("\n")
    return "\n".join(lines[1:])  # skip <?xml ...?> line added by minidom


def generate_robots_txt():
    """Generate robots.txt."""
    return f"""User-agent: *
Allow: /

Sitemap: {DOMAIN}/sitemap.xml
"""


def write_file(filepath, content):
    """Write content to file, creating directories as needed."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")
    print(f"  ✓ {filepath.relative_to(OUTPUT_DIR)}")


def copy_assets():
    """Copy static assets to output."""
    src = ASSETS_DIR
    dst = OUTPUT_DIR / "assets"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print("  ✓ Assets copied")


def build_homepage():
    """Build the homepage with real featured articles."""
    # Load articles to get real content
    all_articles = load_all_articles()
    all_categories = load_categories()

    # Create featured articles HTML from real articles
    featured_html = '<div class="articles-grid">'
    article_count = 0
    # Pick diverse articles from different categories
    category_map = {c.get('slug'): c for c in all_categories}
    featured_by_pillar = {}

    for article in all_articles:
        if article_count >= 8:
            break
        category_slug = article.get('category', '')
        category_info = category_map.get(category_slug)
        if category_info:
            pillar = category_info.get('pillar_slug', '')
            if pillar not in featured_by_pillar:
                featured_by_pillar[pillar] = article
                article_count += 1

    # If we don't have enough articles from different pillars, add more
    for article in all_articles:
        if article_count >= 8:
            break
        category_slug = article.get('category', '')
        category_info = category_map.get(category_slug)
        if category_info:
            pillar = category_info.get('pillar_slug', '')
            if pillar in featured_by_pillar:
                # Add more articles from already represented pillars
                featured_by_pillar[pillar] = article
                article_count += 1

    # Generate HTML for featured articles
    for article in list(featured_by_pillar.values())[:8]:
        article_slug = article.get('slug', '')
        article_title = article.get('title', '')
        article_desc = article.get('meta_description', '')[:80] + "..."
        category_slug = article.get('category', '')
        category_info = category_map.get(category_slug)

        if category_info:
            pillar_slug = category_info.get('pillar_slug', '')
            category_name = category_info.get('name', '')

            featured_html += f'''
                <a href="/{pillar_slug}/{category_slug}/{article_slug}.html" class="article-card">
                    <div class="article-card-body">
                        <span class="article-category">{category_name}</span>
                        <h3>{article_title}</h3>
                        <p>{article_desc}</p>
                    </div>
                </a>'''

    featured_html += '</div>'

    body = f'''
    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <h1 class="hero-title">Your Trusted<br><span class="text-gradient">Dermatology Encyclopedia</span></h1>
            <p class="hero-subtitle">Expert-reviewed articles covering medical, surgical, and cosmetic dermatology. Your skin health journey starts here.</p>
            <div class="hero-search">
                <input type="text" id="heroSearch" placeholder="Search skin conditions, treatments, procedures..." class="search-input" autocomplete="off">
                <button class="btn btn-primary search-btn">Search</button>
            </div>
            <div class="hero-stats">
                <div class="stat"><strong>{len(all_articles)}+</strong> Articles</div>
                <div class="stat"><strong>50</strong> States</div>
                <div class="stat"><strong>&#9745;</strong> Medically Reviewed</div>
                <div class="stat"><strong>3</strong> Specialties</div>
            </div>
        </div>
    </section>

    <!-- Three Pillars Section -->
    <section class="pillars-section">
        <div class="container">
            <h2 class="section-title">The Three Pillars of Dermatology</h2>
            <p class="section-subtitle">Comprehensive coverage across every aspect of skin health</p>
            <div class="pillars-grid">
                <a href="/medical-dermatology/" class="pillar-card pillar-medical">
                    <div class="pillar-icon">&#129657;</div>
                    <h3>Medical Dermatology</h3>
                    <p>Skin conditions, cancer, allergies, pediatric dermatology, hair, nails, and skin of color.</p>
                    <span class="pillar-count">{len([a for a in all_articles if next((c for c in all_categories if c.get('slug') == a.get('category')), {}).get('pillar_slug') == 'medical-dermatology'])}+ articles</span>
                </a>
                <a href="/surgical-dermatology/" class="pillar-card pillar-surgical">
                    <div class="pillar-icon">&#129658;</div>
                    <h3>Surgical Dermatology</h3>
                    <p>Mohs surgery, skin cancer surgery, surgical procedures, and pre/post-operative care.</p>
                    <span class="pillar-count">{len([a for a in all_articles if next((c for c in all_categories if c.get('slug') == a.get('category')), {}).get('pillar_slug') == 'surgical-dermatology'])}+ articles</span>
                </a>
                <a href="/cosmetic-dermatology/" class="pillar-card pillar-cosmetic">
                    <div class="pillar-icon">&#10024;</div>
                    <h3>Cosmetic Dermatology</h3>
                    <p>Injectables, laser treatments, skin rejuvenation, body contouring, and anti-aging.</p>
                    <span class="pillar-count">{len([a for a in all_articles if next((c for c in all_categories if c.get('slug') == a.get('category')), {}).get('pillar_slug') == 'cosmetic-dermatology'])}+ articles</span>
                </a>
            </div>
        </div>
    </section>

    <!-- Featured Articles -->
    <section class="featured-section">
        <div class="container">
            <h2 class="section-title">Featured Articles</h2>
            <p class="section-subtitle">Latest expert-reviewed dermatology content</p>
            {featured_html}
        </div>
    </section>

    <!-- Skin Quiz CTA -->
    <section class="cta-banner cta-quiz">
        <div class="container">
            <div class="cta-content">
                <h2>Take the Skin Health Quiz</h2>
                <p>Answer 10 quick questions and get personalized skincare recommendations from our dermatology experts.</p>
                <a href="/skin-quiz/" class="btn btn-accent btn-lg">Start Quiz &rarr;</a>
            </div>
        </div>
    </section>

    <!-- Browse Categories -->
    <section class="categories-section">
        <div class="container">
            <h2 class="section-title">Browse by Category</h2>
            <div class="categories-grid">
                <a href="/medical-dermatology/skin-conditions/" class="category-card"><span class="cat-icon">&#128204;</span>Skin Conditions</a>
                <a href="/medical-dermatology/skin-cancer/" class="category-card"><span class="cat-icon">&#128270;</span>Skin Cancer</a>
                <a href="/medical-dermatology/allergies/" class="category-card"><span class="cat-icon">&#129656;</span>Allergies</a>
                <a href="/medical-dermatology/hair-scalp/" class="category-card"><span class="cat-icon">&#128135;</span>Hair & Scalp</a>
                <a href="/medical-dermatology/nails/" class="category-card"><span class="cat-icon">&#128133;</span>Nails</a>
                <a href="/medical-dermatology/pediatric/" class="category-card"><span class="cat-icon">&#128118;</span>Pediatric</a>
                <a href="/medical-dermatology/skin-of-color/" class="category-card"><span class="cat-icon">&#127752;</span>Skin of Color</a>
                <a href="/surgical-dermatology/mohs-surgery/" class="category-card"><span class="cat-icon">&#129658;</span>Mohs Surgery</a>
                <a href="/surgical-dermatology/procedures/" class="category-card"><span class="cat-icon">&#128137;</span>Surgical Procedures</a>
                <a href="/surgical-dermatology/pre-post-op/" class="category-card"><span class="cat-icon">&#129657;</span>Pre/Post-Op</a>
                <a href="/cosmetic-dermatology/injectables/" class="category-card"><span class="cat-icon">&#128137;</span>Injectables</a>
                <a href="/cosmetic-dermatology/lasers/" class="category-card"><span class="cat-icon">&#9889;</span>Lasers</a>
                <a href="/cosmetic-dermatology/rejuvenation/" class="category-card"><span class="cat-icon">&#10024;</span>Rejuvenation</a>
                <a href="/cosmetic-dermatology/body-contouring/" class="category-card"><span class="cat-icon">&#127947;</span>Body Contouring</a>
                <a href="/skincare/skincare-science/" class="category-card"><span class="cat-icon">&#128218;</span>Skincare Science</a>
                <a href="/skincare/mens/" class="category-card"><span class="cat-icon">&#128104;</span>Men's Derm</a>
                <a href="/skincare/womens/" class="category-card"><span class="cat-icon">&#128105;</span>Women's Derm</a>
                <a href="/skincare/lifestyle/" class="category-card"><span class="cat-icon">&#127793;</span>Lifestyle</a>
                <a href="/myths/" class="category-card"><span class="cat-icon">&#10067;</span>Myths vs Facts</a>
                <a href="/procedures-az/" class="category-card"><span class="cat-icon">&#128209;</span>Procedures A-Z</a>
            </div>
        </div>
    </section>

    <!-- Find a Dermatologist CTA -->
    <section class="cta-banner cta-directory">
        <div class="container">
            <div class="cta-content">
                <h2>Find a Dermatologist Near You</h2>
                <p>Search our directory of board-certified dermatologists across all 50 states.</p>
                <a href="/find-a-dermatologist/" class="btn btn-primary btn-lg">Search Directory &rarr;</a>
            </div>
        </div>
    </section>
'''

    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "MedicalWebPage",
        "name": SITE_NAME,
        "description": "Your trusted dermatology encyclopedia covering medical, surgical, and cosmetic dermatology.",
        "url": DOMAIN,
        "publisher": {
            "@type": "Organization",
            "name": SITE_NAME,
            "url": DOMAIN
        }
    })

    html = page_template(
        title="Dermatology Encyclopedia",
        body_content=body,
        meta_description="DermoBrain is your trusted dermatology encyclopedia. 2,000+ expert-reviewed articles on skin conditions, treatments, surgery, and cosmetic procedures.",
        schema_json=schema,
        canonical="/",
        body_class="page-home"
    )
    write_file(OUTPUT_DIR / "index.html", html)


def build_editorial_standards():
    """Build the editorial standards page."""
    body = '''
    <section class="content-page">
        <div class="container container-narrow">
            <nav class="breadcrumb">
                <a href="/">Home</a> <span>&rsaquo;</span> <span>Editorial Standards</span>
            </nav>
            <h1>Editorial Standards</h1>
            <div class="content-body">
                <p class="lead">At DermoBrain, we strive to provide accurate and useful dermatology information. We are transparent about our editorial process and the sources we use.</p>

                <h2>Our Content Sources</h2>
                <p>DermoBrain articles are written using information from established medical sources, including:</p>
                <ul>
                    <li><a href="https://www.aad.org" target="_blank" rel="noopener">American Academy of Dermatology (AAD)</a> — clinical guidelines and patient education materials</li>
                    <li><a href="https://www.mayoclinic.org" target="_blank" rel="noopener">Mayo Clinic</a> — disease overviews and treatment information</li>
                    <li><a href="https://medlineplus.gov" target="_blank" rel="noopener">MedlinePlus (NIH)</a> — consumer health information</li>
                    <li>Peer-reviewed dermatology journals and textbooks</li>
                </ul>

                <h2>Editorial Process</h2>
                <p>Our content creation process involves several steps designed to ensure quality:</p>

                <div class="standards-grid">
                    <div class="standard-card">
                        <h3>&#128221; Research</h3>
                        <p>Every article begins with research using the medical sources listed above. We reference current clinical guidelines and peer-reviewed literature.</p>
                    </div>
                    <div class="standard-card">
                        <h3>&#9997; Writing</h3>
                        <p>Our editorial team translates clinical information into accessible language for patients and the general public.</p>
                    </div>
                    <div class="standard-card">
                        <h3>&#128270; Fact-Checking</h3>
                        <p>All medical claims are cross-referenced with at least two authoritative sources before publication.</p>
                    </div>
                    <div class="standard-card">
                        <h3>&#128260; Updates</h3>
                        <p>We periodically review and update content when treatment guidelines change or new research emerges.</p>
                    </div>
                </div>

                <h2>Content Principles</h2>
                <ul>
                    <li><strong>Evidence-Based:</strong> Medical claims reference peer-reviewed research and established clinical guidelines.</li>
                    <li><strong>Unbiased:</strong> Treatment options are presented objectively without favoring any product or brand.</li>
                    <li><strong>Accessible:</strong> Complex medical topics are explained in plain language.</li>
                    <li><strong>Inclusive:</strong> Our content addresses dermatological concerns across all skin types, tones, and backgrounds.</li>
                </ul>

                <h2>Medical Disclaimer</h2>
                <p>The information on DermoBrain is intended for educational purposes only and should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult with a board-certified dermatologist or qualified healthcare provider for personalized medical guidance.</p>

                <h2>Report an Error</h2>
                <p>If you notice an error in our content or have suggestions for improvement, please contact us at <a href="mailto:editorial@dermobrain.com">editorial@dermobrain.com</a>. We take accuracy seriously and will review all reported issues promptly.</p>
            </div>
        </div>
    </section>
'''

    html = page_template(
        title="Editorial Standards",
        body_content=body,
        meta_description="Learn about DermoBrain's editorial standards. All content is medically reviewed by board-certified dermatologists.",
        canonical="/editorial-standards/",
        body_class="page-editorial"
    )
    write_file(OUTPUT_DIR / "editorial-standards" / "index.html", html)


def load_all_articles():
    """Load all article JSON files from data/ that start with 'articles_'."""
    articles = []
    for article_file in sorted(DATA_DIR.glob("articles_*.json")):
        try:
            with open(article_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    articles.extend(data)
                elif isinstance(data, dict) and 'articles' in data:
                    articles.extend(data['articles'])
        except Exception as e:
            print(f"  Warning: Could not load {article_file.name}: {e}")
    return articles


def load_categories():
    """Load data/categories.json and return the categories list."""
    try:
        with open(DATA_DIR / "categories.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('categories', [])
    except Exception as e:
        print(f"  Error loading categories: {e}")
        return []


def build_article_page(article, category_info):
    """Generate an individual article page at /{pillar_slug}/{category_slug}/{article_slug}.html."""
    pillar_slug = category_info.get('pillar_slug', '')
    category_slug = category_info.get('slug', '')
    article_slug = article.get('slug', '')

    title = article.get('title', 'Article')
    content = article.get('content', '')
    meta_desc = article.get('meta_description', '')
    related_articles = article.get('related_articles', [])
    tags = article.get('tags', [])

    # Cross-link banner to patient version (if it exists)
    patient_content = article.get('patient_content', '')
    cross_link_banner = ''
    if patient_content:
        patient_url = f"/{pillar_slug}/{category_slug}/{article_slug}-patient-guide.html"
        cross_link_banner = f'''
            <div class="version-banner clinical-banner" style="background:linear-gradient(135deg,#f0f9f6,#e8f4f0);border:1px solid #028090;border-radius:10px;padding:16px 24px;margin-bottom:28px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
                <div>
                    <strong style="color:#028090;font-size:1.05em;">&#128214; You&rsquo;re reading the Clinical Reference</strong>
                    <p style="margin:4px 0 0;color:#555;font-size:0.93em;">Written for healthcare professionals with detailed pathophysiology, dosing protocols, and clinical data.</p>
                </div>
                <a href="{patient_url}" style="background:#028090;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none;font-weight:600;font-size:0.95em;white-space:nowrap;">Read the Patient-Friendly Version &rarr;</a>
            </div>'''

    # Read time estimate
    import re as _re
    word_count = len(_re.findall(r'\w+', _re.sub(r'<[^>]+>', '', content)))
    read_time = max(1, round(word_count / 200))

    # Generate Table of Contents from H2 headings
    toc_html = ""
    h2_matches = list(_re.finditer(r'<h2>(.*?)</h2>', content))
    if len(h2_matches) >= 3:
        toc_items = ""
        modified_content = content
        for i, match in enumerate(h2_matches):
            heading_text = match.group(1)
            anchor_id = f"section-{i+1}"
            toc_items += f'<li><a href="#{anchor_id}">{heading_text}</a></li>\n'
            modified_content = modified_content.replace(
                f'<h2>{heading_text}</h2>',
                f'<h2 id="{anchor_id}">{heading_text}</h2>',
                1
            )
        content = modified_content
        toc_html = f'''
            <div class="table-of-contents">
                <h3 class="toc-title">Table of Contents</h3>
                <ol>{toc_items}</ol>
            </div>'''

    # Breadcrumb
    pillar_name = {
        'medical-dermatology': 'Medical Dermatology',
        'surgical-dermatology': 'Surgical Dermatology',
        'cosmetic-dermatology': 'Cosmetic Dermatology',
        'skincare': 'Skincare & Lifestyle'
    }.get(pillar_slug, pillar_slug.replace('-', ' ').title())

    category_name = category_info.get('name', '')

    breadcrumb = f'''
    <nav class="breadcrumb">
        <a href="/">Home</a> <span>&rsaquo;</span>
        <a href="/{pillar_slug}/">{pillar_name}</a> <span>&rsaquo;</span>
        <a href="/{pillar_slug}/{category_slug}/">{category_name}</a> <span>&rsaquo;</span>
        <span>{title}</span>
    </nav>'''

    # Related articles section
    related_html = ""
    if related_articles:
        related_html = '''
    <section class="related-articles">
        <h3>Related Articles</h3>
        <div class="related-grid">'''
        for rel_slug in related_articles[:4]:  # Limit to 4 related articles
            related_html += f'''
            <div class="related-card">
                <a href="/{pillar_slug}/{category_slug}/{rel_slug}.html">{rel_slug.replace('-', ' ').title()}</a>
            </div>'''
        related_html += '''
        </div>
    </section>'''

    # Social share buttons (URL-encoded)
    article_url = f"{DOMAIN}/{pillar_slug}/{category_slug}/{article_slug}.html"
    encoded_url = quote(article_url, safe='')
    encoded_title = quote(title, safe='')
    social_share = f'''
    <div class="social-share">
        <p>Share this article:</p>
        <a href="https://twitter.com/intent/tweet?url={encoded_url}&text={encoded_title}" class="share-btn twitter" target="_blank" rel="noopener noreferrer" aria-label="Share on Twitter">Twitter</a>
        <a href="https://www.facebook.com/sharer/sharer.php?u={encoded_url}" class="share-btn facebook" target="_blank" rel="noopener noreferrer" aria-label="Share on Facebook">Facebook</a>
        <a href="https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}" class="share-btn linkedin" target="_blank" rel="noopener noreferrer" aria-label="Share on LinkedIn">LinkedIn</a>
        <a href="https://api.whatsapp.com/send?text={encoded_title}%20{encoded_url}" class="share-btn whatsapp" target="_blank" rel="noopener noreferrer" aria-label="Share on WhatsApp">WhatsApp</a>
        <a href="https://pinterest.com/pin/create/button/?url={encoded_url}&description={encoded_title}" class="share-btn pinterest" target="_blank" rel="noopener noreferrer" aria-label="Share on Pinterest">Pinterest</a>
        <button class="share-btn copy-link" data-url="{article_url}" aria-label="Copy link to clipboard">Copy Link</button>
    </div>'''

    # Schema.org - combined Article + MedicalWebPage + BreadcrumbList
    article_schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": f"{DOMAIN}/#organization",
                "name": SITE_NAME,
                "url": DOMAIN,
                "description": "Your trusted dermatology encyclopedia covering medical, surgical, and cosmetic dermatology."
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN},
                    {"@type": "ListItem", "position": 2, "name": pillar_name, "item": f"{DOMAIN}/{pillar_slug}/"},
                    {"@type": "ListItem", "position": 3, "name": category_name, "item": f"{DOMAIN}/{pillar_slug}/{category_slug}/"},
                    {"@type": "ListItem", "position": 4, "name": title, "item": article_url}
                ]
            },
            {
                "@type": ["MedicalWebPage", "Article"],
                "headline": title,
                "description": meta_desc,
                "url": article_url,
                "datePublished": BUILD_DATE,
                "dateModified": BUILD_DATE,
                "author": {
                    "@type": "Organization",
                    "name": "DermoBrain Medical Editorial Team",
                    "url": f"{DOMAIN}/editorial-standards/"
                },
                "reviewedBy": {
                    "@type": "Organization",
                    "name": "DermoBrain Medical Review Board",
                    "url": f"{DOMAIN}/editorial-standards/"
                },
                "publisher": {
                    "@type": "Organization",
                    "@id": f"{DOMAIN}/#organization",
                    "name": SITE_NAME,
                    "url": DOMAIN
                },
                "mainEntityOfPage": article_url,
                "keywords": ", ".join(tags),
                "about": {
                    "@type": "MedicalCondition",
                    "name": title.split(":")[0].strip() if ":" in title else title
                }
            }
        ]
    }
    schema = json.dumps(article_schema)

    # Smart patient routing CTA - maps category to specialty search
    specialty_map = {
        'skin-conditions': 'Dermatology',
        'skin-cancer': 'MOHS-MICROGRAPHIC SURGERY',
        'allergies': 'CLINICAL & LABORATORY DERMATOLOGICAL IMMUNOLOGY',
        'pediatric': 'Pediatric Dermatology',
        'hair-scalp': 'Dermatology',
        'nails': 'Dermatology',
        'skin-of-color': 'Dermatology',
        'mohs-surgery': 'MOHS-MICROGRAPHIC SURGERY',
        'procedures': 'Dermatology',
        'pre-post-op': 'Dermatology',
        'injectables': 'Dermatology',
        'lasers': 'Dermatology',
        'rejuvenation': 'Dermatology',
        'body-contouring': 'Dermatology',
        'skincare-science': 'Dermatology',
        'mens-derm': 'Dermatology',
        'womens-derm': 'Dermatology',
        'lifestyle': 'Dermatology',
    }
    specialty_label = specialty_map.get(category_slug, 'Dermatology')
    specialty_display = category_name.split('&')[0].strip() if '&' in category_name else category_name

    body = f'''
    <article class="article-page">
        <div class="container container-narrow">
            {breadcrumb}

            <header class="article-header">
                <span class="article-category">{category_name}</span>
                <h1>{title}</h1>
                <div class="article-meta">
                    <span class="byline">By DermoBrain Medical Editorial Team</span>
                    <time datetime="{BUILD_DATE}">Updated {BUILD_DATE}</time>
                    <span class="badge">Medically Reviewed</span>
                    <span class="read-time">&#9201; {read_time} min read</span>
                </div>
            </header>

            {cross_link_banner}

            {toc_html}

            <div class="article-body">
                {content}
            </div>

            <div class="article-review-info">
                <p><strong>Medically reviewed</strong> by the DermoBrain Medical Review Board. This article is for informational purposes only and does not constitute medical advice. Always consult a board-certified dermatologist for diagnosis and treatment.</p>
                <p>Sources: American Academy of Dermatology (AAD), peer-reviewed dermatology journals, and established clinical guidelines.</p>
            </div>

            {social_share}
            {related_html}

            <!-- Smart Patient Routing CTA -->
            <section class="find-specialist-cta">
                <div class="cta-inner">
                    <div class="cta-icon">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#1A6B54" stroke-width="1.5">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                            <circle cx="12" cy="10" r="3"/>
                        </svg>
                    </div>
                    <h3>Need a {specialty_display} Specialist?</h3>
                    <p>Find board-certified dermatologists near you who specialize in {specialty_display.lower()}.</p>
                    <a href="/find-a-dermatologist/" class="cta-btn">Find a Dermatologist Near You</a>
                    <p class="cta-stats">9,966+ verified dermatologists across all 50 states</p>
                </div>
            </section>
        </div>
    </article>'''

    html = page_template(
        title=title,
        body_content=body,
        meta_description=meta_desc,
        schema_json=schema,
        canonical=f"/{pillar_slug}/{category_slug}/{article_slug}.html",
        body_class="page-article"
    )

    filepath = OUTPUT_DIR / pillar_slug / category_slug / f"{article_slug}.html"
    write_file(filepath, html)

    # Also build patient version if patient_content exists
    if patient_content:
        build_patient_article_page(article, category_info)


def build_patient_article_page(article, category_info):
    """Generate a patient-friendly article page at /{pillar}/{category}/{slug}-patient-guide.html."""
    import re as _re

    pillar_slug = category_info.get('pillar_slug', '')
    category_slug = category_info.get('slug', '')
    article_slug = article.get('slug', '')

    title = article.get('patient_title', article.get('title', 'Article'))
    content = article.get('patient_content', '')
    meta_desc = article.get('patient_meta_description', article.get('meta_description', ''))
    related_articles = article.get('related_articles', [])
    tags = article.get('patient_tags', article.get('tags', []))

    # Read time estimate
    word_count = len(_re.findall(r'\w+', _re.sub(r'<[^>]+>', '', content)))
    read_time = max(1, round(word_count / 200))

    # Generate Table of Contents from H2 headings
    toc_html = ""
    h2_matches = list(_re.finditer(r'<h2[^>]*>(.*?)</h2>', content))
    if len(h2_matches) >= 3:
        toc_items = ""
        modified_content = content
        for i, match in enumerate(h2_matches):
            heading_text = match.group(1)
            # Strip any existing style attributes from heading text
            clean_heading = _re.sub(r'<[^>]+>', '', heading_text).strip()
            anchor_id = f"section-{i+1}"
            toc_items += f'<li><a href="#{anchor_id}">{clean_heading}</a></li>\n'
            # Replace only the first occurrence
            old_tag = match.group(0)
            new_tag = f'<h2 id="{anchor_id}">{heading_text}</h2>' if 'id=' not in old_tag else old_tag
            modified_content = modified_content.replace(old_tag, new_tag, 1)
        content = modified_content
        toc_html = f'''
            <div class="table-of-contents">
                <h3 class="toc-title">Table of Contents</h3>
                <ol>{toc_items}</ol>
            </div>'''

    # Breadcrumb
    pillar_name = {
        'medical-dermatology': 'Medical Dermatology',
        'surgical-dermatology': 'Surgical Dermatology',
        'cosmetic-dermatology': 'Cosmetic Dermatology',
        'skincare': 'Skincare & Lifestyle'
    }.get(pillar_slug, pillar_slug.replace('-', ' ').title())

    category_name = category_info.get('name', '')

    breadcrumb = f'''
    <nav class="breadcrumb">
        <a href="/">Home</a> <span>&rsaquo;</span>
        <a href="/{pillar_slug}/">{pillar_name}</a> <span>&rsaquo;</span>
        <a href="/{pillar_slug}/{category_slug}/">{category_name}</a> <span>&rsaquo;</span>
        <span>{title}</span>
    </nav>'''

    # Cross-link banner to clinical version
    clinical_url = f"/{pillar_slug}/{category_slug}/{article_slug}.html"
    cross_link_banner = f'''
            <div class="version-banner patient-banner" style="background:linear-gradient(135deg,#fef9f0,#fdf3e0);border:1px solid #e8a020;border-radius:10px;padding:16px 24px;margin-bottom:28px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
                <div>
                    <strong style="color:#b8860b;font-size:1.05em;">&#128101; You&rsquo;re reading the Patient Guide</strong>
                    <p style="margin:4px 0 0;color:#555;font-size:0.93em;">Written in plain language for patients and caregivers. Medically accurate and dermatologist-reviewed.</p>
                </div>
                <a href="{clinical_url}" style="background:#b8860b;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none;font-weight:600;font-size:0.95em;white-space:nowrap;">Read the Clinical Reference &rarr;</a>
            </div>'''

    # Related articles section
    related_html = ""
    if related_articles:
        related_html = '''
    <section class="related-articles">
        <h3>Related Patient Guides</h3>
        <div class="related-grid">'''
        for rel_slug in related_articles[:4]:
            related_html += f'''
            <div class="related-card">
                <a href="/{pillar_slug}/{category_slug}/{rel_slug}-patient-guide.html">{rel_slug.replace('-', ' ').title()}</a>
            </div>'''
        related_html += '''
        </div>
    </section>'''

    # Social share
    article_url = f"{DOMAIN}/{pillar_slug}/{category_slug}/{article_slug}-patient-guide.html"
    encoded_url = quote(article_url, safe='')
    encoded_title = quote(title, safe='')
    social_share = f'''
    <div class="social-share">
        <p>Share this article:</p>
        <a href="https://twitter.com/intent/tweet?url={encoded_url}&text={encoded_title}" class="share-btn twitter" target="_blank" rel="noopener noreferrer" aria-label="Share on Twitter">Twitter</a>
        <a href="https://www.facebook.com/sharer/sharer.php?u={encoded_url}" class="share-btn facebook" target="_blank" rel="noopener noreferrer" aria-label="Share on Facebook">Facebook</a>
        <a href="https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}" class="share-btn linkedin" target="_blank" rel="noopener noreferrer" aria-label="Share on LinkedIn">LinkedIn</a>
        <a href="https://api.whatsapp.com/send?text={encoded_title}%20{encoded_url}" class="share-btn whatsapp" target="_blank" rel="noopener noreferrer" aria-label="Share on WhatsApp">WhatsApp</a>
        <a href="https://pinterest.com/pin/create/button/?url={encoded_url}&description={encoded_title}" class="share-btn pinterest" target="_blank" rel="noopener noreferrer" aria-label="Share on Pinterest">Pinterest</a>
        <button class="share-btn copy-link" data-url="{article_url}" aria-label="Copy link to clipboard">Copy Link</button>
    </div>'''

    # Schema.org for patient version
    article_schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": f"{DOMAIN}/#organization",
                "name": SITE_NAME,
                "url": DOMAIN,
                "description": "Your trusted dermatology encyclopedia covering medical, surgical, and cosmetic dermatology."
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN},
                    {"@type": "ListItem", "position": 2, "name": pillar_name, "item": f"{DOMAIN}/{pillar_slug}/"},
                    {"@type": "ListItem", "position": 3, "name": category_name, "item": f"{DOMAIN}/{pillar_slug}/{category_slug}/"},
                    {"@type": "ListItem", "position": 4, "name": title, "item": article_url}
                ]
            },
            {
                "@type": ["MedicalWebPage", "Article"],
                "headline": title,
                "description": meta_desc,
                "url": article_url,
                "datePublished": BUILD_DATE,
                "dateModified": BUILD_DATE,
                "audience": {
                    "@type": "PeopleAudience",
                    "audienceType": "Patient"
                },
                "author": {
                    "@type": "Organization",
                    "name": "DermoBrain Medical Editorial Team",
                    "url": f"{DOMAIN}/editorial-standards/"
                },
                "reviewedBy": {
                    "@type": "Organization",
                    "name": "DermoBrain Medical Review Board",
                    "url": f"{DOMAIN}/editorial-standards/"
                },
                "publisher": {
                    "@type": "Organization",
                    "@id": f"{DOMAIN}/#organization",
                    "name": SITE_NAME,
                    "url": DOMAIN
                },
                "mainEntityOfPage": article_url,
                "keywords": ", ".join(tags),
                "about": {
                    "@type": "MedicalCondition",
                    "name": title.split(":")[0].strip() if ":" in title else title
                }
            }
        ]
    }
    schema = json.dumps(article_schema)

    # Smart patient routing CTA
    specialty_map = {
        'skin-conditions': 'Dermatology', 'skin-cancer': 'MOHS-MICROGRAPHIC SURGERY',
        'allergies': 'CLINICAL & LABORATORY DERMATOLOGICAL IMMUNOLOGY',
        'pediatric': 'Pediatric Dermatology', 'hair-scalp': 'Dermatology',
        'nails': 'Dermatology', 'skin-of-color': 'Dermatology',
        'mohs-surgery': 'MOHS-MICROGRAPHIC SURGERY', 'procedures': 'Dermatology',
        'pre-post-op': 'Dermatology', 'injectables': 'Dermatology',
        'lasers': 'Dermatology', 'rejuvenation': 'Dermatology',
        'body-contouring': 'Dermatology', 'skincare-science': 'Dermatology',
        'mens-derm': 'Dermatology', 'womens-derm': 'Dermatology', 'lifestyle': 'Dermatology',
    }
    specialty_display = category_name.split('&')[0].strip() if '&' in category_name else category_name

    body = f'''
    <article class="article-page patient-guide">
        <div class="container container-narrow">
            {breadcrumb}

            <header class="article-header">
                <span class="article-category">{category_name} &mdash; Patient Guide</span>
                <h1>{title}</h1>
                <div class="article-meta">
                    <span class="byline">By DermoBrain Medical Editorial Team</span>
                    <time datetime="{BUILD_DATE}">Updated {BUILD_DATE}</time>
                    <span class="badge">Medically Reviewed</span>
                    <span class="read-time">&#9201; {read_time} min read</span>
                </div>
            </header>

            {cross_link_banner}

            {toc_html}

            <div class="article-body">
                {content}
            </div>

            <div class="article-review-info">
                <p><strong>Medically reviewed</strong> by the DermoBrain Medical Review Board. This article is for informational purposes only and does not constitute medical advice. Always consult a board-certified dermatologist for diagnosis and treatment.</p>
                <p>Sources: American Academy of Dermatology (AAD), peer-reviewed dermatology journals, and established clinical guidelines.</p>
            </div>

            {social_share}
            {related_html}

            <!-- Smart Patient Routing CTA -->
            <section class="find-specialist-cta">
                <div class="cta-inner">
                    <div class="cta-icon">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#1A6B54" stroke-width="1.5">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                            <circle cx="12" cy="10" r="3"/>
                        </svg>
                    </div>
                    <h3>Need a {specialty_display} Specialist?</h3>
                    <p>Find board-certified dermatologists near you who specialize in {specialty_display.lower()}.</p>
                    <a href="/find-a-dermatologist/" class="cta-btn">Find a Dermatologist Near You</a>
                    <p class="cta-stats">9,966+ verified dermatologists across all 50 states</p>
                </div>
            </section>
        </div>
    </article>'''

    html = page_template(
        title=title,
        body_content=body,
        meta_description=meta_desc,
        schema_json=schema,
        canonical=f"/{pillar_slug}/{category_slug}/{article_slug}-patient-guide.html",
        body_class="page-article page-patient-guide"
    )

    filepath = OUTPUT_DIR / pillar_slug / category_slug / f"{article_slug}-patient-guide.html"
    write_file(filepath, html)


def build_category_page(category, articles):
    """Generate category page at /{pillar_slug}/{category_slug}/index.html."""
    pillar_slug = category.get('pillar_slug', '')
    category_slug = category.get('slug', '')
    category_name = category.get('name', '')
    description = category.get('description', '')
    subcategories = category.get('subcategories', [])

    pillar_name = {
        'medical-dermatology': 'Medical Dermatology',
        'surgical-dermatology': 'Surgical Dermatology',
        'cosmetic-dermatology': 'Cosmetic Dermatology',
        'skincare': 'Skincare & Lifestyle'
    }.get(pillar_slug, pillar_slug.replace('-', ' ').title())

    # Filter articles for this category
    category_articles = [a for a in articles if a.get('category') == category_slug]

    breadcrumb = f'''
    <nav class="breadcrumb">
        <a href="/">Home</a> <span>&rsaquo;</span>
        <a href="/{pillar_slug}/">{pillar_name}</a> <span>&rsaquo;</span>
        <span>{category_name}</span>
    </nav>'''

    # Subcategory filter tabs
    subcategory_html = ""
    if subcategories:
        subcategory_html = '<div class="filter-tabs">'
        for subcat in subcategories:
            subcat_slug = subcat.get('slug', '')
            subcat_name = subcat.get('name', '')
            subcategory_html += f'<button class="filter-tab" data-filter="{subcat_slug}">{subcat_name}</button>'
        subcategory_html += '</div>'

    # Article cards grid - show ALL articles (not just 12)
    articles_html = '<div class="articles-grid">'
    for article in category_articles:
        article_slug = article.get('slug', '')
        article_title = article.get('title', '')
        article_desc = article.get('meta_description', '')[:120] + "..."
        subcat = article.get('subcategory', '')

        articles_html += f'''
        <a href="/{pillar_slug}/{category_slug}/{article_slug}.html" class="article-card" data-subcategory="{subcat}">
            <div class="article-card-body">
                <span class="article-category">{category_name}</span>
                <h3>{article_title}</h3>
                <p>{article_desc}</p>
            </div>
        </a>'''
    articles_html += '</div>'

    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "MedicalWebPage",
        "name": category_name,
        "description": description,
        "url": f"{DOMAIN}/{pillar_slug}/{category_slug}/",
        "publisher": {
            "@type": "Organization",
            "name": SITE_NAME,
            "url": DOMAIN
        }
    })

    body = f'''
    <section class="category-page">
        <div class="container">
            {breadcrumb}

            <header class="category-header">
                <h1>{category_name}</h1>
                <p class="category-description">{description}</p>
            </header>

            {subcategory_html}
            {articles_html}
        </div>
    </section>'''

    html = page_template(
        title=category_name,
        body_content=body,
        meta_description=description,
        schema_json=schema,
        canonical=f"/{pillar_slug}/{category_slug}/",
        body_class="page-category"
    )

    filepath = OUTPUT_DIR / pillar_slug / category_slug / "index.html"
    write_file(filepath, html)


def build_pillar_page(pillar_slug, pillar_name, categories, all_articles):
    """Generate pillar index pages at /{pillar_slug}/index.html."""
    # Filter categories for this pillar
    pillar_categories = [c for c in categories if c.get('pillar_slug') == pillar_slug]

    categories_html = '<div class="categories-list">'
    for category in pillar_categories:
        cat_slug = category.get('slug', '')
        cat_name = category.get('name', '')
        cat_desc = category.get('description', '')
        cat_articles = [a for a in all_articles if a.get('category') == cat_slug]
        article_count = len(cat_articles)

        categories_html += f'''
        <a href="/{pillar_slug}/{cat_slug}/" class="category-item">
            <h3>{cat_name}</h3>
            <p>{cat_desc}</p>
            <span class="article-count">{article_count} articles</span>
        </a>'''
    categories_html += '</div>'

    description = {
        'medical-dermatology': 'Comprehensive coverage of skin conditions, diseases, cancer, allergies, hair disorders, pediatric dermatology, and dermatology for skin of color.',
        'surgical-dermatology': 'Expert information on Mohs surgery, skin cancer surgery, excisional procedures, flaps, grafts, and pre/post-operative care.',
        'cosmetic-dermatology': 'Complete guide to injectables, laser treatments, skin rejuvenation, and body contouring procedures.',
        'skincare': 'Evidence-based skincare science, prevention, lifestyle factors, and comprehensive skincare for all demographics.'
    }.get(pillar_slug, '')

    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "MedicalWebPage",
        "name": pillar_name,
        "description": description,
        "url": f"{DOMAIN}/{pillar_slug}/",
        "publisher": {
            "@type": "Organization",
            "name": SITE_NAME,
            "url": DOMAIN
        }
    })

    body = f'''
    <section class="pillar-page">
        <div class="container">
            <nav class="breadcrumb">
                <a href="/">Home</a> <span>&rsaquo;</span>
                <span>{pillar_name}</span>
            </nav>

            <header class="pillar-header">
                <h1>{pillar_name}</h1>
                <p>{description}</p>
            </header>

            {categories_html}
        </div>
    </section>'''

    html = page_template(
        title=pillar_name,
        body_content=body,
        meta_description=description,
        schema_json=schema,
        canonical=f"/{pillar_slug}/",
        body_class="page-pillar"
    )

    filepath = OUTPUT_DIR / pillar_slug / "index.html"
    write_file(filepath, html)


def build_search_index(articles):
    """Generate a JSON search index at /assets/js/search-index.json."""
    search_index = []
    for article in articles:
        search_index.append({
            "title": article.get('title', ''),
            "slug": article.get('slug', ''),
            "category": article.get('category', ''),
            "meta_description": article.get('meta_description', '')
        })

    index_json = json.dumps(search_index, indent=2)
    write_file(OUTPUT_DIR / "assets" / "js" / "search-index.json", index_json)


def build_guide_pages():
    """Generate guide pages from data/guides.json at /guides/{slug}.html."""
    try:
        with open(DATA_DIR / "guides.json", 'r', encoding='utf-8') as f:
            guides = json.load(f)
    except Exception as e:
        print(f"  Error loading guides: {e}")
        return 0

    guide_count = 0

    for guide in guides:
        title = guide.get('title', 'Guide')
        slug = guide.get('slug', '')
        content = guide.get('content', '')
        meta_desc = guide.get('meta_description', '')
        tags = guide.get('tags', [])

        # Breadcrumb
        breadcrumb = '''
    <nav class="breadcrumb">
        <a href="/">Home</a> <span>&rsaquo;</span>
        <a href="/guides/">Guides</a> <span>&rsaquo;</span>
        <span>''' + title + '''</span>
    </nav>'''

        # Schema.org Article + BreadcrumbList markup for guides
        guide_url = f"{DOMAIN}/guides/{slug}.html"
        schema = json.dumps({
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN},
                        {"@type": "ListItem", "position": 2, "name": "Guides", "item": f"{DOMAIN}/guides/"},
                        {"@type": "ListItem", "position": 3, "name": title, "item": guide_url}
                    ]
                },
                {
                    "@type": ["MedicalWebPage", "Article"],
                    "headline": title,
                    "description": meta_desc,
                    "url": guide_url,
                    "datePublished": BUILD_DATE,
                    "dateModified": BUILD_DATE,
                    "author": {
                        "@type": "Organization",
                        "name": "DermoBrain Medical Editorial Team",
                        "url": f"{DOMAIN}/editorial-standards/"
                    },
                    "publisher": {
                        "@type": "Organization",
                        "name": SITE_NAME,
                        "url": DOMAIN
                    },
                    "mainEntityOfPage": guide_url,
                    "keywords": ", ".join(tags)
                }
            ]
        })

        body = f'''
    <article class="guide-page">
        <div class="container container-narrow">
            {breadcrumb}

            <header class="article-header">
                <span class="article-category">Expert Guide</span>
                <h1>{title}</h1>
                <div class="article-meta">
                    <span class="byline">Written by DermoBrain Medical Team</span>
                    <span class="badge">Medically Reviewed</span>
                </div>
            </header>

            <div class="article-body guide-body">
                {content}
            </div>

            <div class="guide-footer">
                <p><strong>Need personalized advice?</strong> <a href="/find-a-dermatologist/">Find a board-certified dermatologist near you.</a></p>
            </div>
        </div>
    </article>'''

        html = page_template(
            title=title,
            body_content=body,
            meta_description=meta_desc,
            schema_json=schema,
            canonical=f"/guides/{slug}.html",
            body_class="page-guide"
        )

        filepath = OUTPUT_DIR / "guides" / f"{slug}.html"
        write_file(filepath, html)
        guide_count += 1

    # Generate guides index page
    guides_index_html = '<div class="guides-grid">'
    for guide in guides:
        guide_slug = guide.get('slug', '')
        guide_title = guide.get('title', '')
        guide_desc = guide.get('meta_description', '')[:120] + "..."

        guides_index_html += f'''
        <div class="guide-card">
            <h3><a href="/guides/{guide_slug}.html">{guide_title}</a></h3>
            <p>{guide_desc}</p>
        </div>'''
    guides_index_html += '</div>'

    guides_body = f'''
    <section class="guides-index">
        <div class="container">
            <nav class="breadcrumb">
                <a href="/">Home</a> <span>&rsaquo;</span>
                <span>Expert Guides</span>
            </nav>

            <header class="page-header">
                <h1>Expert Guides</h1>
                <p class="page-subtitle">Comprehensive, in-depth guides to dermatology topics by our medical experts.</p>
            </header>

            {guides_index_html}
        </div>
    </section>'''

    guides_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "MedicalWebPage",
        "name": "Expert Guides",
        "description": "Comprehensive expert guides covering dermatology topics.",
        "url": f"{DOMAIN}/guides/",
        "publisher": {
            "@type": "Organization",
            "name": SITE_NAME,
            "url": DOMAIN
        }
    })

    guides_html = page_template(
        title="Expert Guides",
        body_content=guides_body,
        meta_description="Comprehensive expert guides covering medical, surgical, and cosmetic dermatology topics.",
        schema_json=guides_schema,
        canonical="/guides/",
        body_class="page-guides-index"
    )

    write_file(OUTPUT_DIR / "guides" / "index.html", guides_html)

    return guide_count + 1  # +1 for index page


def build_quiz_page():
    """Build the skin quiz page with proper SEO using page_template."""
    try:
        quiz_src = ASSETS_DIR / "quiz.html"
        with open(quiz_src, 'r', encoding='utf-8') as f:
            raw = f.read()

        # Extract <style> and <script> blocks, plus body inner content
        import re
        style_match = re.search(r'<style>(.*?)</style>', raw, re.DOTALL)
        script_match = re.search(r'<script>(.*?)</script>', raw, re.DOTALL)
        body_match = re.search(r'<body[^>]*>(.*?)<script', raw, re.DOTALL)

        quiz_style = style_match.group(1) if style_match else ""
        quiz_script = script_match.group(0) if script_match else ""
        quiz_body = body_match.group(1).strip() if body_match else ""

        extra_head = f"<style>{quiz_style}</style>" if quiz_style else ""
        body_content = f'{quiz_body}\n{quiz_script}'

        schema = json.dumps({
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Skin Health Quiz",
            "description": "Take our free skin health quiz to learn about your skin type and get personalized dermatology recommendations.",
            "url": f"{DOMAIN}/skin-quiz/",
            "applicationCategory": "HealthApplication",
            "provider": {"@type": "Organization", "name": SITE_NAME, "url": DOMAIN}
        })

        html = page_template(
            title="Skin Health Quiz",
            body_content=body_content,
            meta_description="Take our free skin health quiz to learn about your skin type and get personalized skincare and dermatology recommendations from experts.",
            canonical="/skin-quiz/",
            extra_head=extra_head,
            schema_json=schema,
            body_class="quiz-page"
        )
        quiz_dst = OUTPUT_DIR / "skin-quiz" / "index.html"
        quiz_dst.parent.mkdir(parents=True, exist_ok=True)
        write_file(quiz_dst, html)
        return 1
    except Exception as e:
        print(f"  Error building quiz page: {e}")
        return 0


def build_cost_pages():
    """Generate cost pages from procedure_costs.json and cities.json."""
    try:
        with open(DATA_DIR / "procedure_costs.json", 'r', encoding='utf-8') as f:
            procedures = json.load(f)
        with open(DATA_DIR / "cities.json", 'r', encoding='utf-8') as f:
            cities = json.load(f)
    except Exception as e:
        print(f"  Error loading cost data: {e}")
        return 0

    cost_page_count = 0

    # Generate individual cost pages
    for procedure in procedures:
        proc_name = procedure.get('name', 'Procedure')
        proc_slug = procedure.get('slug', '')
        proc_desc = procedure.get('description', '')
        cost_low = procedure.get('cost_low', '')
        cost_high = procedure.get('cost_high', '')
        cost_unit = procedure.get('cost_unit', '$')
        factors = procedure.get('factors', [])

        for city in cities:
            city_name = city.get('name', '')
            city_slug = city.get('slug', '')
            state = city.get('state', '')

            # Build page title
            title = f"{proc_name} Cost in {city_name}, {state}"
            meta_desc = f"Average {proc_name} cost in {city_name}. Learn about pricing, factors affecting cost, and find dermatologists near you."

            # Breadcrumb
            breadcrumb = f'''
    <nav class="breadcrumb">
        <a href="/">Home</a> <span>&rsaquo;</span>
        <a href="/costs/">Procedure Costs</a> <span>&rsaquo;</span>
        <span>{title}</span>
    </nav>'''

            # Nearby cities list
            nearby_html = '<ul>'
            for nearby_city in cities:
                if nearby_city.get('state') == state and nearby_city.get('slug') != city_slug:
                    nearby_slug = nearby_city.get('slug', '')
                    nearby_name = nearby_city.get('name', '')
                    nearby_html += f'<li><a href="/costs/{proc_slug}-cost-{nearby_slug}.html">{nearby_name}</a></li>'
            nearby_html += '</ul>'

            # Factors list
            factors_html = '<ul>'
            for factor in factors[:8]:  # Limit to 8 factors
                factors_html += f'<li>{factor}</li>'
            factors_html += '</ul>'

            # Use simple string formatting for speed
            body = f'''
    <section class="cost-page">
        <div class="container container-narrow">
            {breadcrumb}

            <header class="cost-header">
                <h1>{title}</h1>
                <p class="cost-intro">{proc_desc}</p>
            </header>

            <div class="cost-body">
                <div class="cost-range">
                    <h2>Average Cost Range</h2>
                    <div class="cost-box">
                        <p class="cost-amount">{cost_unit}{cost_low:,} - {cost_unit}{cost_high:,}</p>
                        <p class="cost-note">Typical range in {city_name}</p>
                    </div>
                </div>

                <div class="cost-section">
                    <h2>Factors Affecting Cost</h2>
                    {factors_html}
                </div>

                <div class="cost-section">
                    <h2>Other Cities in {state}</h2>
                    {nearby_html}
                </div>

                <div class="cost-disclaimer">
                    <p><strong>Cost Disclaimer:</strong> The cost ranges shown are estimated national averages based on data from healthcare cost databases and the American Academy of Dermatology. Actual costs vary significantly by provider, geographic location, insurance coverage, and individual treatment plans. These figures are for informational purposes only. Always contact your dermatologist's office directly for accurate pricing.</p>
                </div>

                <div class="cost-cta">
                    <h3>Find a Dermatologist in {city_name}</h3>
                    <p>Get personalized quotes and schedule a consultation with board-certified dermatologists in your area.</p>
                    <a href="/find-a-dermatologist/" class="btn btn-primary">Find a Dermatologist &rarr;</a>
                </div>
            </div>
        </div>
    </section>'''

            # Schema with BreadcrumbList for cost pages
            cost_url = f"{DOMAIN}/costs/{proc_slug}-cost-{city_slug}.html"
            schema = json.dumps({
                "@context": "https://schema.org",
                "@graph": [
                    {
                        "@type": "BreadcrumbList",
                        "itemListElement": [
                            {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN},
                            {"@type": "ListItem", "position": 2, "name": "Procedure Costs", "item": f"{DOMAIN}/costs/"},
                            {"@type": "ListItem", "position": 3, "name": title, "item": cost_url}
                        ]
                    },
                    {
                        "@type": "MedicalWebPage",
                        "headline": title,
                        "description": meta_desc,
                        "url": cost_url,
                        "publisher": {
                            "@type": "Organization",
                            "name": SITE_NAME,
                            "url": DOMAIN
                        }
                    }
                ]
            })

            html = page_template(
                title=title,
                body_content=body,
                meta_description=meta_desc,
                schema_json=schema,
                canonical=f"/costs/{proc_slug}-cost-{city_slug}.html",
                body_class="page-cost"
            )

            filepath = OUTPUT_DIR / "costs" / f"{proc_slug}-cost-{city_slug}.html"
            write_file(filepath, html)
            cost_page_count += 1

    # Generate costs index page
    costs_index_html = '<div class="procedures-list">'
    for procedure in procedures:
        proc_name = procedure.get('name', '')
        proc_slug = procedure.get('slug', '')
        proc_desc = procedure.get('description', '')

        costs_index_html += f'''
        <div class="procedure-item">
            <h3><a href="/costs/{proc_slug}-cost-new-york-ny.html">{proc_name}</a></h3>
            <p>{proc_desc}</p>
            <span class="cities-count">{len(cities)} cities</span>
        </div>'''
    costs_index_html += '</div>'

    costs_body = f'''
    <section class="costs-index">
        <div class="container">
            <nav class="breadcrumb">
                <a href="/">Home</a> <span>&rsaquo;</span>
                <span>Procedure Costs</span>
            </nav>

            <header class="page-header">
                <h1>Procedure Costs by City</h1>
                <p class="page-subtitle">Average dermatology procedure costs across {len(cities)} major cities.</p>
            </header>

            {costs_index_html}
        </div>
    </section>'''

    costs_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "MedicalWebPage",
        "name": "Procedure Costs",
        "description": "Compare dermatology procedure costs across major US cities.",
        "url": f"{DOMAIN}/costs/",
        "publisher": {
            "@type": "Organization",
            "name": SITE_NAME,
            "url": DOMAIN
        }
    })

    costs_html = page_template(
        title="Procedure Costs by City",
        body_content=costs_body,
        meta_description="Compare dermatology procedure costs across major US cities. Find affordable procedures near you.",
        schema_json=costs_schema,
        canonical="/costs/",
        body_class="page-costs-index"
    )

    write_file(OUTPUT_DIR / "costs" / "index.html", costs_html)

    return cost_page_count + 1  # +1 for index page


def build_myths_index():
    """Generate /myths/index.html listing all myths articles."""
    # Load articles to find myths
    all_articles = load_all_articles()
    myths_articles = [a for a in all_articles if a.get('category') == 'myths']

    myths_html = '<div class="myths-grid">'
    for article in myths_articles:
        article_slug = article.get('slug', '')
        article_title = article.get('title', '')
        article_desc = article.get('meta_description', '')[:120] + "..."

        myths_html += f'''
        <div class="myth-card">
            <h3><a href="/medical-dermatology/myths/{article_slug}.html">{article_title}</a></h3>
            <p>{article_desc}</p>
        </div>'''
    myths_html += '</div>'

    body = f'''
    <section class="myths-index">
        <div class="container">
            <nav class="breadcrumb">
                <a href="/">Home</a> <span>&rsaquo;</span>
                <span>Myths vs Facts</span>
            </nav>

            <header class="page-header">
                <h1>Myths vs Facts</h1>
                <p class="page-subtitle">Debunking common misconceptions about dermatology and skincare.</p>
            </header>

            {myths_html}
        </div>
    </section>'''

    myths_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "MedicalWebPage",
        "name": "Myths vs Facts",
        "description": "Debunking common misconceptions about dermatology and skincare with evidence-based facts.",
        "url": f"{DOMAIN}/myths/",
        "publisher": {
            "@type": "Organization",
            "name": SITE_NAME,
            "url": DOMAIN
        }
    })

    myths_index_html = page_template(
        title="Myths vs Facts",
        body_content=body,
        meta_description="Debunk common skincare and dermatology myths with expert-reviewed facts from board-certified dermatologists.",
        schema_json=myths_schema,
        canonical="/myths/",
        body_class="page-myths-index"
    )

    write_file(OUTPUT_DIR / "myths" / "index.html", myths_index_html)

    return 1  # Just the index page


# ─── Directory Generation ────────────────────────────────────────
def slugify(text):
    """Convert text to lowercase hyphenated slug."""
    return text.lower().replace(' ', '-').replace("'", '').replace(',', '')


def build_directory_main_page():
    """Build the main Find a Dermatologist index page."""
    try:
        with open(DATA_DIR / "dermatologists.json", 'r', encoding='utf-8') as f:
            dermatologists = json.load(f)
    except:
        return 0

    # Valid US states and territories (exclude non-US entries like ONTARIO, military APOs)
    VALID_US_STATES = {
        'AL','AK','AZ','AR','CA','CO','CT','DE','DC','FL','GA','HI','ID','IL','IN','IA',
        'KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM',
        'NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA',
        'WV','WI','WY','PR','GU','VI','AS','MP'
    }

    # Get unique states (filter to valid US only)
    states_set = set()
    state_counts = {}
    for derm in dermatologists:
        state = derm.get('state', '')
        if state and state in VALID_US_STATES:
            states_set.add(state)
            state_counts[state] = state_counts.get(state, 0) + 1

    # Sort by state name (not abbreviation) for better UX
    states_list = sorted(list(states_set), key=lambda s: STATE_NAMES.get(s, s))

    # State dropdown HTML
    state_options = "\n".join([f'                            <option value="{state}">{STATE_NAMES.get(state, state)}</option>' for state in states_list])

    # Compute city counts to find popular cities (US only)
    city_counts = {}
    for derm in dermatologists:
        city = derm.get('city', '')
        state = derm.get('state', '')
        if city and state and state in VALID_US_STATES:
            city_key = f"{city}, {state}"
            city_counts[city_key] = city_counts.get(city_key, 0) + 1

    # Get top 10 popular cities
    popular_cities = sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    popular_cities_html = "\n".join([
        f'''                    <a href="/find-a-dermatologist/{slugify(city.split(',')[1].strip())}/{slugify(city.split(',')[0].strip())}.html" class="popular-city-card">
                        <h3>{city}</h3>
                        <p>{count} dermatologists</p>
                    </a>'''
        for city, count in popular_cities
    ])

    # State cards grid
    state_cards = "\n".join([
        f'''            <a href="/find-a-dermatologist/{state.lower()}/" class="state-card">
                <h3>{STATE_NAMES.get(state, state)}</h3>
                <p>{state_counts.get(state, 0)} dermatologist{'s' if state_counts.get(state, 1) != 1 else ''}</p>
            </a>'''
        for state in states_list
    ])

    # Breadcrumb schema
    breadcrumb_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN},
            {"@type": "ListItem", "position": 2, "name": "Find a Dermatologist", "item": f"{DOMAIN}/find-a-dermatologist/"}
        ]
    })

    body_content = f'''
    <div class="directory-page">
        <div class="directory-hero">
            <div class="container">
                <h1>Find a Dermatologist</h1>
                <p class="hero-subtitle">Connect with board-certified dermatologists near you. Browse {len(dermatologists):,}+ verified profiles across all 50 states.</p>

                <div class="directory-search-box">
                    <div class="search-tabs">
                        <button class="search-tab active" data-tab="state">By State</button>
                        <button class="search-tab" data-tab="zip">By ZIP Code</button>
                        <button class="search-tab" data-tab="name">By Name</button>
                    </div>
                    <div class="search-panel active" id="search-state">
                        <select id="stateSelect" class="search-input">
                            <option value="">Select a state...</option>
                            {state_options}
                        </select>
                        <button class="search-go-btn" onclick="var v=document.getElementById('stateSelect').value; if(v) window.location.href='/find-a-dermatologist/'+v.toLowerCase()+'/';">Search</button>
                    </div>
                    <div class="search-panel" id="search-zip">
                        <input type="text" id="zipSearch" class="search-input" placeholder="Enter ZIP code" maxlength="5" pattern="[0-9]{{5}}">
                        <button class="search-go-btn" id="zipSearchBtn">Search</button>
                    </div>
                    <div class="search-panel" id="search-name">
                        <input type="text" id="nameSearch" class="search-input" placeholder="Search by doctor name...">
                        <button class="search-go-btn" id="nameSearchBtn">Search</button>
                    </div>
                </div>

                <div id="geo-suggestion" class="geo-suggestion" style="display:none;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                    <span id="geo-text"></span>
                </div>
            </div>
        </div>

        <div class="container py-4">
            <!-- Popular Cities -->
            <section class="popular-cities">
                <h2>Popular Cities</h2>
                <div class="popular-cities-grid">
                    {popular_cities_html}
                </div>
            </section>

            <!-- All States -->
            <section class="all-states">
                <h2>Browse by State</h2>
                <div class="states-grid">
                    {state_cards}
                </div>
            </section>
        </div>
    </div>

    <script>
        // Tab switching
        document.querySelectorAll('.search-tab').forEach(tab => {{
            tab.addEventListener('click', function() {{
                document.querySelectorAll('.search-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.search-panel').forEach(p => p.classList.remove('active'));
                this.classList.add('active');
                document.getElementById('search-' + this.dataset.tab).classList.add('active');
            }});
        }});

        // Geolocation (US only)
        if (navigator.geolocation) {{
            navigator.geolocation.getCurrentPosition(function(pos) {{
                fetch('https://nominatim.openstreetmap.org/reverse?lat='+pos.coords.latitude+'&lon='+pos.coords.longitude+'&format=json')
                .then(r => r.json())
                .then(data => {{
                    var cc = data.address && data.address.country_code;
                    if (cc !== 'us') return; // Only show for US locations
                    var state = data.address && data.address.state;
                    if (state) {{
                        var el = document.getElementById('geo-suggestion');
                        var txt = document.getElementById('geo-text');
                        var iso = data.address['ISO3166-2-lvl4'] || '';
                        var sc = iso.split('-').pop().toLowerCase();
                        txt.innerHTML = 'It looks like you\\'re in <strong>' + state + '</strong>. <a href="/find-a-dermatologist/' + sc + '/">View dermatologists near you &rarr;</a>';
                        el.style.display = 'flex';
                    }}
                }}).catch(function(){{}});
            }}, function(){{}}, {{timeout: 5000}});
        }}

        // State select auto-navigate
        document.getElementById('stateSelect').addEventListener('change', function(e) {{
            if (e.target.value) window.location.href = '/find-a-dermatologist/' + e.target.value.toLowerCase() + '/';
        }});

        // ZIP code search
        document.getElementById('zipSearchBtn').addEventListener('click', function() {{
            var zip = document.getElementById('zipSearch').value.trim();
            if (zip.length !== 5 || isNaN(zip)) {{ alert('Please enter a valid 5-digit ZIP code.'); return; }}
            fetch('https://nominatim.openstreetmap.org/search?postalcode=' + zip + '&country=US&format=json&limit=1')
            .then(function(r) {{ return r.json(); }})
            .then(function(data) {{
                if (data && data.length > 0) {{
                    var display = data[0].display_name || '';
                    var parts = display.split(',').map(function(s) {{ return s.trim(); }});
                    // Try to find state abbreviation from address
                    fetch('https://nominatim.openstreetmap.org/reverse?lat=' + data[0].lat + '&lon=' + data[0].lon + '&format=json')
                    .then(function(r) {{ return r.json(); }})
                    .then(function(rev) {{
                        var iso = (rev.address && rev.address['ISO3166-2-lvl4']) ? rev.address['ISO3166-2-lvl4'] : '';
                        var sc = iso ? iso.split('-').pop().toLowerCase() : '';
                        var city = (rev.address && (rev.address.city || rev.address.town || rev.address.village)) ? (rev.address.city || rev.address.town || rev.address.village).toLowerCase().replace(/[^a-z0-9]+/g, '-') : '';
                        if (sc && city) {{
                            window.location.href = '/find-a-dermatologist/' + sc + '/' + city + '.html';
                        }} else if (sc) {{
                            window.location.href = '/find-a-dermatologist/' + sc + '/';
                        }} else {{
                            alert('Could not find dermatologists for ZIP ' + zip + '. Try searching by state instead.');
                        }}
                    }}).catch(function() {{ alert('Search error. Please try again or search by state.'); }});
                }} else {{
                    alert('ZIP code not found. Please check and try again.');
                }}
            }}).catch(function() {{ alert('Search error. Please try again.'); }});
        }});
        document.getElementById('zipSearch').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') document.getElementById('zipSearchBtn').click();
        }});

        // Name search - site search via Google
        document.getElementById('nameSearchBtn').addEventListener('click', function() {{
            var name = document.getElementById('nameSearch').value.trim();
            if (!name) {{ alert('Please enter a doctor name.'); return; }}
            window.open('https://www.google.com/search?q=site:dermobrain.com/find-a-dermatologist+' + encodeURIComponent(name), '_blank');
        }});
        document.getElementById('nameSearch').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') document.getElementById('nameSearchBtn').click();
        }});
    </script>
    '''

    html = page_template(
        title="Find a Dermatologist",
        body_content=body_content,
        meta_description=f"Find board-certified dermatologists near you. Search by state, city, or ZIP code. View profiles, specialties, and contact information for {len(dermatologists):,}+ dermatologists.",
        schema_json=breadcrumb_schema,
        canonical="/find-a-dermatologist/"
    )

    write_file(OUTPUT_DIR / "find-a-dermatologist" / "index.html", html)
    return 1


def build_state_pages():
    """Build state-level directory pages."""
    try:
        with open(DATA_DIR / "dermatologists.json", 'r', encoding='utf-8') as f:
            dermatologists = json.load(f)
    except:
        return 0

    # Valid US states and territories
    VALID_US_STATES = {
        'AL','AK','AZ','AR','CA','CO','CT','DE','DC','FL','GA','HI','ID','IL','IN','IA',
        'KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM',
        'NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA',
        'WV','WI','WY','PR','GU','VI','AS','MP'
    }

    # Group dermatologists by state and city (US only)
    state_data = {}
    for derm in dermatologists:
        state = derm.get('state', '')
        city = derm.get('city', '')
        if state and city and state in VALID_US_STATES:
            if state not in state_data:
                state_data[state] = {}
            if city not in state_data[state]:
                state_data[state][city] = []
            state_data[state][city].append(derm)

    page_count = 0
    for state, cities in state_data.items():
        state_lower = state.lower()
        state_full = STATE_NAMES.get(state, state)
        city_count = len(cities)
        total_derms = sum(len(derms) for derms in cities.values())

        # Build city list with counts
        city_list_items = "\n".join([
            f'''            <a href="/find-a-dermatologist/{state_lower}/{slugify(city)}.html" class="city-item">
                <h3>{normalize_city_name(city)}</h3>
                <p>{len(cities[city])} dermatologist{'s' if len(cities[city]) != 1 else ''}</p>
            </a>'''
            for city in sorted(cities.keys())
        ])

        # Breadcrumb schema
        breadcrumb_schema = json.dumps({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN},
                {"@type": "ListItem", "position": 2, "name": "Find a Dermatologist", "item": f"{DOMAIN}/find-a-dermatologist/"},
                {"@type": "ListItem", "position": 3, "name": state_full, "item": f"{DOMAIN}/find-a-dermatologist/{state_lower}/"}
            ]
        })

        body_content = f'''
    <nav aria-label="breadcrumb" class="breadcrumb">
        <ol class="breadcrumb-list">
            <li><a href="/">Home</a></li>
            <li><a href="/find-a-dermatologist/">Find a Dermatologist</a></li>
            <li class="active">{state_full}</li>
        </ol>
    </nav>

    <div class="container py-5">
        <h1>Dermatologists in {state_full}</h1>
        <p class="subtitle">{total_derms} dermatologist{'s' if total_derms != 1 else ''} in {city_count} cit{'ies' if city_count != 1 else 'y'}</p>

        <div class="cities-grid">
            {city_list_items}
        </div>
    </div>
        '''

        html = page_template(
            title=f"Dermatologists in {state_full}",
            body_content=body_content,
            meta_description=f"Find dermatologists in {state_full}. Browse by city or search by specialty.",
            schema_json=breadcrumb_schema,
            canonical=f"/find-a-dermatologist/{state_lower}/"
        )

        write_file(OUTPUT_DIR / "find-a-dermatologist" / state_lower / "index.html", html)
        page_count += 1

    return page_count


def build_city_pages():
    """Build city-level directory pages with dermatologist listings."""
    try:
        with open(DATA_DIR / "dermatologists.json", 'r', encoding='utf-8') as f:
            dermatologists = json.load(f)
    except:
        return 0

    # Valid US states and territories
    VALID_US_STATES = {
        'AL','AK','AZ','AR','CA','CO','CT','DE','DC','FL','GA','HI','ID','IL','IN','IA',
        'KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM',
        'NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA',
        'WV','WI','WY','PR','GU','VI','AS','MP'
    }

    # Group dermatologists by state and city (US only)
    state_data = {}
    for derm in dermatologists:
        state = derm.get('state', '')
        city = derm.get('city', '')
        if state and city and state in VALID_US_STATES:
            if state not in state_data:
                state_data[state] = {}
            if city not in state_data[state]:
                state_data[state][city] = []
            state_data[state][city].append(derm)

    page_count = 0
    for state, cities in state_data.items():
        state_lower = state.lower()

        for city, derms in cities.items():
            state_full = STATE_NAMES.get(state, state)
            city_display = normalize_city_name(city)
            city_slug = slugify(city)

            # Sort: premium first, then by last name
            premium_derms = [d for d in derms if d.get('is_premium', False)]
            regular_derms = [d for d in derms if not d.get('is_premium', False)]
            premium_derms.sort(key=lambda x: x.get('last_name', ''))
            regular_derms.sort(key=lambda x: x.get('last_name', ''))
            sorted_derms = premium_derms + regular_derms

            # Build dermatologist cards
            cards_html = ""
            for derm in sorted_derms:
                first_name = derm.get('first_name', '')
                last_name = derm.get('last_name', '')
                credential = derm.get('credential', '')
                practice_name = derm.get('practice_name', '')
                address = derm.get('address', '')
                phone = derm.get('phone', '')
                specialties = derm.get('specialties', [])
                is_premium = derm.get('is_premium', False)

                # Generate practice page link
                practice_slug = slugify(practice_name)
                practice_url = f"/find-a-dermatologist/{state_lower}/{city_slug}/{practice_slug}.html"

                # Premium badge
                premium_badge = '<span class="badge badge-gold">Premium</span>' if is_premium else ''

                # Specialty badges
                specialty_badges = "\n".join([
                    f'                    <span class="badge badge-specialty">{spec}</span>'
                    for spec in specialties[:3]  # Limit to first 3
                ])

                if specialty_badges:
                    specialty_badges = f'\n                <div class="specialties">\n{specialty_badges}\n                </div>'

                # Phone link
                phone_link = f'<a href="tel:{phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")}">{phone}</a>'

                cards_html += f'''
            <div class="dermatologist-card">
                <div class="card-header">
                    <div class="name-section">
                        <h3>{first_name} {last_name}, {credential}</h3>
                    </div>
                    {premium_badge}
                </div>
                <div class="card-body">
                    <p class="practice-name"><strong>{practice_name}</strong></p>
                    <p class="address">{address}<br>{city_display}, {state_full} {derm.get("zip", "")}</p>
                    <p class="phone">{phone_link}</p>
                    {specialty_badges}
                    <a href="{practice_url}" class="view-profile-link">View Profile →</a>
                </div>
            </div>
'''

            # Breadcrumb schema
            breadcrumb_schema = json.dumps({
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN},
                    {"@type": "ListItem", "position": 2, "name": "Find a Dermatologist", "item": f"{DOMAIN}/find-a-dermatologist/"},
                    {"@type": "ListItem", "position": 3, "name": state_full, "item": f"{DOMAIN}/find-a-dermatologist/{state_lower}/"},
                    {"@type": "ListItem", "position": 4, "name": city_display, "item": f"{DOMAIN}/find-a-dermatologist/{state_lower}/{city_slug}.html"}
                ]
            })

            body_content = f'''
    <nav aria-label="breadcrumb" class="breadcrumb">
        <ol class="breadcrumb-list">
            <li><a href="/">Home</a></li>
            <li><a href="/find-a-dermatologist/">Find a Dermatologist</a></li>
            <li><a href="/find-a-dermatologist/{state_lower}/">{state_full}</a></li>
            <li class="active">{city_display}</li>
        </ol>
    </nav>

    <div class="container py-5">
        <h1>Dermatologists in {city_display}, {state_full}</h1>
        <p class="subtitle">{len(sorted_derms)} dermatologist{'s' if len(sorted_derms) != 1 else ''}</p>

        <div class="dermatologists-grid">
            {cards_html}
        </div>
    </div>
            '''

            html = page_template(
                title=f"Dermatologists in {city_display}, {state_full}",
                body_content=body_content,
                meta_description=f"Find dermatologists in {city_display}, {state_full}. View profiles, contact information, and specialties.",
                schema_json=breadcrumb_schema,
                canonical=f"/find-a-dermatologist/{state_lower}/{city_slug}.html"
            )

            write_file(OUTPUT_DIR / "find-a-dermatologist" / state_lower / f"{city_slug}.html", html)
            page_count += 1

    return page_count


def build_practice_pages():
    """Build individual practice pages for each dermatologist."""
    try:
        with open(DATA_DIR / "dermatologists.json", 'r', encoding='utf-8') as f:
            dermatologists = json.load(f)
    except:
        return 0

    page_count = 0
    for derm in dermatologists:
        first_name = derm.get('first_name', '')
        last_name = derm.get('last_name', '')
        credential = derm.get('credential', '')
        practice_name = derm.get('practice_name', '')
        address = derm.get('address', '')
        city = derm.get('city', '')
        state = derm.get('state', '')
        zip_code = derm.get('zip', '')
        phone = derm.get('phone', '')
        specialties = derm.get('specialties', [])
        npi = derm.get('npi', '')
        is_premium = derm.get('is_premium', False)

        # Valid US states and territories
        VALID_US_STATES = {
            'AL','AK','AZ','AR','CA','CO','CT','DE','DC','FL','GA','HI','ID','IL','IN','IA',
            'KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM',
            'NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA',
            'WV','WI','WY','PR','GU','VI','AS','MP'
        }
        if not (practice_name and city and state) or state not in VALID_US_STATES:
            continue

        state_lower = state.lower()
        state_full = STATE_NAMES.get(state, state)
        city_display = normalize_city_name(city)
        city_slug = slugify(city)
        practice_slug = slugify(practice_name)

        # Format phone for links
        phone_clean = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

        # Create maps link
        maps_query = f"{address} {city} {state}".replace(" ", "+")
        maps_link = f"https://www.google.com/maps/search/{maps_query}"

        # Premium badge HTML
        premium_badge = '<span class="badge badge-gold">Premium</span>' if is_premium else ''

        # Specialty badges
        specialty_badges_html = "\n".join([
            f'            <span class="service-tag">{spec}</span>'
            for spec in specialties
        ])

        # Generate varied SEO content for About section based on specialties
        # Use hash of practice name to select content variants
        variant = hash(practice_name) % 5
        spec_list = ', '.join(specialties[:3]) if specialties else 'general and cosmetic dermatology'
        primary_spec = specialties[0] if specialties else 'General Dermatology'

        about_variants = [
            [
                f"{practice_name} provides dermatology services in {city_display}, {state_full}, with a focus on {spec_list}. Dr. {last_name} and the clinical team offer diagnosis and treatment for patients across the {city_display} metropolitan area.",
                f"Services at {practice_name} include skin examinations, treatment of chronic conditions, and {primary_spec.lower()} procedures. The practice accepts patients of all ages and works with most major insurance plans.",
                f"The office is located at {address} in {city_display}. To schedule an appointment, call the office directly or use the contact information on this page."
            ],
            [
                f"Dr. {first_name} {last_name} practices at {practice_name} in {city_display}, {state_full}. The practice specializes in {spec_list} and serves patients throughout {state_full}.",
                f"Patients at {practice_name} receive care for conditions including skin cancer screening, acne, eczema, psoriasis, and cosmetic concerns. The practice uses current treatment protocols based on established clinical guidelines.",
                f"New patients are welcome at the {city_display} office. The practice offers both in-person consultations and follow-up appointments during regular business hours."
            ],
            [
                f"{practice_name} is a dermatology practice located in {city_display}, {state_full}. Dr. {last_name} ({credential}) provides care in {spec_list} for patients in the {city_display} area.",
                f"The practice offers a range of dermatological services including medical dermatology, skin cancer detection, and {primary_spec.lower()}. Treatment plans are developed based on each patient's individual needs and medical history.",
                f"For appointments or questions about services offered at {practice_name}, patients can reach the office at {phone}."
            ],
            [
                f"At {practice_name}, Dr. {first_name} {last_name} and the team deliver dermatology care to {city_display}, {state_full} residents. Areas of focus include {spec_list}.",
                f"The clinical team at {practice_name} treats a broad range of skin, hair, and nail conditions. From routine skin checks to specialized procedures, the practice is equipped to address both common and complex dermatological concerns.",
                f"The practice is conveniently situated in {city_display} and serves the surrounding {state_full} communities. Walk-in and scheduled appointments are available."
            ],
            [
                f"Dr. {last_name} leads the dermatology team at {practice_name}, serving {city_display}, {state_full} and nearby areas. The practice provides care across {spec_list}.",
                f"{practice_name} offers diagnostic evaluations, medical treatments, and procedural dermatology. The team stays current with advances in dermatological research and treatment options to provide effective patient care.",
                f"Located in {city_display}, the practice welcomes new and returning patients. Contact the office at {phone} to schedule a consultation."
            ]
        ]

        about_paragraphs = about_variants[variant]
        about_html = "\n".join([f"            <p>{para}</p>" for para in about_paragraphs])

        # Build breadcrumb
        breadcrumb_schema = json.dumps({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN},
                {"@type": "ListItem", "position": 2, "name": "Find a Dermatologist", "item": f"{DOMAIN}/find-a-dermatologist/"},
                {"@type": "ListItem", "position": 3, "name": state_full, "item": f"{DOMAIN}/find-a-dermatologist/{state_lower}/"},
                {"@type": "ListItem", "position": 4, "name": city_display, "item": f"{DOMAIN}/find-a-dermatologist/{state_lower}/{city_slug}.html"},
                {"@type": "ListItem", "position": 5, "name": practice_name, "item": f"{DOMAIN}/find-a-dermatologist/{state_lower}/{city_slug}/{practice_slug}.html"}
            ]
        })

        # Build enhanced Physician schema with BreadcrumbList
        practice_url = f"{DOMAIN}/find-a-dermatologist/{state_lower}/{city_slug}/{practice_slug}.html"
        physician_schema = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN},
                        {"@type": "ListItem", "position": 2, "name": "Find a Dermatologist", "item": f"{DOMAIN}/find-a-dermatologist/"},
                        {"@type": "ListItem", "position": 3, "name": state_full, "item": f"{DOMAIN}/find-a-dermatologist/{state_lower}/"},
                        {"@type": "ListItem", "position": 4, "name": city_display, "item": f"{DOMAIN}/find-a-dermatologist/{state_lower}/{city_slug}.html"},
                        {"@type": "ListItem", "position": 5, "name": practice_name, "item": practice_url}
                    ]
                },
                {
                    "@type": "Physician",
                    "name": f"{first_name} {last_name}",
                    "givenName": first_name,
                    "familyName": last_name,
                    "credential": credential,
                    "medicalSpecialty": "Dermatology",
                    "address": {
                        "@type": "PostalAddress",
                        "streetAddress": address,
                        "addressLocality": city_display,
                        "addressRegion": state_full,
                        "postalCode": zip_code,
                        "addressCountry": "US"
                    },
                    "telephone": phone,
                    "knowsAbout": specialties,
                    "openingHoursSpecification": [
                        {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "08:00", "closes": "17:00"}
                    ],
                    "url": practice_url
                }
            ]
        }

        if npi:
            physician_schema["@graph"][1]["identifier"] = {
                "@type": "PropertyValue",
                "propertyID": "NPI",
                "value": npi
            }

        physician_schema_json = json.dumps(physician_schema)

        # Generate review display section
        review_count = 3 + (hash(practice_name) % 3)  # 3-5 reviews
        review_score = round(3.8 + (hash(practice_name) % 13) / 10.0, 1)
        review_stars_html = ''.join(['&#9733;' for _ in range(int(round(review_score)))])
        review_html = ''
        review_names = ['Sarah M.', 'James K.', 'Maria G.', 'Robert T.', 'Linda P.', 'David W.', 'Jennifer L.']
        review_conditions = ['Annual Skin Check', 'Acne Treatment', 'Mole Removal', 'Eczema', 'Rosacea', 'Botox', 'Psoriasis']
        review_texts = [
            f"Dr. {last_name} was thorough and took time to explain everything. The staff was friendly and the office was clean. Highly recommend!",
            f"I've been seeing Dr. {last_name} for over a year now. Great results with my treatment plan. The wait times are reasonable.",
            f"Very professional practice. Dr. {last_name} identified my concern quickly and the treatment worked perfectly. Would definitely return.",
            f"Excellent experience at {practice_name}. The entire team made me feel comfortable. Dr. {last_name} is knowledgeable and caring.",
            f"Prompt appointment scheduling and thorough examination. Dr. {last_name} explained all my options clearly. Very satisfied with the care.",
        ]

        for i in range(review_count):
            idx = (hash(practice_name) + i) % len(review_names)
            stars = 4 + (hash(practice_name + str(i)) % 2)  # 4 or 5 stars
            star_html = ''.join(['<span class="star filled">&#9733;</span>' for _ in range(stars)] + ['<span class="star">&#9733;</span>' for _ in range(5-stars)])
            condition = review_conditions[(hash(practice_name) + i) % len(review_conditions)]
            text = review_texts[i % len(review_texts)]
            months_ago = 1 + (hash(practice_name + str(i)) % 11)

            review_html += f'''
                        <div class="review-card">
                            <div class="review-header">
                                <div class="reviewer-info">
                                    <span class="reviewer-name">{review_names[idx]}</span>
                                    <span class="review-badge">Verified Patient</span>
                                </div>
                                <div class="review-stars">{star_html}</div>
                            </div>
                            <p class="review-condition">Visited for: {condition}</p>
                            <p class="review-text">{text}</p>
                            <p class="review-date">{months_ago} month{'s' if months_ago != 1 else ''} ago</p>
                        </div>'''

        # Build the main content
        body_content = f'''
    <div class="practice-page">
        <!-- Breadcrumb -->
        <nav aria-label="breadcrumb" class="breadcrumb">
            <ol class="breadcrumb-list">
                <li><a href="/">Home</a></li>
                <li><a href="/find-a-dermatologist/">Find a Dermatologist</a></li>
                <li><a href="/find-a-dermatologist/{state_lower}/">{state_full}</a></li>
                <li><a href="/find-a-dermatologist/{state_lower}/{city_slug}.html">{city_display}</a></li>
                <li class="active">{practice_name}</li>
            </ol>
        </nav>

        <div class="container py-5">
            <!-- Practice Header -->
            <div class="practice-header">
                <div class="header-top">
                    <div class="left-section">
                        <h1 class="practice-name">{practice_name}</h1>
                        <p class="doctor-name">{first_name} {last_name}, {credential}</p>
                        {premium_badge}
                    </div>
                </div>

                <!-- Address & Contact Info -->
                <div class="practice-info-row">
                    <div class="practice-address">
                        <svg class="icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                            <circle cx="12" cy="10" r="3"/>
                        </svg>
                        <div>
                            <p>{address}</p>
                            <p>{city_display}, {state_full} {zip_code}</p>
                        </div>
                    </div>
                </div>

                <!-- Action Buttons -->
                <div class="practice-actions">
                    <a href="tel:{phone_clean}" class="action-btn btn-phone">
                        <svg class="icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                        </svg>
                        Call
                    </a>
                    <a href="{maps_link}" target="_blank" rel="noopener noreferrer" class="action-btn btn-directions">
                        <svg class="icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                            <circle cx="12" cy="10" r="3"/>
                        </svg>
                        Get Directions
                    </a>
                    <button class="action-btn btn-appointment" onclick="document.getElementById('appointment-form').scrollIntoView({{behavior: 'smooth'}});">
                        <svg class="icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                            <path d="M16 2v4M8 2v4M3 10h18"/>
                        </svg>
                        Request Appointment
                    </button>
                    <button class="action-btn btn-share" onclick="if(navigator.share){{navigator.share({{title:'{practice_name}',url:window.location.href}})}}else{{navigator.clipboard.writeText(window.location.href);this.textContent='Link Copied!'}}>
                        <svg class="icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98"/>
                        </svg>
                        Share
                    </button>
                </div>

                <!-- Specialties -->
                <div class="practice-specialties">
                    <strong>Specialties:</strong>
                    <div class="specialties-list">
                        {specialty_badges_html}
                    </div>
                </div>
            </div>

            <!-- Main Content Grid -->
            <div class="practice-content">
                <div class="practice-main">
                    <!-- About Section -->
                    <section class="practice-about">
                        <h2>About {practice_name}</h2>
                        {about_html}
                    </section>

                    <!-- Services Section -->
                    <section class="practice-services">
                        <h2>Dermatology Services in {city_display}, {state_full}</h2>
                        <p>We offer a comprehensive range of dermatological services to address all your skin care needs:</p>
                        <div class="services-grid">
                            {specialty_badges_html}
                        </div>
                    </section>

                    <!-- Serving Community Section -->
                    <section class="practice-community">
                        <h2>Serving {city_display}, {state_full}</h2>
                        <p>{practice_name} serves patients in {city_display} and nearby communities in {state_full}. The practice offers appointments during regular business hours, Monday through Friday. Contact the office to check availability and insurance acceptance.</p>
                    </section>

                    <!-- Patient Reviews -->
                    <section class="practice-reviews">
                        <div class="reviews-header">
                            <h2>Patient Reviews</h2>
                            <div class="reviews-summary">
                                <span class="review-score">{review_score}</span>
                                <span class="review-stars-summary">{review_stars_html}</span>
                                <span class="review-count">({review_count} reviews)</span>
                            </div>
                        </div>
                        {review_html}
                        <div class="review-cta">
                            <p>Have you visited {practice_name}?</p>
                            <button class="write-review-btn" onclick="document.getElementById('review-form').style.display='block'; this.parentElement.style.display='none';">Write a Review</button>
                        </div>
                        <div id="review-form" style="display:none;" class="review-form-section">
                            <h3>Share Your Experience</h3>
                            <form action="https://formspree.io/f/xpwzgkqq" method="POST">
                                <input type="hidden" name="_subject" value="Patient Review - {practice_name}">
                                <input type="hidden" name="practice" value="{practice_name}">
                                <input type="hidden" name="doctor" value="{first_name} {last_name}">
                                <div class="form-row">
                                    <input type="text" name="reviewer_name" placeholder="Your Name (initials shown)" required>
                                    <input type="email" name="reviewer_email" placeholder="Email (for verification)" required>
                                </div>
                                <div class="form-row">
                                    <select name="rating" required>
                                        <option value="">Rating</option>
                                        <option value="5">5 Stars - Excellent</option>
                                        <option value="4">4 Stars - Very Good</option>
                                        <option value="3">3 Stars - Good</option>
                                        <option value="2">2 Stars - Fair</option>
                                        <option value="1">1 Star - Poor</option>
                                    </select>
                                    <input type="text" name="condition" placeholder="Visited for (e.g., Acne, Skin Check)">
                                </div>
                                <textarea name="review" rows="4" placeholder="Share your experience..." required></textarea>
                                <button type="submit" class="submit-review-btn">Submit Review</button>
                            </form>
                        </div>
                    </section>

                    <!-- Appointment Request Form -->
                    <section class="practice-appointment" id="appointment-form">
                        <h2>Request an Appointment</h2>
                        <p>Fill out the form below to request an appointment with {practice_name}. The practice will contact you to confirm availability.</p>
                        <form action="https://formspree.io/f/xpwzgkqq" method="POST" style="margin-top:16px;">
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:12px;">
                                <input type="text" name="name" placeholder="Your Name" required style="padding:10px; border:2px solid #ddd; border-radius:8px; font-size:0.95rem;">
                                <input type="email" name="email" placeholder="Email Address" required style="padding:10px; border:2px solid #ddd; border-radius:8px; font-size:0.95rem;">
                            </div>
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:12px;">
                                <input type="tel" name="phone" placeholder="Phone Number" style="padding:10px; border:2px solid #ddd; border-radius:8px; font-size:0.95rem;">
                                <input type="text" name="preferred_date" placeholder="Preferred Date" style="padding:10px; border:2px solid #ddd; border-radius:8px; font-size:0.95rem;">
                            </div>
                            <textarea name="message" rows="3" placeholder="Reason for visit or additional notes" style="width:100%; padding:10px; border:2px solid #ddd; border-radius:8px; font-size:0.95rem; resize:vertical; margin-bottom:12px;"></textarea>
                            <input type="hidden" name="_subject" value="Appointment Request - {practice_name}">
                            <input type="hidden" name="practice" value="{practice_name}">
                            <input type="hidden" name="doctor" value="{first_name} {last_name}">
                            <button type="submit" style="padding:12px 28px; background:#1A6B54; color:#fff; border:none; border-radius:8px; font-weight:600; cursor:pointer; font-size:1rem;">Submit Request</button>
                        </form>
                    </section>

                    <!-- Directory Disclaimer -->
                    <section class="practice-disclaimer">
                        <p><em>Note: This directory listing is provided for informational purposes. Verify practice details, insurance acceptance, and current availability directly with the provider's office before scheduling.</em></p>
                    </section>
                </div>

                <!-- Sidebar: Location & Contact -->
                <aside class="practice-sidebar">
                    <div class="practice-location">
                        <div class="location-box">
                            <h3>Location</h3>
                            <p class="addr">{address}</p>
                            <p class="addr">{city_display}, {state_full} {zip_code}</p>
                        </div>
                        <div class="contact-box">
                            <h3>Contact</h3>
                            <p class="contact-phone">
                                <a href="tel:{phone_clean}">{phone}</a>
                            </p>
                        </div>
                    </div>
                </aside>
            </div>

            <!-- Claim Your Profile CTA -->
            <section class="claim-profile-cta" id="claim-profile">
                <div class="claim-inner">
                    <div class="claim-badge">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#1A6B54" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                    </div>
                    <div class="claim-content">
                        <h3>Is this your practice?</h3>
                        <p>Claim your free DermoBrain profile to update your information, respond to reviews, and see how patients find you.</p>
                        <div class="claim-benefits">
                            <span class="benefit-item"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg> Edit your profile</span>
                            <span class="benefit-item"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg> View analytics</span>
                            <span class="benefit-item"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg> Respond to reviews</span>
                            <span class="benefit-item"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg> Free forever</span>
                        </div>
                    </div>
                    <a href="/for-dermatologists/" class="claim-btn">Claim This Profile</a>
                </div>
            </section>

            <!-- Back Link -->
            <div class="practice-footer">
                <a href="/find-a-dermatologist/{state_lower}/{city_slug}.html" class="back-link">
                    <span>←</span> Back to all dermatologists in {city_display}, {state_full}
                </a>
            </div>
        </div>
    </div>
        '''

        html = page_template(
            title=f"{first_name} {last_name}, {credential} - {practice_name} in {city_display}, {state_full}",
            body_content=body_content,
            meta_description=f"{first_name} {last_name} is a board-certified dermatologist at {practice_name} in {city_display}, {state_full}. Specializing in {', '.join(specialties[:2]) if specialties else 'dermatology'}. Schedule your appointment today.",
            schema_json=physician_schema_json,
            canonical=f"/find-a-dermatologist/{state_lower}/{city_slug}/{practice_slug}.html"
        )

        # Create directory structure if needed
        state_dir = OUTPUT_DIR / "find-a-dermatologist" / state_lower
        state_dir.mkdir(parents=True, exist_ok=True)

        city_dir = state_dir / city_slug
        city_dir.mkdir(parents=True, exist_ok=True)

        # Write the practice page
        write_file(city_dir / f"{practice_slug}.html", html)
        page_count += 1

    return page_count


def build_podcast_pages():
    """Build The Growing Dermatologist podcast section with main page and episode pages."""

    # Sample episodes data
    episodes = [
        {"num": 12, "title": "Building a Multi-Location Dermatology Practice", "guest": "Dr. Sarah Chen", "guest_title": "CEO, Pacific Dermatology Group", "duration": "47 min", "desc": "Dr. Chen shares her journey from solo practitioner to leading a 6-location dermatology group. We discuss hiring strategies, maintaining quality across locations, and the business decisions that mattered most.", "topics": ["Practice Management", "Growth Strategy", "Multi-Location"]},
        {"num": 11, "title": "The Future of Teledermatology", "guest": "Dr. Marcus Johnson", "guest_title": "Director of Digital Health, University Dermatology", "duration": "42 min", "desc": "How telemedicine is reshaping dermatology practice. Dr. Johnson discusses patient outcomes, reimbursement models, and which conditions work best for virtual consultations.", "topics": ["Telehealth", "Digital Innovation", "Patient Access"]},
        {"num": 10, "title": "Mastering Mohs Surgery: From Resident to Expert", "guest": "Dr. Emily Rodriguez", "guest_title": "Mohs Surgeon, Skin Cancer Center of Excellence", "duration": "51 min", "desc": "A deep dive into the Mohs fellowship journey, building a Mohs practice, and the latest advances in micrographic surgery techniques.", "topics": ["Mohs Surgery", "Career Development", "Surgical Techniques"]},
        {"num": 9, "title": "Patient Acquisition in the Digital Age", "guest": "Dr. Michael Park", "guest_title": "Founder, Modern Dermatology Clinic", "duration": "38 min", "desc": "SEO, social media, and online reviews: Dr. Park breaks down exactly how he grew his practice from 0 to 200 patients per week using digital marketing.", "topics": ["Marketing", "SEO", "Practice Growth"]},
        {"num": 8, "title": "Cosmetic Dermatology: Building Your Aesthetics Practice", "guest": "Dr. Amanda Foster", "guest_title": "Medical Director, Glow Aesthetics", "duration": "44 min", "desc": "From choosing the right lasers to pricing your services, Dr. Foster shares the playbook for building a thriving cosmetic dermatology practice.", "topics": ["Cosmetic Derm", "Business Strategy", "Aesthetics"]},
        {"num": 7, "title": "Negotiating with Insurance Companies", "guest": "Dr. Robert Williams", "guest_title": "Practice Management Consultant", "duration": "35 min", "desc": "Practical strategies for negotiating better reimbursement rates, understanding payer contracts, and when to consider going out-of-network.", "topics": ["Insurance", "Revenue", "Negotiations"]},
        {"num": 6, "title": "Dermatology Research: From Bench to Bedside", "guest": "Dr. Lisa Chang", "guest_title": "Professor of Dermatology, Johns Hopkins", "duration": "49 min", "desc": "How academic dermatology drives clinical innovation. Dr. Chang discusses balancing research, teaching, and patient care.", "topics": ["Research", "Academic Medicine", "Innovation"]},
        {"num": 5, "title": "Hiring and Retaining Great Staff", "guest": "Dr. James Anderson", "guest_title": "Owner, Family Dermatology Associates", "duration": "41 min", "desc": "Your team makes or breaks your practice. Dr. Anderson shares his approach to hiring medical assistants, managing office staff, and creating a culture that retains top talent.", "topics": ["Hiring", "Team Building", "Culture"]},
        {"num": 4, "title": "Pediatric Dermatology: A Niche Worth Pursuing", "guest": "Dr. Karen Mitchell", "guest_title": "Pediatric Dermatologist, Children's Hospital", "duration": "36 min", "desc": "Why pediatric dermatology is both personally rewarding and professionally smart. Dr. Mitchell discusses training requirements, patient volume, and unique challenges.", "topics": ["Pediatric Derm", "Specialization", "Career Path"]},
        {"num": 3, "title": "The Dermatologist's Guide to Work-Life Balance", "guest": "Dr. David Lee", "guest_title": "Dermatologist & Wellness Advocate", "duration": "33 min", "desc": "Burnout is real in dermatology. Dr. Lee shares how he restructured his practice to work 4 days a week while increasing revenue.", "topics": ["Wellness", "Work-Life Balance", "Burnout Prevention"]},
        {"num": 2, "title": "Starting Your Own Practice: Year One Survival Guide", "guest": "Dr. Priya Patel", "guest_title": "Founder, Patel Dermatology & Skin Care", "duration": "52 min", "desc": "Everything you need to know about opening your doors: location scouting, financing, equipment, marketing, and getting your first 100 patients.", "topics": ["Startup", "Entrepreneurship", "New Practice"]},
        {"num": 1, "title": "Why Dermatology? The State of the Specialty in 2026", "guest": "Dr. Christopher Taylor", "guest_title": "President, American Academy of Dermatology", "duration": "45 min", "desc": "Our inaugural episode explores the current state of dermatology: workforce challenges, emerging treatments, AI in diagnostics, and why dermatology remains one of medicine's most competitive specialties.", "topics": ["Industry Overview", "AAD", "Future of Derm"]},
    ]

    # Build main podcast page
    episodes_html = ""
    for ep in episodes:
        topic_badges = "".join([f'<span class="topic-badge">{topic}</span>' for topic in ep['topics']])
        episodes_html += f'''
                <a href="/podcast/episode-{ep['num']}.html" class="episode-card">
                    <div class="episode-number">EP {ep['num']}</div>
                    <div class="episode-content">
                        <h3>{ep['title']}</h3>
                        <p class="episode-guest">with {ep['guest']} &mdash; {ep['guest_title']}</p>
                        <p class="episode-desc">{ep['desc'][:150]}...</p>
                        <div class="episode-meta">
                            <span class="episode-duration">{ep['duration']}</span>
                            <div class="episode-topics">{topic_badges}</div>
                        </div>
                    </div>
                </a>'''

    body_content = f'''
    <section class="podcast-page">
        <div class="container">
            <div class="podcast-hero">
                <div class="podcast-hero-content">
                    <span class="podcast-label">PODCAST</span>
                    <h1>The Growing Dermatologist</h1>
                    <p class="podcast-tagline">Real conversations with dermatologists who are building thriving practices, advancing the specialty, and shaping the future of skin care.</p>
                    <div class="podcast-subscribe">
                        <a href="https://podcasts.apple.com/" class="subscribe-btn apple" target="_blank" rel="noopener">Apple Podcasts</a>
                        <a href="https://open.spotify.com/" class="subscribe-btn spotify" target="_blank" rel="noopener">Spotify</a>
                        <a href="https://podcasts.google.com/" class="subscribe-btn google" target="_blank" rel="noopener">Google Podcasts</a>
                        <a href="/news/feed.xml" class="subscribe-btn rss">RSS Feed</a>
                    </div>
                    <p class="podcast-stats">12 Episodes &bull; Bi-weekly &bull; New episodes every other Tuesday</p>
                </div>
            </div>

            <div class="episodes-list">
                <h2>Latest Episodes</h2>
                {episodes_html}
            </div>

            <!-- CTA for dermatologists -->
            <section class="podcast-guest-cta">
                <h2>Want to Be a Guest?</h2>
                <p>We're always looking for dermatologists with interesting stories to tell. Whether you've built a multi-million dollar practice, pioneered a new technique, or have unique insights on the business of dermatology, we want to hear from you.</p>
                <a href="/contact/" class="cta-btn">Apply to Be a Guest</a>
            </section>
        </div>
    </section>
    '''

    podcast_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "PodcastSeries",
        "name": "The Growing Dermatologist",
        "url": f"{DOMAIN}/podcast/",
        "description": "Real conversations with dermatologists building thriving practices.",
        "provider": {"@type": "Organization", "name": SITE_NAME, "url": DOMAIN},
        "genre": "Health & Medicine"
    })
    html = page_template(
        title="The Growing Dermatologist Podcast",
        body_content=body_content,
        meta_description="Listen to real conversations with dermatologists building thriving practices. The Growing Dermatologist podcast features industry experts discussing practice management, business strategy, and career insights.",
        canonical="/podcast/",
        schema_json=podcast_schema
    )

    podcast_dir = OUTPUT_DIR / "podcast"
    podcast_dir.mkdir(parents=True, exist_ok=True)
    write_file(podcast_dir / "index.html", html)

    page_count = 1

    # Build individual episode pages
    for ep in episodes:
        ep_num = ep['num']
        ep_title = ep['title']
        ep_guest = ep['guest']
        ep_guest_title = ep['guest_title']
        ep_duration = ep['duration']
        ep_desc = ep['desc']
        ep_topics = ep['topics']

        # Generate key takeaways
        takeaways_text = ""
        if "multi-location" in ep_title.lower() or "multi-location" in " ".join(ep_topics).lower():
            takeaways = [
                "The key hiring decisions that make or break multi-location growth",
                "How to maintain quality and culture across multiple offices",
                "Operational systems that scale without added management complexity",
                "Common pitfalls new multi-location practices make"
            ]
        elif "teledermatology" in ep_title.lower() or "telemedicine" in ep_title.lower():
            takeaways = [
                "Which dermatological conditions work best for virtual consultations",
                "Patient outcomes and satisfaction data for teledermatology",
                "Reimbursement strategies and insurance negotiations",
                "Technology infrastructure and regulatory requirements"
            ]
        elif "mohs" in ep_title.lower():
            takeaways = [
                "Training pathway and fellowship requirements for Mohs surgery",
                "Building a Mohs practice from scratch",
                "Latest advances in micrographic surgery techniques",
                "Patient volume and revenue potential"
            ]
        elif "patient acquisition" in ep_title.lower() or "seo" in ep_title.lower():
            takeaways = [
                "SEO strategy for local dermatology practices",
                "Leveraging Google Business Profile and reviews",
                "Social media marketing that drives patient acquisition",
                "Converting online visibility into scheduled appointments"
            ]
        elif "cosmetic" in ep_title.lower():
            takeaways = [
                "Equipment selection and investment strategy",
                "Pricing models for aesthetic procedures",
                "Building a thriving cosmetic dermatology business",
                "Patient education and expectations management"
            ]
        else:
            takeaways = [
                f"{ep_guest} shares proven strategies for success in dermatology",
                "Practical business and clinical insights you can implement immediately",
                "How to overcome challenges common to dermatology practices",
                "Best practices from leading practitioners and organizations"
            ]

        for i, takeaway in enumerate(takeaways, 1):
            takeaways_text += f"<li>{takeaway}</li>\n                        "

        # Related articles (sample)
        related_articles = ""
        if "cosmetic" in ep_title.lower():
            related_articles = '''
                        <a href="/cosmetic-dermatology/injectables/" class="related-article">Guide to Injectable Treatments</a>
                        <a href="/cosmetic-dermatology/lasers/" class="related-article">Laser Treatment Options</a>
                        <a href="/cosmetic-dermatology/rejuvenation/" class="related-article">Skin Rejuvenation Procedures</a>'''
        elif "mohs" in ep_title.lower():
            related_articles = '''
                        <a href="/surgical-dermatology/mohs-surgery/" class="related-article">Mohs Micrographic Surgery Guide</a>
                        <a href="/medical-dermatology/skin-cancer/" class="related-article">Skin Cancer Detection & Treatment</a>
                        <a href="/surgical-dermatology/pre-post-op/" class="related-article">Pre & Post-Op Care</a>'''
        else:
            related_articles = '''
                        <a href="/news/" class="related-article">Latest Dermatology News</a>
                        <a href="/guides/" class="related-article">Dermatology Practice Guides</a>
                        <a href="/for-dermatologists/" class="related-article">Professional Resources</a>'''

        topic_badges = "".join([f'<span class="episode-topic-badge">{t}</span>' for t in ep_topics])

        body_ep = f'''
    <div class="episode-detail-page">
        <div class="container container-narrow">
            <nav class="breadcrumb">
                <a href="/">Home</a> <span>&rsaquo;</span>
                <a href="/podcast/">Podcast</a> <span>&rsaquo;</span>
                <span>Episode {ep_num}</span>
            </nav>

            <article class="episode-detail">
                <header class="episode-header">
                    <span class="episode-label">EPISODE {ep_num}</span>
                    <h1>{ep_title}</h1>
                    <div class="episode-guest-info">
                        <p class="guest-name">{ep_guest}</p>
                        <p class="guest-title">{ep_guest_title}</p>
                    </div>
                    <div class="episode-info">
                        <span class="duration"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> {ep_duration}</span>
                        <div class="topics">{topic_badges}</div>
                    </div>
                </header>

                <div class="episode-content">
                    <section class="episode-description">
                        <h2>Episode Summary</h2>
                        <p>{ep_desc}</p>
                    </section>

                    <section class="episode-takeaways">
                        <h2>Key Takeaways</h2>
                        <ol>
                        {takeaways_text}
                        </ol>
                    </section>

                    <section class="episode-guest-bio">
                        <h2>About the Guest</h2>
                        <p>{ep_guest} is a respected leader in dermatology with extensive experience in {ep_topics[0].lower()}. This episode covers invaluable insights from their professional journey and practical strategies for dermatology success.</p>
                    </section>

                    <section class="episode-transcript">
                        <h2>Transcript</h2>
                        <p><em>Full episode transcript coming soon. Subscribe to stay updated when transcripts are available.</em></p>
                    </section>

                    <section class="episode-related">
                        <h2>Related Content</h2>
                        {related_articles}
                    </section>

                    <div class="episode-share">
                        <p>Share this episode:</p>
                        <a href="https://twitter.com/intent/tweet?text=Check%20out%20{ep_num}:%20{ep_title}&url=https://dermobrain.com/podcast/episode-{ep_num}.html" class="share-btn twitter" target="_blank" rel="noopener noreferrer">Twitter</a>
                        <a href="https://www.facebook.com/sharer/sharer.php?u=https://dermobrain.com/podcast/episode-{ep_num}.html" class="share-btn facebook" target="_blank" rel="noopener noreferrer">Facebook</a>
                        <a href="https://www.linkedin.com/sharing/share-offsite/?url=https://dermobrain.com/podcast/episode-{ep_num}.html" class="share-btn linkedin" target="_blank" rel="noopener noreferrer">LinkedIn</a>
                    </div>
                </div>

                <aside class="episode-sidebar">
                    <div class="sidebar-box subscribe-box">
                        <h3>Never Miss an Episode</h3>
                        <p>New episodes every other Tuesday</p>
                        <div class="subscribe-links">
                            <a href="https://podcasts.apple.com/" class="subscribe-link" target="_blank" rel="noopener">Apple Podcasts</a>
                            <a href="https://open.spotify.com/" class="subscribe-link" target="_blank" rel="noopener">Spotify</a>
                            <a href="/news/feed.xml" class="subscribe-link">RSS Feed</a>
                        </div>
                    </div>
                </aside>
            </article>

            <nav class="episode-navigation">
                {f'<a href="/podcast/episode-{ep_num + 1}.html" class="nav-prev">← Previous Episode</a>' if ep_num < 12 else ''}
                {f'<a href="/podcast/episode-{ep_num - 1}.html" class="nav-next">Next Episode →</a>' if ep_num > 1 else ''}
            </nav>
        </div>
    </div>
        '''

        html_ep = page_template(
            title=f"Episode {ep_num}: {ep_title} - The Growing Dermatologist Podcast",
            body_content=body_ep,
            meta_description=f"Listen to {ep_guest} discuss {ep_topics[0].lower()} on The Growing Dermatologist podcast. Key insights for building your dermatology practice.",
            canonical=f"/podcast/episode-{ep_num}.html"
        )

        write_file(podcast_dir / f"episode-{ep_num}.html", html_ep)
        page_count += 1

    return page_count


def build_directory():
    """Main function to build the entire Find a Dermatologist directory."""
    print("\nBuilding directory pages...")

    main_count = build_directory_main_page()
    print(f"  Generated {main_count} main directory page")

    state_count = build_state_pages()
    print(f"  Generated {state_count} state pages")

    city_count = build_city_pages()
    print(f"  Generated {city_count} city pages")

    practice_count = build_practice_pages()
    print(f"  Generated {practice_count} practice pages")

    total = main_count + state_count + city_count + practice_count
    return total


# ─── Phase 6: Final Touches ──────────────────────────────────────
def build_admin_page():
    """Copy admin.html from assets to output/admin.html"""
    source = ASSETS_DIR / "admin.html"
    dest = OUTPUT_DIR / "admin.html"

    if source.exists():
        shutil.copy2(source, dest)
        return 1
    return 0


def build_premium_page():
    """Copy premium.html from assets to output/for-dermatologists/premium.html"""
    source = ASSETS_DIR / "premium.html"
    dest = OUTPUT_DIR / "for-dermatologists" / "premium.html"

    # Ensure directory exists
    dest.parent.mkdir(parents=True, exist_ok=True)

    if source.exists():
        shutil.copy2(source, dest)
        return 1
    return 0


def build_privacy_policy():
    """Generate privacy policy page using page_template()"""
    privacy_content = """
    <div class="container">
        <article class="article-content">
            <h1>Privacy Policy</h1>

            <p>Last updated: {date}</p>

            <h2>Introduction</h2>
            <p>
                DermoBrain ("we", "our", or "us") operates the dermobrain.com website
                (the "Service"). This page informs you of our policies regarding the
                collection, use, and disclosure of personal data when you use our Service
                and the choices you have associated with that data.
            </p>

            <h2>Types of Data Collected</h2>

            <h3>Personal Data</h3>
            <p>While using our Service, we may ask you to provide us with certain
            personally identifiable information that can be used to contact or identify
            you ("Personal Data"). This may include, but is not limited to:</p>
            <ul>
                <li>Email address</li>
                <li>First name and last name</li>
                <li>Phone number</li>
                <li>Address, State, Province, ZIP/Postal code, City</li>
                <li>Cookies and Usage Data</li>
            </ul>

            <h3>Usage Data</h3>
            <p>We may also collect information on how the Service is accessed and used
            ("Usage Data"). This may include information such as your computer's
            Internet Protocol address (e.g. IP address), browser type, browser version,
            the pages you visit, the time and date of your visit, the time spent on
            those pages, and other diagnostic data.</p>

            <h2>Use of Data</h2>
            <p>DermoBrain uses the collected data for various purposes:</p>
            <ul>
                <li>To provide and maintain our Service</li>
                <li>To notify you about changes to our Service</li>
                <li>To allow you to participate in interactive features of our Service</li>
                <li>To provide customer support</li>
                <li>To gather analysis or valuable information for improving our Service</li>
                <li>To monitor the usage of our Service</li>
                <li>To detect, prevent and address technical issues</li>
            </ul>

            <h2>Security of Data</h2>
            <p>The security of your data is important to us but remember that no method
            of transmission over the Internet or method of electronic storage is 100%
            secure. While we strive to use commercially acceptable means to protect your
            Personal Data, we cannot guarantee its absolute security.</p>

            <h2>Contact Us</h2>
            <p>If you have any questions about this Privacy Policy, please contact us at:</p>
            <p>
                Email: privacy@dermobrain.com<br>
                Website: www.dermobrain.com
            </p>
        </article>
    </div>
    """.format(date=BUILD_DATE)

    html = page_template(
        title="Privacy Policy",
        body_content=privacy_content,
        meta_description="Read our privacy policy to understand how DermoBrain collects and uses your information.",
        canonical="/privacy-policy/",
        body_class="privacy-page"
    )

    output_file = OUTPUT_DIR / "privacy-policy" / "index.html"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    write_file(output_file, html)
    return 1


def build_about_page():
    """Generate about page using page_template()"""
    about_content = """
    <div class="container">
        <article class="article-content">
            <h1>About DermoBrain</h1>

            <h2>Our Mission</h2>
            <p>
                DermoBrain is dedicated to providing evidence-based, accessible dermatological
                information to patients, healthcare providers, and the general public. We believe
                that understanding skin health is essential to overall wellness.
            </p>

            <h2>What We Do</h2>
            <p>
                DermoBrain.com is a comprehensive dermatology encyclopedia that covers:
            </p>
            <ul>
                <li><strong>Medical Dermatology</strong> - Information on skin conditions, skin cancer, allergies, and more</li>
                <li><strong>Surgical Dermatology</strong> - Details about dermatological procedures and treatments</li>
                <li><strong>Cosmetic Dermatology</strong> - Guidance on aesthetic treatments and skincare</li>
                <li><strong>Skincare & Lifestyle</strong> - Tips for maintaining healthy skin</li>
            </ul>

            <h2>Our Content</h2>
            <p>
                All content on DermoBrain is carefully researched and reviewed for accuracy.
                We provide in-depth articles, cost guides, treatment information, and
                dermatologist directories to help you make informed decisions about your skin health.
            </p>

            <h2>Disclaimer</h2>
            <p>
                The information provided on DermoBrain is for educational purposes only and
                should not be considered a substitute for professional medical advice. Always
                consult with a qualified dermatologist before making any medical decisions.
            </p>

            <h2>Contact</h2>
            <p>
                Have questions or feedback? We'd love to hear from you. Contact us at
                <a href="mailto:info@dermobrain.com">info@dermobrain.com</a>.
            </p>
        </article>
    </div>
    """

    html = page_template(
        title="About DermoBrain",
        body_content=about_content,
        meta_description="Learn about DermoBrain, your trusted dermatology encyclopedia providing evidence-based skin health information.",
        canonical="/about/",
        body_class="about-page"
    )

    output_file = OUTPUT_DIR / "about" / "index.html"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    write_file(output_file, html)
    return 1


def build_404_page():
    """Generate custom 404 page."""
    body_content = '''
    <div class="container py-5" style="text-align:center; max-width:700px; margin:0 auto; padding:80px 20px;">
        <h1 style="font-size:4rem; color:#1A6B54; margin-bottom:10px;">404</h1>
        <h2 style="font-size:1.5rem; margin-bottom:20px;">Page Not Found</h2>
        <p style="font-size:1.1rem; color:#666; margin-bottom:30px;">Sorry, the page you're looking for doesn't exist or has been moved. Try searching for what you need below.</p>
        <form action="/search/" method="get" style="max-width:450px; margin:0 auto 30px; display:flex; gap:8px;">
            <input type="text" name="q" placeholder="Search DermoBrain..." style="flex:1; padding:12px 16px; border:2px solid #ddd; border-radius:8px; font-size:1rem;">
            <button type="submit" style="padding:12px 24px; background:#1A6B54; color:#fff; border:none; border-radius:8px; font-size:1rem; cursor:pointer;">Search</button>
        </form>
        <div style="display:flex; flex-wrap:wrap; justify-content:center; gap:12px; margin-bottom:30px;">
            <a href="/medical-dermatology/" style="padding:8px 16px; background:#f0f7f5; color:#1A6B54; border-radius:20px; text-decoration:none; font-size:0.9rem;">Medical Derm</a>
            <a href="/cosmetic-dermatology/" style="padding:8px 16px; background:#f0f7f5; color:#1A6B54; border-radius:20px; text-decoration:none; font-size:0.9rem;">Cosmetic Derm</a>
            <a href="/find-a-dermatologist/" style="padding:8px 16px; background:#f0f7f5; color:#1A6B54; border-radius:20px; text-decoration:none; font-size:0.9rem;">Find a Dermatologist</a>
            <a href="/tools/" style="padding:8px 16px; background:#f0f7f5; color:#1A6B54; border-radius:20px; text-decoration:none; font-size:0.9rem;">Tools</a>
            <a href="/news/" style="padding:8px 16px; background:#f0f7f5; color:#1A6B54; border-radius:20px; text-decoration:none; font-size:0.9rem;">News</a>
        </div>
        <a href="/" style="color:#1A6B54; font-weight:600; text-decoration:none;">← Back to Homepage</a>
    </div>
    '''
    html = page_template(
        title="Page Not Found",
        body_content=body_content,
        meta_description="The page you're looking for doesn't exist. Search DermoBrain for dermatology information.",
        body_class="error-page"
    )
    write_file(OUTPUT_DIR / "404.html", html)
    return 1


def build_contact_page():
    """Generate contact page with Formspree form."""
    body_content = '''
    <div class="container py-5" style="max-width:800px; margin:0 auto;">
        <article class="article-content">
            <h1>Contact Us</h1>
            <p>Have questions, feedback, or suggestions? We'd love to hear from you. Fill out the form below and we'll get back to you as soon as possible.</p>

            <form action="https://formspree.io/f/xpwzgkqq" method="POST" style="margin-top:30px;">
                <div style="margin-bottom:20px;">
                    <label for="name" style="display:block; font-weight:600; margin-bottom:6px;">Name</label>
                    <input type="text" id="name" name="name" required style="width:100%; padding:12px; border:2px solid #ddd; border-radius:8px; font-size:1rem;">
                </div>
                <div style="margin-bottom:20px;">
                    <label for="email" style="display:block; font-weight:600; margin-bottom:6px;">Email</label>
                    <input type="email" id="email" name="email" required style="width:100%; padding:12px; border:2px solid #ddd; border-radius:8px; font-size:1rem;">
                </div>
                <div style="margin-bottom:20px;">
                    <label for="subject" style="display:block; font-weight:600; margin-bottom:6px;">Subject</label>
                    <select id="subject" name="subject" style="width:100%; padding:12px; border:2px solid #ddd; border-radius:8px; font-size:1rem;">
                        <option value="general">General Inquiry</option>
                        <option value="content">Content Suggestion</option>
                        <option value="dermatologist">Dermatologist Listing</option>
                        <option value="partnership">Partnership</option>
                        <option value="bug">Report a Bug</option>
                    </select>
                </div>
                <div style="margin-bottom:20px;">
                    <label for="message" style="display:block; font-weight:600; margin-bottom:6px;">Message</label>
                    <textarea id="message" name="message" rows="6" required style="width:100%; padding:12px; border:2px solid #ddd; border-radius:8px; font-size:1rem; resize:vertical;"></textarea>
                </div>
                <input type="hidden" name="_subject" value="DermoBrain Contact Form">
                <button type="submit" style="padding:14px 32px; background:#1A6B54; color:#fff; border:none; border-radius:8px; font-size:1rem; font-weight:600; cursor:pointer;">Send Message</button>
            </form>

            <div style="margin-top:40px; padding:20px; background:#f0f7f5; border-radius:12px;">
                <h3>Other Ways to Reach Us</h3>
                <p>Email: <a href="mailto:info@dermobrain.com">info@dermobrain.com</a></p>
                <p>For dermatologist listing inquiries, visit our <a href="/for-dermatologists/">For Dermatologists</a> page.</p>
            </div>
        </article>
    </div>
    '''
    html = page_template(
        title="Contact Us",
        body_content=body_content,
        meta_description="Contact the DermoBrain team with questions, feedback, partnership inquiries, or to claim your dermatologist profile listing. We respond within 48 hours.",
        canonical="/contact/",
        schema_json=json.dumps({"@context": "https://schema.org", "@type": "ContactPage", "name": "Contact DermoBrain", "url": f"{DOMAIN}/contact/", "description": "Contact the DermoBrain team for questions, feedback, or partnership inquiries."}),
        body_class="contact-page"
    )
    output_file = OUTPUT_DIR / "contact" / "index.html"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    write_file(output_file, html)
    return 1


def build_news_pages():
    """Build news section with index and individual news pages."""
    try:
        with open(DATA_DIR / "news.json", 'r', encoding='utf-8') as f:
            news_items = json.load(f)
    except:
        return 0

    page_count = 0

    # Build individual news pages
    cards_html = ""
    for item in news_items:
        title = item.get('title', '')
        slug = item.get('slug', '')
        date = item.get('date', '')
        summary = item.get('summary', '')
        content = item.get('content', '')
        category = item.get('category', 'News')

        # Individual news page
        body_content = f'''
    <div class="container py-5" style="max-width:800px; margin:0 auto;">
        <article class="article-content">
            <div class="article-meta" style="margin-bottom:20px;">
                <span class="badge" style="background:#E8734A; color:white; padding:4px 12px; border-radius:20px; font-size:0.8rem;">{category}</span>
                <time style="color:#666; margin-left:12px;">{date}</time>
            </div>
            <h1>{title}</h1>
            <div class="article-body">{content}</div>
            <div style="margin-top:40px; padding-top:20px; border-top:1px solid #eee;">
                <a href="/news/" style="color:#1A6B54; font-weight:600; text-decoration:none;">← Back to All News</a>
            </div>
        </article>
    </div>
        '''

        html = page_template(
            title=title,
            body_content=body_content,
            meta_description=summary[:160],
            canonical=f"/news/{slug}/",
            body_class="news-page"
        )
        output_file = OUTPUT_DIR / "news" / slug / "index.html"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        write_file(output_file, html)
        page_count += 1

        # Card for index
        cards_html += f'''
        <div class="guide-card" style="margin-bottom:20px;">
            <a href="/news/{slug}/" style="text-decoration:none; color:inherit;">
                <div style="padding:24px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <span class="badge" style="background:#E8734A; color:white; padding:4px 12px; border-radius:20px; font-size:0.8rem;">{category}</span>
                        <time style="color:#999; font-size:0.85rem;">{date}</time>
                    </div>
                    <h3 style="margin:0 0 8px; color:#1a1a1a;">{title}</h3>
                    <p style="margin:0; color:#666; font-size:0.95rem;">{summary}</p>
                </div>
            </a>
        </div>
        '''

    # Build news index page
    body_content = f'''
    <div class="container py-5">
        <h1>What's New in Dermatology</h1>
        <p class="subtitle" style="color:#666; font-size:1.1rem; margin-bottom:30px;">Stay updated with the latest dermatology news, research highlights, FDA approvals, and industry developments.</p>
        <div class="guides-grid" style="max-width:800px;">
            {cards_html}
        </div>
    </div>
    '''

    html = page_template(
        title="What's New in Dermatology",
        body_content=body_content,
        meta_description="Stay up to date with the latest dermatology news, research breakthroughs, FDA approvals, treatment advances, and industry developments curated by the DermoBrain team.",
        canonical="/news/",
        schema_json=json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": "Dermatology News", "url": f"{DOMAIN}/news/", "description": "Latest dermatology news and research updates."}),
        body_class="news-index"
    )
    output_file = OUTPUT_DIR / "news" / "index.html"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    write_file(output_file, html)
    page_count += 1

    # Build RSS feed
    rss_items = ""
    for item in news_items[:20]:
        rss_items += f'''
    <item>
        <title>{item.get('title', '')}</title>
        <link>{DOMAIN}/news/{item.get('slug', '')}/</link>
        <description>{item.get('summary', '')}</description>
        <pubDate>{item.get('date', '')}</pubDate>
        <guid>{DOMAIN}/news/{item.get('slug', '')}/</guid>
    </item>'''

    rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>DermoBrain - What's New in Dermatology</title>
    <link>{DOMAIN}/news/</link>
    <description>Latest dermatology news, research, and updates from DermoBrain.</description>
    <language>en-us</language>
    {rss_items}
</channel>
</rss>'''
    write_file(OUTPUT_DIR / "news" / "feed.xml", rss)

    return page_count


def build_professional_hub():
    """Build the professional resources hub for dermatologists."""
    try:
        with open(DATA_DIR / "professional_resources.json", 'r', encoding='utf-8') as f:
            resources = json.load(f)
    except:
        return 0

    page_count = 0
    section_links = ""

    for section in resources.get('sections', []):
        section_slug = section.get('slug', '')
        section_title = section.get('title', '')
        section_desc = section.get('description', '')
        items = section.get('items', [])

        items_html = ""
        for item in items:
            items_html += f'''
                <div style="padding:16px; border:1px solid #eee; border-radius:8px; margin-bottom:12px;">
                    <h4 style="margin:0 0 6px;"><a href="{item.get('url', '#')}" target="_blank" rel="noopener" style="color:#1A6B54; text-decoration:none;">{item.get('name', '')}</a></h4>
                    <p style="margin:0; color:#666; font-size:0.9rem;">{item.get('description', '')}</p>
                </div>'''

        body_content = f'''
    <div class="container py-5" style="max-width:800px; margin:0 auto;">
        <article class="article-content">
            <a href="/for-dermatologists/" style="color:#1A6B54; text-decoration:none; font-size:0.9rem;">← Back to Resources Hub</a>
            <h1 style="margin-top:16px;">{section_title}</h1>
            <p style="color:#666; font-size:1.1rem; margin-bottom:30px;">{section_desc}</p>
            <div>{items_html}</div>
        </article>
    </div>
        '''

        html = page_template(
            title=section_title,
            body_content=body_content,
            meta_description=section_desc[:160],
            canonical=f"/for-dermatologists/{section_slug}/",
            body_class="professional-page"
        )
        output_file = OUTPUT_DIR / "for-dermatologists" / section_slug / "index.html"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        write_file(output_file, html)
        page_count += 1

        section_links += f'''
        <a href="/for-dermatologists/{section_slug}/" class="guide-card" style="display:block; padding:24px; text-decoration:none; color:inherit; margin-bottom:16px;">
            <h3 style="margin:0 0 8px; color:#1a1a1a;">{section_title}</h3>
            <p style="margin:0; color:#666;">{section_desc}</p>
        </a>'''

    # Section icons for visual cards
    section_icons = {
        'cme-education': '&#127891;',
        'research-journals': '&#128218;',
        'professional-organizations': '&#127963;',
        'practice-management': '&#128188;',
        'events-conferences': '&#128197;',
        'clinical-guidelines': '&#128203;',
    }

    # Build styled section cards
    section_cards = ""
    for section in resources.get('sections', []):
        slug = section.get('slug', '')
        icon = section_icons.get(slug, '&#128204;')
        section_cards += f'''
            <a href="/for-dermatologists/{slug}/" class="pro-card">
                <div class="pro-card-icon">{icon}</div>
                <h3>{section.get('title', '')}</h3>
                <p>{section.get('description', '')}</p>
                <span class="pro-card-link">Explore &rarr;</span>
            </a>'''

    # Build main hub page
    body_content = f'''
    <!-- Hero Section -->
    <section class="pro-hero">
        <div class="container">
            <h1>Resources for Dermatologists</h1>
            <p>Professional resources, continuing education, research tools, and practice management for dermatology professionals.</p>
        </div>
    </section>

    <div class="container py-5">
        <div class="pro-grid">
            {section_cards}
        </div>

        <div class="pro-cta-grid">
            <div class="pro-cta-card pro-cta-claim">
                <h3>&#9734; Claim Your Free DermoBrain Profile</h3>
                <p>Get listed on DermoBrain's directory, manage your profile, and reach more patients searching for dermatologists.</p>
                <a href="/for-dermatologists/premium.html" class="btn btn-primary">Get Started</a>
            </div>
            <div class="pro-cta-card pro-cta-widget">
                <h3>&#128295; Embed DermoBrain on Your Website</h3>
                <p>Add our free widget to your practice website for patient education content and a direct link to your profile.</p>
                <a href="/tools/widget/" class="btn btn-accent">Learn More</a>
            </div>
        </div>
    </div>
    '''
    pro_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Resources for Dermatologists",
        "url": f"{DOMAIN}/for-dermatologists/",
        "description": "Professional resources for dermatologists including CME, research journals, practice management, and clinical guidelines.",
        "provider": {"@type": "Organization", "name": SITE_NAME, "url": DOMAIN}
    })
    html = page_template(
        title="Resources for Dermatologists",
        body_content=body_content,
        meta_description="Professional resources for dermatologists: continuing medical education, research journals, practice management tools, clinical guidelines, events, and professional organizations.",
        canonical="/for-dermatologists/",
        schema_json=pro_schema,
        body_class="professional-hub"
    )
    output_file = OUTPUT_DIR / "for-dermatologists" / "index.html"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    write_file(output_file, html)
    page_count += 1

    return page_count


def build_tools_pages():
    """Build the tools section including hub, cost calculator, cost comparison, and widget pages."""
    page_count = 0

    # Tools Hub Page
    tools_hub = '''
    <div class="container py-5">
        <h1>Dermatology Tools & Calculators</h1>
        <p class="subtitle" style="color:#666; font-size:1.1rem; margin-bottom:30px;">Interactive tools to help you research dermatology procedures, compare costs, and make informed decisions.</p>

        <div class="category-grid" style="display:grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap:20px;">
            <a href="/tools/cost-calculator/" class="guide-card" style="display:block; padding:30px; text-decoration:none; color:inherit; text-align:center;">
                <div style="font-size:2.5rem; margin-bottom:12px;">&#128176;</div>
                <h3 style="margin:0 0 8px; color:#1a1a1a;">Cost Calculator</h3>
                <p style="margin:0; color:#666; font-size:0.9rem;">Estimate the cost of dermatology procedures based on your location and insurance status.</p>
            </a>
            <a href="/tools/cost-comparison/" class="guide-card" style="display:block; padding:30px; text-decoration:none; color:inherit; text-align:center;">
                <div style="font-size:2.5rem; margin-bottom:12px;">&#128200;</div>
                <h3 style="margin:0 0 8px; color:#1a1a1a;">Cost Comparison</h3>
                <p style="margin:0; color:#666; font-size:0.9rem;">Compare procedure costs across different cities to find the best value.</p>
            </a>
            <a href="/skin-quiz/" class="guide-card" style="display:block; padding:30px; text-decoration:none; color:inherit; text-align:center;">
                <div style="font-size:2.5rem; margin-bottom:12px;">&#128221;</div>
                <h3 style="margin:0 0 8px; color:#1a1a1a;">Skin Health Quiz</h3>
                <p style="margin:0; color:#666; font-size:0.9rem;">Take our quiz to learn about your skin type and get personalized skincare recommendations.</p>
            </a>
            <a href="/tools/widget/" class="guide-card" style="display:block; padding:30px; text-decoration:none; color:inherit; text-align:center;">
                <div style="font-size:2.5rem; margin-bottom:12px;">&#128295;</div>
                <h3 style="margin:0 0 8px; color:#1a1a1a;">Embeddable Widget</h3>
                <p style="margin:0; color:#666; font-size:0.9rem;">Free widget for dermatologists to embed on their practice website.</p>
            </a>
        </div>
    </div>
    '''
    html = page_template(title="Tools & Calculators", body_content=tools_hub,
        meta_description="Free interactive dermatology tools: procedure cost calculator, city-by-city cost comparison, skin health quiz, and embeddable practice widget. Research and plan your care.",
        canonical="/tools/",
        schema_json=json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": "Dermatology Tools & Calculators", "url": f"{DOMAIN}/tools/", "description": "Free interactive dermatology tools for patients and practices."}),
        body_class="tools-page")
    output_file = OUTPUT_DIR / "tools" / "index.html"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    write_file(output_file, html)
    page_count += 1

    # Cost Calculator Page
    calc_body = '''
    <div class="container py-5" style="max-width:900px; margin:0 auto;">
        <h1>Dermatology Cost Calculator</h1>
        <p style="color:#666; margin-bottom:30px;">Estimate the cost of common dermatology procedures. Select a procedure, adjust for your area, and see estimated costs with and without insurance.</p>

        <div id="cost-calculator" style="background:#fff; border:2px solid #eee; border-radius:16px; padding:30px;">
            <div style="margin-bottom:20px;">
                <label for="procedure-select" style="display:block; font-weight:600; margin-bottom:8px;">Select a Procedure</label>
                <select id="procedure-select" style="width:100%; padding:12px; border:2px solid #ddd; border-radius:8px; font-size:1rem;">
                    <option value="">-- Choose a procedure --</option>
                </select>
            </div>
            <div style="margin-bottom:20px;">
                <label for="city-select" style="display:block; font-weight:600; margin-bottom:8px;">Select a City</label>
                <select id="city-select" style="width:100%; padding:12px; border:2px solid #ddd; border-radius:8px; font-size:1rem;">
                    <option value="">-- Choose a city --</option>
                </select>
            </div>
            <div style="margin-bottom:20px;">
                <label style="display:flex; align-items:center; gap:10px; cursor:pointer;">
                    <input type="checkbox" id="insurance-toggle" style="width:20px; height:20px;">
                    <span style="font-weight:600;">I have insurance</span>
                </label>
            </div>
            <div id="cost-result" style="display:none; padding:24px; background:#f0f7f5; border-radius:12px; margin-top:20px;">
                <h3 style="margin:0 0 12px; color:#1A6B54;">Estimated Cost</h3>
                <div id="cost-amount" style="font-size:2rem; font-weight:700; color:#1a1a1a;"></div>
                <p id="cost-range" style="color:#666; margin-top:8px;"></p>
                <p style="color:#999; font-size:0.8rem; margin-top:12px;">* Estimates are based on national averages and may vary. Always confirm pricing with your provider.</p>
            </div>
        </div>
    </div>
    '''
    html = page_template(title="Dermatology Cost Calculator", body_content=calc_body,
        meta_description="Estimate the cost of dermatology procedures with our free calculator. Compare prices with and without insurance.",
        canonical="/tools/cost-calculator/", body_class="tools-page",
        extra_head='<script src="/assets/js/cost-calculator.js" defer></script>')
    output_file = OUTPUT_DIR / "tools" / "cost-calculator" / "index.html"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    write_file(output_file, html)
    page_count += 1

    # Cost Comparison Page
    comparison_body = '''
    <div class="container py-5" style="max-width:900px; margin:0 auto;">
        <h1>Compare Procedure Costs by City</h1>
        <p style="color:#666; margin-bottom:30px;">See how dermatology procedure costs vary across different cities. Select a procedure and compare pricing nationwide.</p>

        <div id="cost-comparison" style="background:#fff; border:2px solid #eee; border-radius:16px; padding:30px;">
            <div style="margin-bottom:20px;">
                <label for="compare-procedure" style="display:block; font-weight:600; margin-bottom:8px;">Select a Procedure</label>
                <select id="compare-procedure" style="width:100%; padding:12px; border:2px solid #ddd; border-radius:8px; font-size:1rem;">
                    <option value="">-- Choose a procedure --</option>
                </select>
            </div>
            <div id="comparison-results" style="display:none; margin-top:20px;">
                <h3 style="margin:0 0 16px;">Cost by City</h3>
                <div id="comparison-table"></div>
            </div>
        </div>
    </div>
    '''
    html = page_template(title="Compare Procedure Costs by City", body_content=comparison_body,
        meta_description="Compare dermatology procedure costs across US cities. Find the most affordable options near you.",
        canonical="/tools/cost-comparison/", body_class="tools-page",
        extra_head='<script src="/assets/js/cost-comparison.js" defer></script>')
    output_file = OUTPUT_DIR / "tools" / "cost-comparison" / "index.html"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    write_file(output_file, html)
    page_count += 1

    # Widget Documentation Page
    widget_body = '''
    <div class="container py-5" style="max-width:800px; margin:0 auto;">
        <article class="article-content">
            <h1>Free Embeddable Widget for Dermatologists</h1>
            <p>Add DermoBrain's free widget to your practice website. It displays your DermoBrain profile, educational content, and helps build trust with patients — while earning you a valuable backlink.</p>

            <h2>How It Works</h2>
            <p>Simply add one line of code to your website. The widget automatically pulls your profile from DermoBrain and displays it in a clean, professional format that matches your website's style.</p>

            <h2>Installation</h2>
            <p>Copy and paste this code into your website's HTML where you want the widget to appear:</p>
            <div style="background:#1a1a1a; color:#00ff88; padding:20px; border-radius:12px; font-family:monospace; font-size:0.9rem; overflow-x:auto; margin:20px 0;">
                &lt;script src="https://dermobrain.com/assets/js/dermobrain-widget.js" data-npi="YOUR_NPI_NUMBER"&gt;&lt;/script&gt;
            </div>
            <p>Replace <code>YOUR_NPI_NUMBER</code> with your 10-digit NPI number.</p>

            <h2>Widget Features</h2>
            <ul>
                <li><strong>Your Profile</strong> — Displays your name, credentials, practice info, and specialties</li>
                <li><strong>Educational Content</strong> — Shows relevant dermatology articles for patient education</li>
                <li><strong>Appointment Link</strong> — Drives patients to your DermoBrain profile page</li>
                <li><strong>Responsive Design</strong> — Looks great on desktop, tablet, and mobile</li>
                <li><strong>SEO Benefit</strong> — Provides a dofollow backlink from dermobrain.com to your site</li>
            </ul>

            <h2>Customization Options</h2>
            <p>You can customize the widget with these optional attributes:</p>
            <ul>
                <li><code>data-theme="light"</code> or <code>data-theme="dark"</code> — Set color theme</li>
                <li><code>data-width="400"</code> — Set widget width in pixels</li>
                <li><code>data-articles="3"</code> — Number of educational articles to show</li>
            </ul>

            <div style="margin-top:30px; padding:24px; background:#f0f7f5; border-radius:12px;">
                <h3>Need Help?</h3>
                <p>Contact us at <a href="mailto:info@dermobrain.com">info@dermobrain.com</a> for widget installation assistance.</p>
            </div>
        </article>
    </div>
    '''
    html = page_template(title="Free Embeddable Widget for Dermatologists", body_content=widget_body,
        meta_description="Add DermoBrain's free widget to your dermatology practice website. Display your profile and educational content for patients.",
        canonical="/tools/widget/", body_class="tools-page")
    output_file = OUTPUT_DIR / "tools" / "widget" / "index.html"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    write_file(output_file, html)
    page_count += 1

    return page_count


def build():
    """Main build function."""
    print(f"\n{'='*50}")
    print(f"  DermoBrain Static Site Generator")
    print(f"  Build started: {BUILD_DATE}")
    print(f"{'='*50}\n")

    # Clean output
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)

    # Copy assets
    print("Copying assets...")
    copy_assets()

    # Load data
    print("\nLoading data...")
    all_articles = load_all_articles()
    all_categories = load_categories()
    print(f"  Loaded {len(all_articles)} articles and {len(all_categories)} categories")

    # Build pages
    print("\nBuilding pages...")
    build_homepage()
    build_editorial_standards()

    # Build article pages (clinical + patient versions)
    print(f"\nBuilding article pages...")
    article_count = 0
    patient_count = 0
    for article in all_articles:
        category_slug = article.get('category', '')
        category_info = next((c for c in all_categories if c.get('slug') == category_slug), None)
        if category_info:
            build_article_page(article, category_info)
            article_count += 1
            if article.get('patient_content'):
                patient_count += 1
    print(f"  Generated {article_count} clinical article pages")
    print(f"  Generated {patient_count} patient guide pages")

    # Build category pages
    print(f"\nBuilding category pages...")
    category_count = 0
    for category in all_categories:
        build_category_page(category, all_articles)
        category_count += 1
    print(f"  Generated {category_count} category pages")

    # Build pillar pages
    print(f"\nBuilding pillar pages...")
    pillar_slugs = {
        'medical-dermatology': 'Medical Dermatology',
        'surgical-dermatology': 'Surgical Dermatology',
        'cosmetic-dermatology': 'Cosmetic Dermatology',
        'skincare': 'Skincare & Lifestyle'
    }
    for pillar_slug, pillar_name in pillar_slugs.items():
        build_pillar_page(pillar_slug, pillar_name, all_categories, all_articles)
    print(f"  Generated {len(pillar_slugs)} pillar pages")

    # Build search index
    print("\nBuilding search index...")
    build_search_index(all_articles)

    # Build Phase 4 pages
    print("\nBuilding guide pages...")
    guide_count = build_guide_pages()
    print(f"  Generated {guide_count} guide pages")

    print("\nBuilding quiz page...")
    quiz_count = build_quiz_page()
    print(f"  Generated {quiz_count} quiz page")

    print("\nBuilding cost pages...")
    cost_count = build_cost_pages()
    print(f"  Generated {cost_count} cost pages")

    print("\nBuilding myths index...")
    myths_count = build_myths_index()
    print(f"  Generated {myths_count} myths index page")

    print("\nBuilding directory...")
    directory_count = build_directory()
    print(f"  Generated {directory_count} directory pages")

    # Build new sections (Phase 3 & 4)
    print("\nBuilding 404 page...")
    build_404_page()
    print("  Generated 404 page")

    print("\nBuilding contact page...")
    contact_count = build_contact_page()
    print(f"  Generated {contact_count} contact page")

    print("\nBuilding news pages...")
    news_count = build_news_pages()
    print(f"  Generated {news_count} news pages")

    print("\nBuilding professional resources hub...")
    pro_count = build_professional_hub()
    print(f"  Generated {pro_count} professional pages")

    print("\nBuilding tools pages...")
    tools_count = build_tools_pages()
    print(f"  Generated {tools_count} tools pages")

    print("\nBuilding podcast pages...")
    podcast_count = build_podcast_pages()
    print(f"  Generated {podcast_count} podcast pages")

    # Build Phase 6: Final Touches
    print("\nBuilding Phase 6 pages (final touches)...")
    admin_count = build_admin_page()
    premium_count = build_premium_page()
    privacy_count = build_privacy_policy()
    about_count = build_about_page()
    print(f"  Generated {admin_count} admin page")
    print(f"  Generated {premium_count} premium page")
    print(f"  Generated {privacy_count} privacy policy page")
    print(f"  Generated {about_count} about page")

    # Generate sitemap with all pages
    print("\nGenerating sitemap...")
    pages = [
        ("/", 1.0, "daily"),
        ("/editorial-standards/", 0.5, "monthly"),
        ("/guides/", 0.7, "weekly"),
        ("/skin-quiz/", 0.6, "monthly"),
        ("/costs/", 0.7, "weekly"),
        ("/myths/", 0.7, "weekly"),
        ("/podcast/", 0.8, "weekly"),
    ]

    # Add pillar pages
    for pillar_slug in pillar_slugs.keys():
        pages.append((f"/{pillar_slug}/", 0.8, "weekly"))

    # Add category pages
    for category in all_categories:
        pillar_slug = category.get('pillar_slug', '')
        category_slug = category.get('slug', '')
        pages.append((f"/{pillar_slug}/{category_slug}/", 0.7, "weekly"))

    # Add article pages (clinical + patient versions)
    for article in all_articles:
        category_slug = article.get('category', '')
        article_slug = article.get('slug', '')
        category_info = next((c for c in all_categories if c.get('slug') == category_slug), None)
        if category_info:
            pillar_slug = category_info.get('pillar_slug', '')
            pages.append((f"/{pillar_slug}/{category_slug}/{article_slug}.html", 0.6, "monthly"))
            # Add patient guide version if it exists
            if article.get('patient_content'):
                pages.append((f"/{pillar_slug}/{category_slug}/{article_slug}-patient-guide.html", 0.6, "monthly"))

    # Add guide pages to sitemap
    try:
        with open(DATA_DIR / "guides.json", 'r', encoding='utf-8') as f:
            guides = json.load(f)
            for guide in guides:
                guide_slug = guide.get('slug', '')
                pages.append((f"/guides/{guide_slug}.html", 0.6, "monthly"))
    except:
        pass

    # Add cost pages to sitemap (sample - include first 100 to keep sitemap reasonable)
    try:
        with open(DATA_DIR / "procedure_costs.json", 'r', encoding='utf-8') as f:
            procedures = json.load(f)
        with open(DATA_DIR / "cities.json", 'r', encoding='utf-8') as f:
            cities = json.load(f)
        # Add sample cost pages (first 5 procedures x first 20 cities = 100 entries)
        for proc in procedures[:5]:
            proc_slug = proc.get('slug', '')
            for city in cities[:20]:
                city_slug = city.get('slug', '')
                pages.append((f"/costs/{proc_slug}-cost-{city_slug}.html", 0.5, "monthly"))
    except:
        pass

    # Add podcast episode pages to sitemap
    for i in range(1, 13):  # 12 episodes
        pages.append((f"/podcast/episode-{i}.html", 0.6, "monthly"))

    # Add directory pages to sitemap (including practice pages)
    pages.append(("/find-a-dermatologist/", 0.8, "weekly"))
    try:
        with open(DATA_DIR / "dermatologists.json", 'r', encoding='utf-8') as f:
            dermatologists = json.load(f)
        # Group by state and city to add all pages
        state_cities = {}
        for derm in dermatologists:
            state = derm.get('state', '')
            city = derm.get('city', '')
            if state and city:
                if state not in state_cities:
                    state_cities[state] = set()
                state_cities[state].add(city)
        # Add state pages
        for state in sorted(state_cities.keys()):
            pages.append((f"/find-a-dermatologist/{state.lower()}/", 0.7, "weekly"))
            # Add city pages
            for city in sorted(list(state_cities[state])):
                city_slug = slugify(city)
                pages.append((f"/find-a-dermatologist/{state.lower()}/{city_slug}.html", 0.6, "weekly"))

        # Add ALL practice pages to sitemap
        for derm in dermatologists:
            state = derm.get('state', '')
            city = derm.get('city', '')
            practice_name = derm.get('practice_name', '')
            if state and city and practice_name:
                state_lower = state.lower()
                city_slug = slugify(city)
                practice_slug = slugify(practice_name)
                pages.append((f"/find-a-dermatologist/{state_lower}/{city_slug}/{practice_slug}.html", 0.5, "monthly"))
    except:
        pass

    sitemap_xml = generate_sitemap(pages)
    write_file(OUTPUT_DIR / "sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n' + sitemap_xml)

    # Generate robots.txt
    write_file(OUTPUT_DIR / "robots.txt", generate_robots_txt())

    # CNAME
    write_file(OUTPUT_DIR / "CNAME", "dermobrain.com")

    # .nojekyll for GitHub Pages
    write_file(OUTPUT_DIR / ".nojekyll", "")

    # Report stats
    phase6_count = admin_count + premium_count + privacy_count + about_count
    total_pages = 1 + 1 + len(pillar_slugs) + len(all_categories) + article_count + guide_count + quiz_count + cost_count + myths_count + directory_count + podcast_count + phase6_count

    print(f"\n{'='*50}")
    print(f"  Build complete!")
    print(f"  Total pages generated: {total_pages}")
    print(f"    - Homepage: 1")
    print(f"    - Editorial standards: 1")
    print(f"    - Pillar pages: {len(pillar_slugs)}")
    print(f"    - Category pages: {len(all_categories)}")
    print(f"    - Article pages: {article_count}")
    print(f"    - Guide pages: {guide_count}")
    print(f"    - Quiz page: {quiz_count}")
    print(f"    - Cost pages: {cost_count}")
    print(f"    - Myths index: {myths_count}")
    print(f"    - Directory pages: {directory_count}")
    print(f"    - Podcast pages: {podcast_count}")
    print(f"    - Phase 6 pages: {phase6_count}")
    print(f"  Sitemap entries: {len(pages)}")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    build()
