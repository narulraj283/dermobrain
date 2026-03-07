#!/usr/bin/env python3
"""
Process dermatology articles to add patient-friendly versions.
Converts clinical content into 800-1200 word patient versions with proper formatting.
"""

import json
import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Any
import anthropic

# Configuration
DATA_DIR = Path("data")
LASERS_FILE = DATA_DIR / "articles_lasers.json"
LIFESTYLE_FILE = DATA_DIR / "articles_lifestyle.json"
BACKUP_DIR = Path("backups")
OUTPUT_DIR = DATA_DIR

# Ensure backup directory exists
BACKUP_DIR.mkdir(exist_ok=True)


def strip_html(html: str) -> str:
    """Remove HTML tags from text."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html).strip()


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def extract_medical_terms_and_concepts(clinical_content: str) -> Dict[str, Any]:
    """
    Extract key medical terms, percentages, drug names, and study data from clinical content.
    """
    # Extract percentages (e.g., "80-85%")
    percentages = re.findall(r'\d+(?:-\d+)?%', clinical_content)

    # Extract numbers with context (study results, durations)
    numbers = re.findall(r'\d+(?:-\d+)?\s+(?:weeks|months|years|patients|sessions|treatments)', clinical_content)

    # Extract common drug names and medical terms
    common_drugs = ['tretinoin', 'retinoids', 'hydroquinone', 'benzoyl peroxide', 'salicylic acid',
                   'glycolic acid', 'vitamin c', 'peptides', 'ceramides', 'hyaluronic acid',
                   'botox', 'fillers', 'sculptra', 'radiesse']
    found_drugs = []
    lower_content = clinical_content.lower()
    for drug in common_drugs:
        if drug in lower_content:
            found_drugs.append(drug)

    # Extract h2 sections to understand structure
    sections = re.findall(r'<h2[^>]*>([^<]+)</h2>', clinical_content)

    return {
        'percentages': percentages[:5],
        'numbers': numbers[:5],
        'drugs': found_drugs,
        'sections': sections[:6]
    }


def generate_patient_version(clinical_title: str, clinical_content: str, article_type: str) -> Dict[str, Any]:
    """
    Use Claude API to generate patient-friendly content.
    """
    client = anthropic.Anthropic()

    # Extract clinical information
    extracted_info = extract_medical_terms_and_concepts(clinical_content)

    # Create a detailed prompt for Claude
    prompt = f"""You are writing a patient-friendly guide about a dermatology topic for DermoBrain.com.

CLINICAL ARTICLE TITLE: {clinical_title}
ARTICLE TYPE: {article_type}

CLINICAL CONTENT (for reference):
{clinical_content[:3000]}

KEY INFORMATION FOUND:
- Percentages/stats: {', '.join(extracted_info['percentages']) if extracted_info['percentages'] else 'None'}
- Key medications/terms: {', '.join(extracted_info['drugs']) if extracted_info['drugs'] else 'None'}
- Duration/timeline info: {', '.join(extracted_info['numbers']) if extracted_info['numbers'] else 'None'}

TASK: Create a patient-friendly version with these EXACT specifications:

1. PATIENT TITLE: Create a simple, plain-English title (different from clinical title). Use "you/your" language. Examples:
   - Clinical: "CO2 Laser Resurfacing: Ablative Resurfacing for Wrinkles and Scars"
   - Patient: "Getting Rid of Wrinkles and Scars with CO2 Laser Treatment"

2. PATIENT META DESCRIPTION: 100-155 characters. SEO-optimized, includes your/your. Example:
   "Learn how CO2 laser treatment can smooth wrinkles and fade scars on your face. See results, recovery time, and what to expect."

3. PATIENT CONTENT (800-1200 words, HTML format):
   MUST START WITH:
   <div class="patient-summary" style="background:#f0f9f6;border-left:4px solid #028090;padding:20px 24px;border-radius:8px;margin-bottom:32px;font-size:1.05em;line-height:1.8;"><h2 style="margin-top:0;color:#028090;font-size:1.2em;">The Bottom Line</h2><p>[3-4 plain English sentences summarizing the treatment, its benefits, and who it helps]</p></div>

   REQUIREMENTS:
   - Grade 8-10 reading level (simple sentences, define medical terms)
   - Use "you" or "your" at least 5 times
   - Explain all medical/technical terms in simple language
   - Include H2 section headers
   - Include FAQ section with 3-4 questions as H3 headers
   - Include References section with 6-8 realistic citations
   - Word count: 800-1200 words (important!)
   - Medically accurate: use real drug names, actual percentages/data from clinical content
   - HTML formatting with proper tags

   STRUCTURE (modify as needed but include):
   - Bottom Line box (provided above)
   - Introduction: What this treatment is and why patients choose it
   - How It Works: Explain mechanism simply
   - Benefits: What you can expect
   - The Procedure: What happens during treatment
   - Recovery & Results: Timeline for healing and seeing results
   - Side Effects & Risks: Honest discussion
   - Is This Right for You: Candidacy and considerations
   - FAQ section (3-4 questions)
   - References (6-8 citations)

