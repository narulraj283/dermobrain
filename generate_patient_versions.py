#!/usr/bin/env python3
"""
Generate patient-friendly versions of dermatology articles.
Processes articles_skincare-science.json (74 articles) and articles_womens-derm.json (42 articles).
Adds: patient_content, patient_title, patient_meta_description, patient_tags to each article.
"""

import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime
import anthropic

# Configuration
DATA_DIR = "/sessions/affectionate-nifty-archimedes/mnt/ClaudeMacStudio/dermobrain/data"
INPUT_FILES = [
    "articles_skincare-science.json",
    "articles_womens-derm.json"
]
BACKUP_DIR = "/sessions/affectionate-nifty-archimedes/mnt/ClaudeMacStudio/dermobrain/backups"

# Ensure backup directory exists
Path(BACKUP_DIR).mkdir(exist_ok=True)

def generate_patient_content(client, article):
    """Generate patient-friendly content using Claude API."""

    prompt = f"""You are a medical writer creating patient-friendly explanations of dermatology articles for DermoBrain.com.

Clinical Article Title: {article['title']}
Category: {article['category']}
Subcategory: {article.get('subcategory', 'general')}

Clinical Content:
{article['content']}

Your task: Create a patient-friendly version with ALL of these components:

1. PATIENT-FRIENDLY TITLE (different from clinical, plain English):
   - Must be concise and understandable to general audience
   - Example: If clinical is "Photodynamic Therapy for Actinic Keratosis", patient version might be "How Light Therapy Treats Sun Damage"

2. BOTTOM LINE SUMMARY (3-4 plain English sentences):
   - Start with "The most important thing to know..."
   - Explain what the condition/treatment is in simple terms
   - Who should care about this
   - Example format: "The most important thing to know about sunscreen is that it protects your skin from UV damage. There are two main types - chemical and mineral - and they work differently on your skin. Both can be effective, but which is best for you depends on your skin type and preferences."

3. PATIENT-FRIENDLY HTML CONTENT (800-1200 words):
   - Grade 8-10 reading level (Flesch-Kincaid)
   - Use "you/your" at least 5+ times
   - Explain ALL medical terms in simple language when first used
   - Use H2 headings for sections
   - Organize logically: What is this? Why does it matter? How does it work? What should I do?
   - Include an FAQ section with 3-4 H3 questions that patients commonly ask
   - Include References section with 6-8 citations (mix of real study references and reliable sources)
   - Use real data/statistics/percentages from the clinical content
   - All HTML tags properly closed
   - CRITICAL: For references, format as:
     <div class="article-references" style="font-size:0.92em;line-height:1.7;color:#555;">
     <ol>
     <li>Author et al. Study Title. Journal. Year; Volume(Issue):Pages. doi:xxx</li>
     ...more citations...
     </ol>
     </div>

4. META DESCRIPTION (100-155 characters):
   - Must be patient-friendly, not clinical
   - Include key words naturally
   - Example: "Learn how sunscreen protects your skin, the difference between chemical and mineral types, and how to choose the right one for your skin."

5. TAGS (5-8 relevant tags as a list):
   - Patient-oriented, searchable terms
   - No underscores or special characters
   - Example: ["sunscreen", "SPF", "sun protection", "skin damage", "UV rays"]

CRITICAL MEDICAL ACCURACY REQUIREMENTS:
- Use real drug names (retinol, tretinoin, benzoyl peroxide, salicylic acid, etc.)
- Include actual percentages and concentrations mentioned in clinical content
- Reference real study data from the clinical content
- Do NOT invent statistics or treatments
- If clinical content mentions specific studies, treatments, or data, preserve accuracy

FORMATTING REQUIREMENTS:
- Start the HTML content immediately after the Bottom Line summary
- Wrap the Bottom Line in: <div class="patient-summary" style="background:#f0f9f6;border-left:4px solid #028090;padding:20px 24px;border-radius:8px;margin-bottom:32px;font-size:1.05em;line-height:1.8;"><h2 style="margin-top:0;color:#028090;font-size:1.2em;">The Bottom Line</h2><p>Your summary here</p></div>
- Use <h2> for main sections
- Use <h3> for FAQ questions
- Use proper <p> tags for paragraphs
- Ensure all HTML is valid and properly nested

Return ONLY a valid JSON object with these exact keys:
{{
    "patient_title": "...",
    "patient_meta_description": "...",
    "patient_content": "<div class=\\"patient-summary\\"...full HTML content...",
    "patient_tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}

Do NOT include explanations or preamble. Return ONLY the JSON object."""

    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = response.content[0].text.strip()

        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            json_str = json_match.group(0)
            patient_data = json.loads(json_str)
            return patient_data
        else:
            print(f"ERROR: No JSON found in response for article: {article['title'][:50]}")
            return None

    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in response for article: {article['title'][:50]}")
        print(f"  Details: {str(e)[:100]}")
        return None
    except Exception as e:
        print(f"ERROR: API call failed for article: {article['title'][:50]}")
        print(f"  Details: {str(e)[:100]}")
        return None


