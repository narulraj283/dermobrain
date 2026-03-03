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
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

# ─── Configuration ───────────────────────────────────────────────
DOMAIN = "https://dermobrain.com"
SITE_NAME = "DermoBrain"
SITE_TAGLINE = "Your Trusted Dermatology Encyclopedia"
GA4_ID = "G-XXXXXXXXXX"  # Replace with real GA4 measurement ID

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"

BUILD_DATE = datetime.datetime.now().strftime("%Y-%m-%d")

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
            {"label": "Skin Cancer Surgery", "href": "/surgical-dermatology/skin-cancer-surgery/"},
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
            {"label": "Skincare Science", "href": "/skincare/science/"},
            {"label": "Men's Derm", "href": "/skincare/mens/"},
            {"label": "Women's Derm", "href": "/skincare/womens/"},
            {"label": "Lifestyle & Skin", "href": "/skincare/lifestyle/"},
        ]
    },
    {
        "label": "Find a Dermatologist",
        "href": "/find-a-dermatologist/",
        "dropdown": None
    },
    {
        "label": "Skin Quiz",
        "href": "/skin-quiz/",
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
    <meta property="og:title" content="{og_title}">
    <meta property="og:description" content="{og_desc}">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="{SITE_NAME}">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{og_title}">
    <meta name="twitter:description" content="{og_desc}">

    {schema_tag}

    <link rel="stylesheet" href="/assets/css/style.css">
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
                        <li><a href="/skin-quiz/">Skin Health Quiz</a></li>
                        <li><a href="/guides/">Expert Guides</a></li>
                        <li><a href="/myths/">Myths vs Facts</a></li>
                    </ul>
                </div>
                <div class="footer-links">
                    <h4>About</h4>
                    <ul>
                        <li><a href="/about/">About DermoBrain</a></li>
                        <li><a href="/editorial-standards/">Editorial Standards</a></li>
                        <li><a href="/privacy-policy/">Privacy Policy</a></li>
                        <li><a href="/sitemap.xml">Sitemap</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; {datetime.datetime.now().year} DermoBrain.com — All rights reserved.</p>
                <p class="footer-disclaimer">Content is for informational purposes only and does not constitute medical advice. Always consult a board-certified dermatologist.</p>
            </div>
        </div>
    </footer>

    <script src="/assets/js/main.js"></script>
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
                <div class="article-card">
                    <div class="article-card-image placeholder-img"></div>
                    <div class="article-card-body">
                        <span class="article-category">{category_name}</span>
                        <h3><a href="/{pillar_slug}/{category_slug}/{article_slug}.html">{article_title}</a></h3>
                        <p>{article_desc}</p>
                    </div>
                </div>'''

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
                <a href="/skincare/science/" class="category-card"><span class="cat-icon">&#128218;</span>Skincare Science</a>
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
                <p class="lead">At DermoBrain, we are committed to providing accurate, trustworthy, and up-to-date dermatology information. Every article on our site undergoes a rigorous editorial process.</p>

                <h2>Our Review Process</h2>
                <p>All content published on DermoBrain is created by experienced medical writers and reviewed by board-certified dermatologists. Our editorial team follows a multi-step process to ensure the highest quality of information:</p>

                <div class="standards-grid">
                    <div class="standard-card">
                        <h3>&#128221; Research</h3>
                        <p>Every article begins with thorough research using peer-reviewed medical journals, clinical guidelines from the American Academy of Dermatology (AAD), and established dermatological references.</p>
                    </div>
                    <div class="standard-card">
                        <h3>&#9997; Writing</h3>
                        <p>Our medical writers translate complex dermatological concepts into clear, accessible language while maintaining clinical accuracy.</p>
                    </div>
                    <div class="standard-card">
                        <h3>&#129658; Medical Review</h3>
                        <p>A board-certified dermatologist reviews every article for medical accuracy, ensuring all information reflects current clinical practice and evidence-based medicine.</p>
                    </div>
                    <div class="standard-card">
                        <h3>&#128260; Regular Updates</h3>
                        <p>We continuously update our content as new research emerges, treatment guidelines change, or new procedures become available.</p>
                    </div>
                </div>

                <h2>Content Principles</h2>
                <p>Our content adheres to the following principles:</p>
                <ul>
                    <li><strong>Evidence-Based:</strong> All medical claims are supported by peer-reviewed research and established clinical guidelines.</li>
                    <li><strong>Unbiased:</strong> We present treatment options objectively without favoring any specific product, brand, or procedure.</li>
                    <li><strong>Accessible:</strong> Complex medical topics are explained in plain language without sacrificing accuracy.</li>
                    <li><strong>Comprehensive:</strong> We cover all three pillars of dermatology — medical, surgical, and cosmetic — with equal depth and care.</li>
                    <li><strong>Inclusive:</strong> Our content addresses dermatological concerns across all skin types, tones, ages, and backgrounds.</li>
                </ul>

                <h2>Medical Disclaimer</h2>
                <p>The information on DermoBrain is intended for educational purposes only and should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult with a board-certified dermatologist or qualified healthcare provider for personalized medical guidance.</p>

                <h2>Contact Our Editorial Team</h2>
                <p>If you have questions about our editorial standards, notice an error in our content, or would like to suggest a topic, please contact us at <a href="mailto:editorial@dermobrain.com">editorial@dermobrain.com</a>.</p>
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

    # Social share buttons
    article_url = f"{DOMAIN}/{pillar_slug}/{category_slug}/{article_slug}.html"
    social_share = f'''
    <div class="social-share">
        <p>Share this article:</p>
        <a href="https://twitter.com/intent/tweet?url={article_url}&text={title}" class="share-btn twitter" target="_blank" rel="noopener">Twitter</a>
        <a href="https://www.facebook.com/sharer/sharer.php?u={article_url}" class="share-btn facebook" target="_blank" rel="noopener">Facebook</a>
        <button class="share-btn copy-link" onclick="navigator.clipboard.writeText('{article_url}'); alert('Link copied!');">Copy Link</button>
    </div>'''

    # Schema.org Article markup
    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "MedicalWebPage",
        "headline": title,
        "description": meta_desc,
        "url": article_url,
        "datePublished": BUILD_DATE,
        "dateModified": BUILD_DATE,
        "author": {
            "@type": "Organization",
            "name": "DermoBrain Medical Team"
        },
        "publisher": {
            "@type": "Organization",
            "name": SITE_NAME,
            "url": DOMAIN
        },
        "keywords": ", ".join(tags)
    })

    body = f'''
    <article class="article-page">
        <div class="container container-narrow">
            {breadcrumb}

            <header class="article-header">
                <span class="article-category">{category_name}</span>
                <h1>{title}</h1>
                <div class="article-meta">
                    <span class="byline">Written by DermoBrain Medical Team</span>
                    <span class="badge">Medically Reviewed</span>
                </div>
            </header>

            <div class="article-body">
                {content}
            </div>

            {social_share}
            {related_html}
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

    # Article cards grid
    articles_html = '<div class="articles-grid">'
    for article in category_articles[:12]:  # Limit display to 12 articles per page
        article_slug = article.get('slug', '')
        article_title = article.get('title', '')
        article_desc = article.get('meta_description', '')[:120] + "..."

        articles_html += f'''
        <div class="article-card">
            <div class="article-card-image placeholder-img"></div>
            <div class="article-card-body">
                <span class="article-category">{category_name}</span>
                <h3><a href="/{pillar_slug}/{category_slug}/{article_slug}.html">{article_title}</a></h3>
                <p>{article_desc}</p>
            </div>
        </div>'''
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
        <div class="category-item">
            <h3><a href="/{pillar_slug}/{cat_slug}/">{cat_name}</a></h3>
            <p>{cat_desc}</p>
            <span class="article-count">{article_count} articles</span>
        </div>'''
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

            <div class="categories-grid">
                {categories_html}
            </div>
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

        # Schema.org Article markup
        schema = json.dumps({
            "@context": "https://schema.org",
            "@type": "MedicalWebPage",
            "headline": title,
            "description": meta_desc,
            "url": f"{DOMAIN}/guides/{slug}.html",
            "datePublished": BUILD_DATE,
            "dateModified": BUILD_DATE,
            "author": {
                "@type": "Organization",
                "name": "DermoBrain Medical Team"
            },
            "publisher": {
                "@type": "Organization",
                "name": SITE_NAME,
                "url": DOMAIN
            },
            "keywords": ", ".join(tags)
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
    """Copy quiz.html from assets to output/skin-quiz/index.html."""
    try:
        quiz_src = ASSETS_DIR / "quiz.html"
        quiz_dst = OUTPUT_DIR / "skin-quiz" / "index.html"
        quiz_dst.parent.mkdir(parents=True, exist_ok=True)
        with open(quiz_src, 'r', encoding='utf-8') as f:
            quiz_content = f.read()
        write_file(quiz_dst, quiz_content)
        return 1
    except Exception as e:
        print(f"  Error copying quiz page: {e}")
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

                <div class="cost-cta">
                    <h3>Find a Dermatologist in {city_name}</h3>
                    <p>Get personalized quotes and schedule a consultation with board-certified dermatologists in your area.</p>
                    <a href="/find-a-dermatologist/" class="btn btn-primary">Find a Dermatologist &rarr;</a>
                </div>
            </div>
        </div>
    </section>'''

            # Simple schema for cost pages
            schema = json.dumps({
                "@context": "https://schema.org",
                "@type": "MedicalWebPage",
                "headline": title,
                "description": meta_desc,
                "url": f"{DOMAIN}/costs/{proc_slug}-cost-{city_slug}.html",
                "publisher": {
                    "@type": "Organization",
                    "name": SITE_NAME,
                    "url": DOMAIN
                }
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

    # Get unique states
    states_set = set()
    state_counts = {}
    for derm in dermatologists:
        state = derm.get('state', '')
        if state:
            states_set.add(state)
            state_counts[state] = state_counts.get(state, 0) + 1

    states_list = sorted(list(states_set))

    # State dropdown HTML
    state_options = "\n".join([f'                            <option value="{state}">{state}</option>' for state in states_list])

    # State cards grid
    state_cards = "\n".join([
        f'''            <a href="/find-a-dermatologist/{state.lower()}/" class="state-card">
                <h3>{state}</h3>
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
    <div class="container py-5">
        <h1>Find a Dermatologist</h1>
        <p class="subtitle">Search dermatologists by location</p>

        <div class="search-section">
            <div class="search-form">
                <div class="form-group">
                    <label for="stateSelect">Search by State:</label>
                    <select id="stateSelect" class="form-control">
                        <option value="">Select a state...</option>
                        {state_options}
                    </select>
                </div>

                <div class="form-group">
                    <label for="zipSearch">Search by ZIP Code:</label>
                    <input type="text" id="zipSearch" class="form-control" placeholder="Enter ZIP code">
                </div>
            </div>
        </div>

        <div class="states-grid">
            {state_cards}
        </div>
    </div>

    <script>
        document.getElementById('stateSelect').addEventListener('change', function(e) {{
            if (e.target.value) {{
                window.location.href = '/find-a-dermatologist/' + e.target.value.toLowerCase() + '/';
            }}
        }});
    </script>
    '''

    html = page_template(
        title="Find a Dermatologist",
        body_content=body_content,
        meta_description="Find and connect with dermatologists in your area. Search by state or ZIP code.",
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

    # Group dermatologists by state and city
    state_data = {}
    for derm in dermatologists:
        state = derm.get('state', '')
        city = derm.get('city', '')
        if state and city:
            if state not in state_data:
                state_data[state] = {}
            if city not in state_data[state]:
                state_data[state][city] = []
            state_data[state][city].append(derm)

    page_count = 0
    for state, cities in state_data.items():
        state_lower = state.lower()
        city_count = len(cities)
        total_derms = sum(len(derms) for derms in cities.values())

        # Build city list with counts
        city_list_items = "\n".join([
            f'''            <a href="/find-a-dermatologist/{state_lower}/{slugify(city)}.html" class="city-item">
                <h3>{city}</h3>
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
                {"@type": "ListItem", "position": 3, "name": state, "item": f"{DOMAIN}/find-a-dermatologist/{state_lower}/"}
            ]
        })

        body_content = f'''
    <div class="container py-5">
        <h1>Dermatologists in {state}</h1>
        <p class="subtitle">{total_derms} dermatologist{'s' if total_derms != 1 else ''} in {city_count} cit{'ies' if city_count != 1 else 'y'}</p>

        <div class="cities-grid">
            {city_list_items}
        </div>
    </div>
        '''

        html = page_template(
            title=f"Dermatologists in {state}",
            body_content=body_content,
            meta_description=f"Find dermatologists in {state}. Browse by city or search by specialty.",
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

    # Group dermatologists by state and city
    state_data = {}
    for derm in dermatologists:
        state = derm.get('state', '')
        city = derm.get('city', '')
        if state and city:
            if state not in state_data:
                state_data[state] = {}
            if city not in state_data[state]:
                state_data[state][city] = []
            state_data[state][city].append(derm)

    page_count = 0
    for state, cities in state_data.items():
        state_lower = state.lower()

        for city, derms in cities.items():
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
                    <p class="address">{address}<br>{city}, {state} {derm.get("zip", "")}</p>
                    <p class="phone">{phone_link}</p>
                    {specialty_badges}
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
                    {"@type": "ListItem", "position": 3, "name": state, "item": f"{DOMAIN}/find-a-dermatologist/{state_lower}/"},
                    {"@type": "ListItem", "position": 4, "name": city, "item": f"{DOMAIN}/find-a-dermatologist/{state_lower}/{city_slug}.html"}
                ]
            })

            body_content = f'''
    <div class="container py-5">
        <h1>{city}, {state}</h1>
        <p class="subtitle">{len(sorted_derms)} dermatologist{'s' if len(sorted_derms) != 1 else ''}</p>

        <div class="dermatologists-grid">
            {cards_html}
        </div>
    </div>
            '''

            html = page_template(
                title=f"Dermatologists in {city}, {state}",
                body_content=body_content,
                meta_description=f"Find dermatologists in {city}, {state}. View profiles, contact information, and specialties.",
                schema_json=breadcrumb_schema,
                canonical=f"/find-a-dermatologist/{state_lower}/{city_slug}.html"
            )

            write_file(OUTPUT_DIR / "find-a-dermatologist" / state_lower / f"{city_slug}.html", html)
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

    total = main_count + state_count + city_count
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

    # Build article pages
    print(f"\nBuilding article pages...")
    article_count = 0
    for article in all_articles:
        category_slug = article.get('category', '')
        category_info = next((c for c in all_categories if c.get('slug') == category_slug), None)
        if category_info:
            build_article_page(article, category_info)
            article_count += 1
    print(f"  Generated {article_count} article pages")

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
    ]

    # Add pillar pages
    for pillar_slug in pillar_slugs.keys():
        pages.append((f"/{pillar_slug}/", 0.8, "weekly"))

    # Add category pages
    for category in all_categories:
        pillar_slug = category.get('pillar_slug', '')
        category_slug = category.get('slug', '')
        pages.append((f"/{pillar_slug}/{category_slug}/", 0.7, "weekly"))

    # Add article pages
    for article in all_articles:
        category_slug = article.get('category', '')
        article_slug = article.get('slug', '')
        category_info = next((c for c in all_categories if c.get('slug') == category_slug), None)
        if category_info:
            pillar_slug = category_info.get('pillar_slug', '')
            pages.append((f"/{pillar_slug}/{category_slug}/{article_slug}.html", 0.6, "monthly"))

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

    # Add directory pages to sitemap
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
            # Add city pages (limit to keep sitemap manageable)
            for city in sorted(list(state_cities[state]))[:50]:  # Max 50 cities per state in sitemap
                city_slug = slugify(city)
                pages.append((f"/find-a-dermatologist/{state.lower()}/{city_slug}.html", 0.6, "weekly"))
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
    total_pages = 1 + 1 + len(pillar_slugs) + len(all_categories) + article_count + guide_count + quiz_count + cost_count + myths_count + directory_count + phase6_count

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
    print(f"    - Phase 6 pages: {phase6_count}")
    print(f"  Sitemap entries: {len(pages)}")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    build()