4. PATIENT TAGS: Create 5-8 simple, searchable tags (lowercase, comma-separated or as list items)
   Examples: wrinkles, laser treatment, skin resurfacing, acne scars, anti-aging

OUTPUT FORMAT (JSON):
{{
  "patient_title": "...",
  "patient_meta_description": "...",
  "patient_content": "...",
  "patient_tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}

CRITICAL:
- Return ONLY valid JSON
- Ensure content is 800-1200 words
- Check meta_description is 100-155 chars
- Ensure medical terms explained simply
- Include all required sections
- Use "your" or "you" extensively
"""

    try:
        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text

        # Parse the JSON response
        # Find JSON in the response (it might be wrapped in markdown code blocks)
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            json_str = json_match.group(0)
            result = json.loads(json_str)
            return result
        else:
            print(f"ERROR: Could not find JSON in response")
            print(f"Response: {response_text[:500]}")
            return None

    except json.JSONDecodeError as e:
        print(f"ERROR parsing JSON response: {e}")
        return None
    except Exception as e:
        print(f"ERROR calling Claude API: {e}")
        return None


def validate_patient_content(patient_data: Dict[str, Any], article_type: str) -> List[str]:
    """
    Validate that patient content meets all requirements.
    Returns list of validation errors (empty if valid).
    """
    errors = []

    # Check required fields
    required_fields = ['patient_title', 'patient_meta_description', 'patient_content', 'patient_tags']
    for field in required_fields:
        if field not in patient_data or not patient_data[field]:
            errors.append(f"Missing required field: {field}")

    if errors:
        return errors

    # Validate patient_title
    if len(patient_data['patient_title']) < 20 or len(patient_data['patient_title']) > 100:
        errors.append(f"patient_title length should be 20-100 chars, got {len(patient_data['patient_title'])}")

    # Validate patient_meta_description
    meta_len = len(patient_data['patient_meta_description'])
    if meta_len < 100 or meta_len > 155:
        errors.append(f"patient_meta_description must be 100-155 chars, got {meta_len}")

    # Validate content word count
    content_words = count_words(strip_html(patient_data['patient_content']))
    if content_words < 800 or content_words > 1200:
        errors.append(f"patient_content must be 800-1200 words, got {content_words}")

    # Check for Bottom Line section
    if 'patient-summary' not in patient_data['patient_content']:
        errors.append("Missing 'patient-summary' (Bottom Line section)")

    # Check for FAQ section
    if '<h3' not in patient_data['patient_content']:
        errors.append("Missing FAQ section with H3 headers")

    # Check for References section
    if 'article-references' not in patient_data['patient_content']:
        errors.append("Missing article-references section")

    # Check for 'your' or 'you' usage
    content_text = strip_html(patient_data['patient_content']).lower()
    your_count = len(re.findall(r'\byour\b|\byou\b', content_text))
    if your_count < 5:
        errors.append(f"'you/your' appears {your_count} times (need at least 5)")

    # Validate tags
    if not isinstance(patient_data['patient_tags'], list):
        errors.append("patient_tags must be a list")
    elif len(patient_data['patient_tags']) < 5 or len(patient_data['patient_tags']) > 8:
        errors.append(f"patient_tags must have 5-8 items, got {len(patient_data['patient_tags'])}")

    return errors


def process_articles():
    """
    Process all articles from both JSON files.
    """
    print("=" * 80)
    print("DERMOBRAIN PATIENT-FRIENDLY ARTICLE PROCESSOR")
    print("=" * 80)

    articles_data = []

    # Load lasers articles
    print(f"\nLoading {LASERS_FILE}...")
    with open(LASERS_FILE, 'r') as f:
        lasers = json.load(f)
    print(f"  Loaded {len(lasers)} laser articles")

    # Load lifestyle articles
    print(f"Loading {LIFESTYLE_FILE}...")
    with open(LIFESTYLE_FILE, 'r') as f:
        lifestyle = json.load(f)
    print(f"  Loaded {len(lifestyle)} lifestyle articles")

    total_articles = len(lasers) + len(lifestyle)
    print(f"\nTotal articles to process: {total_articles}")

    # Prepare data with file tracking
    for idx, article in enumerate(lasers):
        article['_source_file'] = 'lasers'
        article['_index'] = idx
        articles_data.append(article)

    for idx, article in enumerate(lifestyle):
        article['_source_file'] = 'lifestyle'
        article['_index'] = idx
        articles_data.append(article)

    # Backup original files
    print("\nCreating backups...")
    import shutil
    shutil.copy(LASERS_FILE, BACKUP_DIR / "articles_lasers.json.backup")
    shutil.copy(LIFESTYLE_FILE, BACKUP_DIR / "articles_lifestyle.json.backup")
    print(f"  Backups created in {BACKUP_DIR}/")

    # Process each article
    print(f"\nProcessing {total_articles} articles...")
    print("-" * 80)

    processed_lasers = []
    processed_lifestyle = []
    errors_by_article = {}

    for article_num, article in enumerate(articles_data, 1):
        source_file = article['_source_file']
        index = article['_index']
        title = article.get('title', 'Untitled')
        category = article.get('category', 'unknown')

        print(f"\n[{article_num}/{total_articles}] Processing: {title[:60]}...")
        print(f"  Source: {source_file} | Index: {index}")

        # Generate patient content
        patient_data = generate_patient_version(
            title,
            article.get('content', ''),
            category
        )

        if not patient_data:
            print(f"  ERROR: Failed to generate patient content")
            errors_by_article[article_num] = ["Failed to generate content from API"]
            continue

        # Validate patient content
        validation_errors = validate_patient_content(patient_data, category)

        if validation_errors:
            print(f"  VALIDATION ERRORS ({len(validation_errors)}):")
            for error in validation_errors:
                print(f"    - {error}")
            errors_by_article[article_num] = validation_errors
            continue

        # Add patient fields to article (don't modify existing fields)
        article['patient_title'] = patient_data['patient_title']
        article['patient_meta_description'] = patient_data['patient_meta_description']
        article['patient_content'] = patient_data['patient_content']
        article['patient_tags'] = patient_data['patient_tags']

        # Remove tracking fields before saving
        del article['_source_file']
        del article['_index']

        # Store in appropriate list
        if source_file == 'lasers':
            processed_lasers.append(article)
        else:
            processed_lifestyle.append(article)

        # Print success summary
        content_words = count_words(strip_html(patient_data['patient_content']))
        print(f"  ✓ SUCCESS")
        print(f"    - Title: {patient_data['patient_title'][:50]}...")
        print(f"    - Content: {content_words} words")
        print(f"    - Meta: {len(patient_data['patient_meta_description'])} chars")
        print(f"    - Tags: {len(patient_data['patient_tags'])} items")

    # Save processed articles
    print("\n" + "=" * 80)
    print("SAVING PROCESSED ARTICLES")
    print("=" * 80)

    print(f"\nSaving {len(processed_lasers)} laser articles to {LASERS_FILE}...")
    with open(LASERS_FILE, 'w') as f:
        json.dump(processed_lasers, f, indent=2)
    print(f"  ✓ Saved {len(processed_lasers)} articles")

    print(f"\nSaving {len(processed_lifestyle)} lifestyle articles to {LIFESTYLE_FILE}...")
    with open(LIFESTYLE_FILE, 'w') as f:
        json.dump(processed_lifestyle, f, indent=2)
    print(f"  ✓ Saved {len(processed_lifestyle)} articles")

    # Print summary
    print("\n" + "=" * 80)
    print("PROCESSING SUMMARY")
    print("=" * 80)

    total_processed = len(processed_lasers) + len(processed_lifestyle)
    total_errors = len(errors_by_article)

    print(f"\nTotal Processed: {total_processed}/{total_articles}")
    print(f"  - Laser articles: {len(processed_lasers)}/63")
    print(f"  - Lifestyle articles: {len(processed_lifestyle)}/42")
    print(f"\nErrors: {total_errors}")

    if errors_by_article:
        print("\nArticles with errors:")
        for article_num, errors in sorted(errors_by_article.items()):
            print(f"  Article {article_num}:")
            for error in errors:
                print(f"    - {error}")

    # Return success if all processed
    success = total_processed == total_articles
    print("\n" + "=" * 80)
    if success:
        print("✓ ALL ARTICLES PROCESSED SUCCESSFULLY!")
    else:
        print(f"⚠ {total_articles - total_processed} articles did not process successfully")
    print("=" * 80)

    return success, total_processed, total_articles


if __name__ == "__main__":
    try:
        success, processed, total = process_articles()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