def validate_patient_content(article, patient_data):
    """Validate patient content meets all requirements."""
    issues = []

    if not patient_data:
        return ["No patient data generated"]

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
        content_len = len(patient_data['patient_content'])
        if content_len < 5000:  # Rough estimate for 800-1200 words in HTML
            issues.append(f"patient_content too short: {content_len} chars (expected 5000+)")
        if '<div class="patient-summary"' not in patient_data['patient_content']:
            issues.append("patient_content missing Bottom Line summary div")
        if '<h2' not in patient_data['patient_content']:
            issues.append("patient_content missing H2 headings")
        if '<h3' not in patient_data['patient_content']:
            issues.append("patient_content missing FAQ H3 questions")
        if 'class="article-references"' not in patient_data['patient_content']:
            issues.append("patient_content missing references section")

    # Check patient_tags
    if not patient_data.get('patient_tags'):
        issues.append("Missing patient_tags")
    elif not isinstance(patient_data['patient_tags'], list):
        issues.append(f"patient_tags must be list, got {type(patient_data['patient_tags'])}")
    elif len(patient_data['patient_tags']) < 5 or len(patient_data['patient_tags']) > 8:
        issues.append(f"patient_tags count {len(patient_data['patient_tags'])} not in 5-8 range")

    return issues


def process_articles(input_file, backup_suffix):
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
    backup_path = os.path.join(BACKUP_DIR, f"{input_file.replace('.json', '')}_backup_{backup_suffix}.json")
    with open(backup_path, 'w') as f:
        json.dump(articles, f, indent=2)
    print(f"Backup created: {backup_path}")

    # Initialize Anthropic client
    client = anthropic.Anthropic()

    # Process each article
    processed = 0
    skipped = 0
    errors = 0
    validation_issues = []

    for i, article in enumerate(articles, 1):
        # Skip if already has patient content
        if 'patient_content' in article:
            skipped += 1
            continue

        print(f"\n[{i}/{original_count}] Processing: {article['title'][:60]}...")

        # Generate patient content
        patient_data = generate_patient_content(client, article)

        if not patient_data:
            errors += 1
            continue

        # Validate
        issues = validate_patient_content(article, patient_data)
        if issues:
            validation_issues.append({
                'article': article['title'][:50],
                'issues': issues
            })
            print(f"  WARNING: Validation issues found")
            for issue in issues:
                print(f"    - {issue}")

        # Add to article
        article['patient_title'] = patient_data.get('patient_title', '')
        article['patient_meta_description'] = patient_data.get('patient_meta_description', '')
        article['patient_content'] = patient_data.get('patient_content', '')
        article['patient_tags'] = patient_data.get('patient_tags', [])

        processed += 1
        print(f"  ✓ Added patient content")

    # Save updated articles
    with open(file_path, 'w') as f:
        json.dump(articles, f, indent=2)

    print(f"\n{'-'*80}")
    print(f"Results for {input_file}:")
    print(f"  Total articles: {original_count}")
    print(f"  Processed: {processed}")
    print(f"  Skipped (already had content): {skipped}")
    print(f"  Errors: {errors}")
    print(f"  File saved: {file_path}")

    if validation_issues:
        print(f"\nValidation issues found in {len(validation_issues)} articles:")
        for item in validation_issues[:5]:  # Show first 5
            print(f"  - {item['article']}")
            for issue in item['issues'][:2]:
                print(f"    * {issue}")

    return {
        'file': input_file,
        'total': original_count,
        'processed': processed,
        'skipped': skipped,
        'errors': errors,
        'validation_issues': len(validation_issues)
    }


def main():
    """Main entry point."""
    print(f"Patient Content Generation Script")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)

    # Check data directory
    if not os.path.exists(DATA_DIR):
        print(f"ERROR: Data directory not found: {DATA_DIR}")
        sys.exit(1)

    # Process each file
    results = []
    for input_file in INPUT_FILES:
        file_path = os.path.join(DATA_DIR, input_file)
        if not os.path.exists(file_path):
            print(f"WARNING: File not found: {file_path}")
            continue

        result = process_articles(input_file, datetime.now().strftime('%Y%m%d_%H%M%S'))
        results.append(result)

    # Summary
    print(f"\n{'='*80}")
    print("FINAL SUMMARY")
    print(f"{'='*80}")

    total_processed = sum(r['processed'] for r in results)
    total_skipped = sum(r['skipped'] for r in results)
    total_errors = sum(r['errors'] for r in results)
    total_articles = sum(r['total'] for r in results)
    total_validation_issues = sum(r['validation_issues'] for r in results)

    for result in results:
        print(f"\n{result['file']}:")
        print(f"  Total: {result['total']}")
        print(f"  Processed: {result['processed']}")
        print(f"  Skipped: {result['skipped']}")
        print(f"  Errors: {result['errors']}")
        print(f"  Validation Issues: {result['validation_issues']}")

    print(f"\nGrand Totals (all files):")
    print(f"  Total articles: {total_articles}")
    print(f"  Processed: {total_processed}")
    print(f"  Skipped: {total_skipped}")
    print(f"  Errors: {total_errors}")
    print(f"  Validation Issues: {total_validation_issues}")

    if total_processed + total_skipped == total_articles and total_errors == 0:
        print(f"\n✓ SUCCESS: All {total_articles} articles processed!")
    else:
        print(f"\n⚠ WARNING: Some articles may not have been processed properly.")

    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
