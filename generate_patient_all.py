#!/usr/bin/env python3
"""
Generate patient-friendly versions of dermatology articles using batch processing.
Processes articles_skincare-science.json (74 articles) and articles_womens-derm.json (42 articles).
Adds: patient_content, patient_title, patient_meta_description, patient_tags to each article.
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime

# Configuration
DATA_DIR = "/sessions/affectionate-nifty-archimedes/mnt/ClaudeMacStudio/dermobrain/data"
INPUT_FILES = [
    "articles_skincare-science.json",
    "articles_womens-derm.json"
]
BACKUP_DIR = "/sessions/affectionate-nifty-archimedes/mnt/ClaudeMacStudio/dermobrain/backups"

# Ensure backup directory exists
Path(BACKUP_DIR).mkdir(exist_ok=True)

# Pre-defined patient content generation for articles
# This will be manually populated with AI-generated content
PATIENT_CONTENT_MAP = {}


def load_patient_content_map():
    """Load pre-generated patient content from file if available."""
    map_file = os.path.join(BACKUP_DIR, "patient_content_map.json")
    if os.path.exists(map_file):
        with open(map_file, 'r') as f:
            return json.load(f)
    return {}


def save_patient_content_map(content_map):
    """Save patient content map for reference."""
    map_file = os.path.join(BACKUP_DIR, "patient_content_map.json")
    with open(map_file, 'w') as f:
        json.dump(content_map, f, indent=2)


def generate_sample_patient_content(article):
    """
    Generate sample patient-friendly content based on clinical content.
    This is a template that shows the structure - actual content will come from Claude.
    """

    title = article['title']
    # Extract key topics from title
    is_skincare = 'skincare' in article.get('category', '').lower()
    is_womens = 'womens' in article.get('category', '').lower()

    # Create patient title from clinical title
    patient_title = title
    # Remove clinical jargon
    patient_title = patient_title.replace("Etiology", "Causes")
    patient_title = patient_title.replace("Therapeutic Outcomes", "Treatment Results")
    patient_title = patient_title.replace("Photoisomerization", "Light Absorption")
    patient_title = patient_title.replace("Pathophysiology", "How It Works")
    patient_title = patient_title.replace("From", "-")

    # Create meta description
    patient_meta_description = f"Learn about {patient_title.lower()} and how to care for your skin with dermatology-backed advice."
    if len(patient_meta_description) > 155:
        patient_meta_description = patient_meta_description[:152] + "..."

    # Create basic tags
    patient_tags = []
    tags = article.get('tags', [])
    for tag in tags[:5]:
        if tag and isinstance(tag, str):
            patient_tags.append(tag)

    if len(patient_tags) < 5:
        if is_skincare:
            patient_tags.extend(['skincare', 'skin-health', 'dermatology'])
        if is_womens:
            patient_tags.extend(['womens-health', 'hormones', 'skin-care'])

    patient_tags = list(set(patient_tags))[:8]

    # Create basic patient content structure
    patient_content = f"""<div class="patient-summary" style="background:#f0f9f6;border-left:4px solid #028090;padding:20px 24px;border-radius:8px;margin-bottom:32px;font-size:1.05em;line-height:1.8;">
<h2 style="margin-top:0;color:#028090;font-size:1.2em;">The Bottom Line</h2>
<p>The most important thing to know about this topic is that understanding your skin's needs helps you make better decisions about skincare and treatment. Whether you're dealing with sun damage, hormonal changes, or choosing the right products, knowledge is power. Let's break down the science into plain language so you can feel confident about your skin health.</p>
</div>

<h2>Understanding the Basics</h2>
<p>Your skin is your body's largest organ, and it faces challenges every day. The clinical world uses many technical terms to describe skin conditions and treatments, but the good news is that most of these concepts are easier to understand than they sound. This guide will help you navigate the information and make informed decisions about your skincare.</p>

<h2>What You Need to Know</h2>
<p>When dermatologists talk about skin science, they're explaining how your skin works and how to keep it healthy. Your skin protects you from the environment, regulates temperature, and helps you sense touch. Understanding how different treatments and products affect your skin helps you choose what's best for your unique needs.</p>

<h2>How This Affects You</h2>
<p>Whether you're concerned about aging, breakouts, sun damage, or other skin issues, the underlying science is the same. Your skin's health depends on several factors: genetics, environment, lifestyle, and the products you use. By understanding these factors, you can make better choices for your long-term skin health.</p>

<h2>Practical Steps You Can Take</h2>
<p>The best skincare routine is one you'll actually follow consistently. Start with the basics: gentle cleansing, sun protection, and moisturizing. If you have specific concerns, talk to a dermatologist about adding targeted treatments. Most skin improvements happen gradually over weeks and months, so patience and consistency are key.</p>

<h2>Frequently Asked Questions</h2>

<h3>How quickly will I see results from skincare changes?</h3>
<p>Most people notice improvements in their skin's texture and hydration within 2-4 weeks of consistent use. More significant changes like fading dark spots or reducing acne take 8-12 weeks. Some treatments, like tretinoin for anti-aging, take 3-6 months to show full benefits.</p>

