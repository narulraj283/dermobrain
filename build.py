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
    """Build the placeholder homepage."""
    body = '''
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
                <div class="stat"><strong>2,000+</strong> Articles</div>
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
                    <span class="pillar-count">880+ articles</span>
                </a>
                <a href="/surgical-dermatology/" class="pillar-card pillar-surgical">
                    <div class="pillar-icon">&#129658;</div>
                    <h3>Surgical Dermatology</h3>
                    <p>Mohs surgery, skin cancer surgery, surgical procedures, and pre/post-operative care.</p>
                    <span class="pillar-count">260+ articles</span>
                </a>
                <a href="/cosmetic-dermatology/" class="pillar-card pillar-cosmetic">
                    <div class="pillar-icon">&#10024;</div>
                    <h3>Cosmetic Dermatology</h3>
                    <p>Injectables, laser treatments, skin rejuvenation, body contouring, and anti-aging.</p>
                    <span class="pillar-count">440+ articles</span>
                </a>
            </div>
        </div>
    </section>

    <!-- Featured Articles (Placeholder) -->
    <section class="featured-section">
        <div class="container">
            <h2 class="section-title">Featured Articles</h2>
            <p class="section-subtitle">Latest expert-reviewed dermatology content</p>
            <div class="articles-grid">
                <div class="article-card placeholder-card">
                    <div class="article-card-image placeholder-img"></div>
                    <div class="article-card-body">
                        <span class="article-category">Medical Derm</span>
                        <h3>Understanding Eczema: Causes, Types, and Treatment</h3>
                        <p>A comprehensive guide to atopic dermatitis and related conditions.</p>
                    </div>
                </div>
                <div class="article-card placeholder-card">
                    <div class="article-card-image placeholder-img"></div>
                    <div class="article-card-body">
                        <span class="article-category">Surgical Derm</span>
                        <h3>What to Expect During Mohs Surgery</h3>
                        <p>Step-by-step guide to the gold standard in skin cancer removal.</p>
                    </div>
                </div>
                <div class="article-card placeholder-card">
                    <div class="article-card-image placeholder-img"></div>
                    <div class="article-card-body">
                        <span class="article-category">Cosmetic Derm</span>
                        <h3>Botox vs Fillers: Understanding the Difference</h3>
                        <p>Everything you need to know about injectable treatments.</p>
                    </div>
                </div>
                <div class="article-card placeholder-card">
                    <div class="article-card-image placeholder-img"></div>
                    <div class="article-card-body">
                        <span class="article-category">Skincare</span>
                        <h3>The Complete Guide to Retinoids</h3>
                        <p>From retinol to tretinoin — what works and how to use them.</p>
                    </div>
                </div>
            </div>
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

    # Build pages
    print("\nBuilding pages...")
    build_homepage()
    build_editorial_standards()

    # Generate sitemap
    print("\nGenerating sitemap...")
    pages = [
        ("/", 1.0, "daily"),
        ("/editorial-standards/", 0.5, "monthly"),
    ]
    sitemap_xml = generate_sitemap(pages)
    write_file(OUTPUT_DIR / "sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n' + sitemap_xml)

    # Generate robots.txt
    write_file(OUTPUT_DIR / "robots.txt", generate_robots_txt())

    # CNAME
    write_file(OUTPUT_DIR / "CNAME", "dermobrain.com")

    # .nojekyll for GitHub Pages
    write_file(OUTPUT_DIR / ".nojekyll", "")

    print(f"\n{'='*50}")
    print(f"  Build complete!")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    build()