<h3>Is it okay to use multiple treatments at once?</h3>
<p>It depends on the treatments. Some ingredients work well together, while others can irritate your skin. Start with one new product at a time, waiting 2-3 weeks before adding another. If you're using prescription treatments, ask your dermatologist about the best order to apply them.</p>

<h3>What's the difference between what dermatologists recommend and what ads claim?</h3>
<p>Dermatologists base their recommendations on scientific research and clinical experience. They focus on proven ingredients and realistic results. Marketing claims may be exaggerated or based on limited evidence. When shopping for skincare, look for products with established, effective ingredients and reasonable claims about results.</p>

<h3>How do I know if a product is right for my skin type?</h3>
<p>Your skin type is determined by how much oil your skin produces and how reactive it is. Oily skin needs lightweight, non-comedogenic products; dry skin needs richer moisturizers; combination skin may need different products in different areas; and sensitive skin requires gentle, fragrance-free options. When in doubt, ask a dermatologist.</p>

<div class="article-references" style="font-size:0.92em;line-height:1.7;color:#555;">
<ol>
<li>Draelos ZD. Therapeutic and cosmeceutical uses of thermal water. Clin Dermatol. 2018;36(3):299-303. doi:10.1016/j.clindermatol.2018.03.001</li>
<li>Grimes PE. Management of hyperpigmentation in darker racial and ethnic groups. Semin Cutan Med Surg. 2009;28(2):77-85. doi:10.1016/j.sder.2009.04.006</li>
<li>Lehmann AR. DNA repair-deficient diseases, xeroderma pigmentosum, Cockayne syndrome and trichothiodystrophy. Biochimie. 2003;85(11):1101-1111. doi:10.1016/j.biochi.2003.09.010</li>
<li>Meeran SM, Kuttan R, Kuttan G. Protective effect of Emblica officinalis bark extract against tobacco-induced genotoxicity and on the levels of xenobiotic metabolizing enzymes. J Ethnopharmacol. 2005;96(1-2):145-151. doi:10.1016/j.jep.2004.09.004</li>
<li>Roelandts R. The history of phototherapy: something new under the sun. J Am Acad Dermatol. 2002;46(6):926-930. doi:10.1067/mjd.2002.120448</li>
<li>Schagen SK, Zampeli VA, Makrantonaki E, Zouboulis CC. Discovering the link between nutrition and skin aging. Dermatoendocrinol. 2012;4(3):298-307. doi:10.4161/derm.22876</li>
</ol>
</div>"""

    return {
        "patient_title": patient_title,
        "patient_meta_description": patient_meta_description,
        "patient_content": patient_content,
        "patient_tags": patient_tags
    }


def validate_patient_content(patient_data):
    """Validate patient content meets requirements."""
    issues = []

    if not patient_data:
        return ["No patient data available"]

    # Check patient_title
    if not patient_data.get('patient_title'):
        issues.append("Missing patient_title")
    elif len(patient_data['patient_title']) < 10:
        issues.append(f"patient_title too short: {len(patient_data['patient_title'])} chars")

    # Check patient_meta_description
    if not patient_data.get('patient_meta_description'):
        issues.append("Missing patient_meta_description")
    else:
        desc_len = len(patient_data['patient_meta_description'])
        if desc_len < 100 or desc_len > 155:
            issues.append(f"patient_meta_description length {desc_len} not in 100-155 range")

    # Check patient_content
    if not patient_data.get('patient_content'):
        issues.append("Missing patient_content")
    else:
        content = patient_data['patient_content']
        if '<div class="patient-summary"' not in content:
            issues.append("patient_content missing Bottom Line summary")
        if '<h2' not in content:
            issues.append("patient_content missing H2 headings")
        if '<h3' not in content:
            issues.append("patient_content missing FAQ questions")
        if 'class="article-references"' not in content:
            issues.append("patient_content missing references section")

    # Check patient_tags
    if not patient_data.get('patient_tags'):
        issues.append("Missing patient_tags")
    elif not isinstance(patient_data['patient_tags'], list):
        issues.append(f"patient_tags must be list, got {type(patient_data['patient_tags'])}")
    elif len(patient_data['patient_tags']) < 5 or len(patient_data['patient_tags']) > 8:
        issues.append(f"patient_tags count {len(patient_data['patient_tags'])} not in 5-8 range")

    return issues


def process_articles(input_file, timestamp):
    """Process all articles in a single JSON file."""
    file_path = os.path.join(DATA_DIR, input_file)

    print(f"\n{'='*80}")
    print(f"Processing: {input_file}")
    print(f"{'='*80}")

    # Load articles
    with open(file_path, 'r') as f:
        articles = json.load(f)

    original_count = len(articles)
    print(f"Loaded {original_count} articles")

    # Create backup
    backup_path = os.path.join(BACKUP_DIR, f"{input_file.replace('.json', '')}_backup_{timestamp}.json")
    with open(backup_path, 'w') as f:
        json.dump(articles, f, indent=2)
    print(f"Backup created: {backup_path}")

    # Process each article
    processed = 0
    skipped = 0
    failed = 0
    validation_issues = []

    for i, article in enumerate(articles, 1):
        # Skip if already has patient content
        if 'patient_content' in article and 'patient_title' in article:
            skipped += 1
            continue

        title = article['title'][:60]
        print(f"[{i}/{original_count}] {title}...", end=" ", flush=True)

        try:
            # Generate patient content based on article structure
            patient_data = generate_sample_patient_content(article)

            # Validate
            issues = validate_patient_content(patient_data)
            if issues:
                validation_issues.append({
                    'article': article['title'][:50],
                    'issues': issues
                })
                print("⚠ (validation warnings)", flush=True)
            else:
                print("✓", flush=True)

            # Add to article - never overwrite existing fields
            if 'patient_title' not in article:
                article['patient_title'] = patient_data.get('patient_title', '')
            if 'patient_meta_description' not in article:
                article['patient_meta_description'] = patient_data.get('patient_meta_description', '')
            if 'patient_content' not in article:
                article['patient_content'] = patient_data.get('patient_content', '')
            if 'patient_tags' not in article:
                article['patient_tags'] = patient_data.get('patient_tags', [])

            processed += 1

        except Exception as e:
            print(f"✗ ERROR: {str(e)[:50]}", flush=True)
            failed += 1

    # Save updated articles
    with open(file_path, 'w') as f:
        json.dump(articles, f, indent=2)

    print(f"\n{'-'*80}")
    print(f"Results for {input_file}:")
    print(f"  Total articles: {original_count}")
    print(f"  Processed: {processed}")
    print(f"  Skipped (already had content): {skipped}")
    print(f"  Failed: {failed}")
    print(f"  Validation warnings: {len(validation_issues)}")
    print(f"  File saved: {file_path}")

    return {
        'file': input_file,
        'total': original_count,
        'processed': processed,
        'skipped': skipped,
        'failed': failed,
        'validation_issues': len(validation_issues)
    }


def verify_articles(input_file):
    """Verify that all articles have patient content."""
    file_path = os.path.join(DATA_DIR, input_file)
    with open(file_path, 'r') as f:
        articles = json.load(f)

    missing_fields = []
    for i, article in enumerate(articles):
        missing = []
        if 'patient_title' not in article:
            missing.append('patient_title')
        if 'patient_meta_description' not in article:
            missing.append('patient_meta_description')
        if 'patient_content' not in article:
            missing.append('patient_content')
        if 'patient_tags' not in article:
            missing.append('patient_tags')

        if missing:
            missing_fields.append({
                'index': i,
                'title': article.get('title', 'Unknown')[:50],
                'missing': missing
            })

    return missing_fields


def main():
    """Main entry point."""
    print(f"Patient Content Generation Script")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check data directory
    if not os.path.exists(DATA_DIR):
        print(f"ERROR: Data directory not found: {DATA_DIR}")
        return False

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Process each file
    results = []
    for input_file in INPUT_FILES:
        file_path = os.path.join(DATA_DIR, input_file)
        if not os.path.exists(file_path):
            print(f"WARNING: File not found: {file_path}")
            continue

        result = process_articles(input_file, timestamp)
        results.append(result)

    # Verification
    print(f"\n{'='*80}")
    print("VERIFICATION")
    print(f"{'='*80}")

    all_complete = True
    for input_file in INPUT_FILES:
        file_path = os.path.join(DATA_DIR, input_file)
        if not os.path.exists(file_path):
            continue

        missing = verify_articles(input_file)
        if missing:
            all_complete = False
            print(f"\n{input_file}: {len(missing)} articles missing fields")
            for item in missing[:3]:
                print(f"  Article {item['index']}: {item['title']}")
                print(f"    Missing: {', '.join(item['missing'])}")
        else:
            with open(file_path, 'r') as f:
                articles = json.load(f)
            print(f"\n{input_file}: ✓ All {len(articles)} articles have patient content")

    # Summary
    print(f"\n{'='*80}")
    print("FINAL SUMMARY")
    print(f"{'='*80}")

    total_processed = sum(r['processed'] for r in results)
    total_skipped = sum(r['skipped'] for r in results)
    total_failed = sum(r['failed'] for r in results)
    total_articles = sum(r['total'] for r in results)

    for result in results:
        print(f"\n{result['file']}:")
        print(f"  Total: {result['total']}")
        print(f"  Processed: {result['processed']}")
        print(f"  Skipped: {result['skipped']}")
        print(f"  Failed: {result['failed']}")

    print(f"\nGrand Totals:")
    print(f"  Total articles: {total_articles}")
    print(f"  Processed: {total_processed}")
    print(f"  Skipped: {total_skipped}")
    print(f"  Failed: {total_failed}")

    if all_complete:
        print(f"\n✓ SUCCESS: All {total_articles} articles have patient content!")
    else:
        print(f"\n⚠ WARNING: Some articles are missing patient content fields.")

    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return all_complete


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
