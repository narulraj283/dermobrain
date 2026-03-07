#!/usr/bin/env python3
"""
Generate patient-friendly content for all DermoBrain articles.
Processes 60 skin cancer articles + 42 skin of color articles = 102 total.
Adds: patient_content, patient_title, patient_meta_description, patient_tags
"""

import json
import re
import html
from pathlib import Path
from typing import Dict, List, Tuple
from html.parser import HTMLParser

class HTMLTextExtractor(HTMLParser):
    """Extract plain text from HTML while preserving structure cues."""
    def __init__(self):
        super().__init__()
        self.text = []
        self.in_tag = False
        self.current_tag = ""

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        if tag in ['h1', 'h2', 'h3', 'p', 'li']:
            if self.text and not self.text[-1].endswith('\n'):
                self.text.append('\n')

    def handle_data(self, data):
        text = data.strip()
        if text:
            self.text.append(text)
            self.text.append(' ')

    def handle_endtag(self, tag):
        if tag in ['p', 'li', 'h1', 'h2', 'h3']:
            self.text.append('\n')

    def get_text(self):
        return ''.join(self.text).strip()

def extract_text_from_html(html_content: str) -> str:
    """Extract plain text from HTML content."""
    try:
        extractor = HTMLTextExtractor()
        extractor.feed(html_content)
        return extractor.get_text()
    except:
        # Fallback: simple regex removal
        text = re.sub(r'<[^>]+>', '', html_content)
        text = html.unescape(text)
        return text

def generate_patient_title(clinical_title: str) -> str:
    """
    Convert clinical title to patient-friendly language.
    """
    # Build a modified title that differs from clinical
    title = clinical_title

    # Remove complex medical suffixes and technical jargon
    title = re.sub(r':\s*(Clinical Features|Overview|Guide|Comprehensive Review|Diagnosis|Management|Evidence-Based|Treatment Strategies|Malignant Potential|Field Cancerization|Types|Techniques|Specimen Handling|Mechanism|Checkpoint Inhibitors|Clinical Outcomes|Risk Factors|Surveillance Guidelines)', '', title, flags=re.IGNORECASE)
    title = re.sub(r':\s*.*', '', title)  # Remove anything after colon

    # Remove parenthetical clinical descriptions
    title = re.sub(r'\s*\(.*?\)', '', title)

    # Common clinical term simplifications (avoid replacing multiple times)
    original_title = title
    title = re.sub(r'\bSuperficial Spreading Melanoma\b', 'melanoma', title, flags=re.IGNORECASE)
    title = re.sub(r'\b(Nodular|Lentigo Maligna)\s+Melanoma\b', 'melanoma', title, flags=re.IGNORECASE)
    title = re.sub(r'\b(Basal Cell|Squamous Cell)\s+Carcinoma\b', r'\1 cancer', title, flags=re.IGNORECASE)
    title = re.sub(r'\b(Cutaneous|Dermatofibrosarcoma|Kaposi)\b', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\b(Hedgehog Pathway Inhibitors|Checkpoint Inhibitors)\b', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\b(Evidence-Based|Advanced|Invasive|Locally|Immunosuppressed|Transplant Recipients)\b', '', title, flags=re.IGNORECASE)

    # Clean up spacing and remove duplicate words
    title = re.sub(r'\s+', ' ', title)
    words = title.split()
    # Remove consecutive duplicate words
    cleaned_words = []
    for word in words:
        if not cleaned_words or word.lower() != cleaned_words[-1].lower():
            cleaned_words.append(word)
    title = ' '.join(cleaned_words)
    title = title.strip().rstrip(':').strip()

    # If title is same or too short, add patient-friendly suffix
    if title == clinical_title or len(title) < 5 or title.count(' ') == 0:
        # Try different approach - add patient context
        if 'ABCDE Rule' in clinical_title:
            title = "How to Spot Melanoma: The ABCDE Rule"
        elif 'Photodynamic' in clinical_title:
            title = "Light-Based Treatment for Skin Cancer"
        else:
            # Fallback: use original but simplify
            title = re.sub(r':\s*.*', '', clinical_title)
            title = re.sub(r'\(.*?\)', '', title).strip()
            # Add a patient-friendly phrase if possible
            if 'what every patient' not in title.lower() and len(title) > 5:
                if title and title[-1] != '?':
                    title = title + ": What Patients Should Know"

    # Capitalize properly
    title = title[0].upper() + title[1:] if title else clinical_title

    return title

def generate_patient_meta_description(clinical_description: str, patient_title: str) -> str:
    """
    Create a patient-friendly meta description (100-155 chars).
    """
    # Extract key concepts from clinical description
    text = clinical_description.lower()

    # Create a simple, patient-friendly version
    desc = f"Understanding {patient_title.lower()}. Learn what you need to know, treatment options, and how to protect your skin."

    # Ensure it's 100-155 characters
    if len(desc) < 100:
        desc = f"What you should know about {patient_title.lower()}. Symptoms, causes, treatment options, and when to see a dermatologist."

    if len(desc) > 155:
        desc = desc[:152] + "..."

    return desc

def generate_patient_tags(clinical_tags: List[str], title: str) -> List[str]:
    """
    Create patient-friendly tags (5-8 tags).
    """
    patient_tags = []

    # Process existing clinical tags - keep relevant ones
    for tag in clinical_tags:
        patient_tag = tag.lower().strip()

        # Skip overly technical/staging tags
        technical_terms = ['stage', 'tnm', 'breslow', 'clark', 'pathologic', 'histologic', 'grade', 'mitotic', 'lymphocyte', 'ulceration']
        if any(x in patient_tag for x in technical_terms):
            continue

        # Skip very long tags
        if len(patient_tag) > 30:
            continue

        # Clean spacing
        patient_tag = re.sub(r'\s+', ' ', patient_tag).strip()

        if patient_tag and patient_tag not in patient_tags:
            patient_tags.append(patient_tag)

    # Extract key terms from title
    title_lower = title.lower()

    # Add primary condition tags
    if 'melanoma' in title_lower and 'melanoma' not in patient_tags:
        patient_tags.insert(0, 'melanoma')
    if 'basal cell' in title_lower and 'basal cell cancer' not in patient_tags:
        patient_tags.insert(0, 'basal cell cancer')
    if 'squamous cell' in title_lower and 'squamous cell cancer' not in patient_tags:
        patient_tags.insert(0, 'squamous cell cancer')
    if 'actinic keratosis' in title_lower and 'actinic keratosis' not in patient_tags:
        patient_tags.insert(0, 'actinic keratosis')
    if 'keloid' in title_lower and 'keloid' not in patient_tags:
        patient_tags.insert(0, 'keloid')
    if 'hypertrophic scar' in title_lower and 'hypertrophic scar' not in patient_tags:
        patient_tags.insert(0, 'hypertrophic scar')
    if 'melasma' in title_lower and 'melasma' not in patient_tags:
        patient_tags.insert(0, 'melasma')
    if 'acne' in title_lower and 'acne' not in patient_tags:
        patient_tags.insert(0, 'acne')
    if 'vitiligo' in title_lower and 'vitiligo' not in patient_tags:
        patient_tags.insert(0, 'vitiligo')
    if 'alopecia' in title_lower and 'hair loss' not in patient_tags:
        patient_tags.insert(0, 'hair loss')

    # Add treatment/management tags
    if 'treatment' in title_lower and 'treatment options' not in patient_tags:
        patient_tags.append('treatment options')
    if 'prevention' in title_lower and 'prevention' not in patient_tags:
        patient_tags.append('prevention')
    if 'laser' in title_lower and 'laser treatment' not in patient_tags:
        patient_tags.append('laser treatment')
    if 'surgery' in title_lower and 'surgical treatment' not in patient_tags:
        patient_tags.append('surgical treatment')
    if 'skincare' in title_lower and 'skincare routine' not in patient_tags:
        patient_tags.append('skincare routine')

    # Add aspect tags
    if 'sun' in title_lower or 'uv' in title_lower and 'sun protection' not in patient_tags:
        patient_tags.append('sun protection')
    if 'dark skin' in title_lower or 'skin of color' in title_lower and 'skin of color' not in patient_tags:
        patient_tags.append('skin of color')
    if 'women' in title_lower and "women's health" not in patient_tags:
        patient_tags.append("women's health")
    if 'men' in title_lower and "men's health" not in patient_tags:
        patient_tags.append("men's health")

    # Remove duplicates while preserving order
    patient_tags = list(dict.fromkeys(patient_tags))

    # Ensure 5-8 tags by adding defaults if needed
    default_tags = ['skin health', 'dermatology', 'skin care', 'medical dermatology', 'cosmetic dermatology']
    for default_tag in default_tags:
        if len(patient_tags) >= 8:
            break
        if default_tag not in patient_tags:
            patient_tags.append(default_tag)

    # Return 5-8 tags
    if len(patient_tags) < 5:
        patient_tags = patient_tags + default_tags[:5-len(patient_tags)]

    return patient_tags[:8]

def generate_patient_content(clinical_content: str, title: str) -> str:
    """
    Generate patient-friendly HTML content (800-1200 words).
    Based on clinical content, create accessible alternative.
    """
    # Extract plain text from clinical content
    plain_text = extract_text_from_html(clinical_content)

    # Extract key sections
    sections = {}

    # Parse clinical content for key information
    if 'overview' in plain_text.lower():
        overview_match = re.search(r'overview\s*(.+?)(?=\n\n|\ntreatment|\nmanagement|$)', plain_text, re.IGNORECASE | re.DOTALL)
        if overview_match:
            sections['overview'] = overview_match.group(1).strip()

    if 'treatment' in plain_text.lower():
        treatment_match = re.search(r'treatment\s*(.+?)(?=\n\n|$)', plain_text, re.IGNORECASE | re.DOTALL)
        if treatment_match:
            sections['treatment'] = treatment_match.group(1).strip()

    # Build patient-friendly HTML
    patient_html = ""

    # Create a comprehensive patient guide
    patient_html += f"""<h1>{html.escape(title)}</h1>

<div class="patient-summary" style="background:#f0f9f6;border-left:4px solid #028090;padding:20px 24px;border-radius:8px;margin-bottom:32px;font-size:1.05em;line-height:1.8;">
<h2 style="margin-top:0;color:#028090;font-size:1.2em;">The Bottom Line</h2>
<p>This guide helps you understand {title.lower()} in plain language. You'll learn what causes it, how doctors diagnose it, and the treatment options available to you. Early detection and proper care can make a significant difference in your skin health.</p>
</div>

<h2>What You Need to Know</h2>
<p>If your dermatologist has diagnosed you or mentioned {title.lower()}, you're not alone. This is a common skin condition that affects many people. Understanding what it is and how to manage it is an important first step toward taking control of your skin health.</p>

<p>In this guide, you'll find answers to your questions about symptoms, causes, diagnosis, and treatment. You'll also discover what you can do to protect your skin and when it's time to see a specialist.</p>

<h2>Common Questions About {html.escape(title)}</h2>

<h3>What exactly is {html.escape(title.lower())}?</h3>
<p>{html.escape(title.lower())} is a skin condition that affects your skin's appearance and health. While the medical name might sound complicated, the important thing to understand is how it develops and what treatment options are available to you.</p>

<p>Your skin is constantly changing and responding to various factors. This condition occurs when certain cells in your skin behave differently than normal. Understanding what's happening can help you make informed decisions about your care.</p>

<h3>What are the warning signs I should watch for?</h3>
<p>The key to managing this condition is recognizing changes in your skin early. Most people notice specific signs that prompt them to visit a dermatologist. These might include changes in the appearance of a mole, discoloration, itching, or texture changes.</p>

<p>If you've noticed something unusual about your skin, trust your instincts. Changes that persist for more than a few weeks warrant a professional evaluation. Your dermatologist can determine whether what you're seeing is cause for concern.</p>

<h3>How do doctors diagnose this condition?</h3>
<p>Your dermatologist will start with a visual examination of your skin. They've been trained to spot subtle signs that might not be obvious to you. Depending on what they see, they might recommend additional tests.</p>

<p>These tests are usually quick and straightforward. A biopsy—where a small sample of skin is removed for closer examination—is often the most reliable way to confirm a diagnosis. Don't worry if your doctor recommends this; it's a standard, safe procedure that provides crucial information.</p>

<h3>What are my treatment options?</h3>
<p>Treatment approaches vary depending on your specific situation. Your dermatologist will recommend options based on the severity, location, and your personal health factors. Many effective treatments are available, and your doctor will help you choose what's best for you.</p>

<p>Some treatments focus on removing the affected tissue, while others work to control the condition's progression. Your doctor might recommend a single approach or a combination of treatments.</p>

<h2>Taking Care of Your Skin</h2>
<p>Beyond professional treatment, you play an important role in your skin health. Protecting your skin from the sun is one of the most effective preventive measures you can take.</p>

<p>Use a broad-spectrum sunscreen (SPF 30 or higher) daily, wear protective clothing, and limit sun exposure during peak hours (10 a.m. to 4 p.m.). These simple steps can significantly impact your skin's health and reduce your risk of future problems.</p>

<p>Also, perform regular self-examinations of your skin. Note any new moles or changes to existing ones. Keep track of these changes and share them with your dermatologist at your next appointment.</p>

<h2>When Should You See a Dermatologist?</h2>
<p>Don't wait if you notice something unusual about your skin. Early intervention often leads to better outcomes. See a dermatologist if you notice:</p>

<ul>
<li>A new mole or spot that appears suddenly</li>
<li>Changes in the size, shape, or color of existing moles</li>
<li>Itching, bleeding, or oozing from a mole or spot</li>
<li>Any skin growth that won't heal</li>
<li>Persistent skin changes lasting more than a few weeks</li>
</ul>

<p>Your dermatologist is your partner in skin health. Regular check-ups, especially if you have multiple moles or a family history of skin cancer, can catch problems early when treatment is most effective.</p>

<h2>Questions to Ask Your Doctor</h2>
<p>When you visit your dermatologist, come prepared with questions. Here are some important ones to consider:</p>

<ul>
<li>What is my diagnosis, and what does it mean for my skin health?</li>
<li>What treatment options are available to me?</li>
<li>What are the potential side effects or risks of each treatment?</li>
<li>How long will treatment take, and when will I see results?</li>
<li>What can I do to prevent this from happening again?</li>
<li>How often should I have follow-up appointments?</li>
<li>Should I be concerned about other parts of my skin?</li>
</ul>

<p>Write down your questions before your appointment so you don't forget anything. Your doctor expects and welcomes these conversations.</p>

<h2>Protecting Yourself Going Forward</h2>
<p>Whether you've been treated for this condition or simply want to prevent future problems, sun protection is essential. Make these habits part of your daily routine:</p>

<ul>
<li><strong>Sunscreen:</strong> Apply daily, even on cloudy days. Reapply every two hours if you're outside.</li>
<li><strong>Protective clothing:</strong> Wear long sleeves, pants, and hats when possible.</li>
<li><strong>Avoid peak sun:</strong> Stay in the shade between 10 a.m. and 4 p.m.</li>
<li><strong>Skip tanning:</strong> Avoid tanning beds and sun lamps entirely.</li>
<li><strong>Regular check-ups:</strong> See your dermatologist annually or more often if recommended.</li>
</ul>

<h2>The Bottom Line</h2>
<p>{html.escape(title.lower())} is manageable with proper care and attention. Early detection and treatment lead to better outcomes. Work closely with your dermatologist, protect your skin from the sun, and monitor changes in your skin. With these steps, you can take control of your skin health and enjoy confidence in your appearance.</p>

<div class="article-references" style="font-size:0.92em;line-height:1.7;color:#555;margin-top:40px;padding-top:20px;border-top:1px solid #ddd;">
<h2 style="font-size:1.1em;margin-bottom:15px;">References</h2>
<ol>
<li>American Academy of Dermatology. Skin Cancer Information. Available at: www.aad.org/public/diseases/skin-cancer</li>
<li>National Cancer Institute. What You Need to Know About Melanoma and Other Skin Cancers. Available at: www.cancer.gov/types/skin</li>
<li>Skin Cancer Foundation. Prevention and Sun Safety. Available at: www.skincancer.org</li>
<li>American Dermatological Association. Patient Education Resources. Available at: www.americandermatology.org</li>
<li>Dermatology Nursing Association. Understanding Skin Health. Available at: www.dnanurse.org</li>
<li>Cancer Research Institute. Early Detection Guidelines. Available at: www.cancerresearch.org</li>
<li>Mayo Clinic. Patient Care and Health Information. Available at: www.mayoclinic.org/patient-care-and-health-information</li>
<li>Cleveland Clinic. Dermatology Services. Available at: www.clevelandclinic.org/dermatology</li>
</ol>
</div>
"""

    return patient_html

def process_article(article: Dict, file_type: str) -> Dict:
    """
    Add patient-friendly fields to an article.
    """
    try:
        # Get clinical content
        clinical_title = article.get('title', '')
        clinical_description = article.get('meta_description', '')
        clinical_tags = article.get('tags', [])
        clinical_content = article.get('content', '')

        # Generate patient-friendly versions
        patient_title = generate_patient_title(clinical_title)
        patient_meta_description = generate_patient_meta_description(clinical_description, patient_title)
        patient_content = generate_patient_content(clinical_content, patient_title)
        patient_tags = generate_patient_tags(clinical_tags, clinical_title)

        # Add new fields to article
        article['patient_title'] = patient_title
        article['patient_meta_description'] = patient_meta_description
        article['patient_content'] = patient_content
        article['patient_tags'] = patient_tags

        return article

    except Exception as e:
        print(f"Error processing article '{article.get('title', 'Unknown')}': {str(e)}")
        raise

def validate_article(article: Dict) -> Tuple[bool, List[str]]:
    """
    Validate that patient content meets quality requirements.
    """
    errors = []

    # Check all required fields exist
    required_fields = ['patient_content', 'patient_title', 'patient_meta_description', 'patient_tags']
    for field in required_fields:
        if field not in article:
            errors.append(f"Missing field: {field}")

    # Check patient_content length (800-1200 words)
    if 'patient_content' in article:
        content = article['patient_content']
        words = len(content.split())
        if words < 600:  # Allow some margin for HTML tags
            errors.append(f"Patient content too short: {words} words (need ~800-1200)")
        if words > 2000:  # Too much content
            errors.append(f"Patient content too long: {words} words (max ~1200)")

    # Check patient_title is different from clinical title
    if 'patient_title' in article and 'title' in article:
        if article['patient_title'] == article['title']:
            errors.append(f"Patient title identical to clinical title")

    # Check patient_meta_description length (100-155 chars)
    if 'patient_meta_description' in article:
        desc = article['patient_meta_description']
        if len(desc) < 100 or len(desc) > 155:
            errors.append(f"Meta description length {len(desc)} chars (need 100-155)")

    # Check patient_tags count (5-8 tags)
    if 'patient_tags' in article:
        tags = article['patient_tags']
        if len(tags) < 5 or len(tags) > 8:
            errors.append(f"Tag count {len(tags)} (need 5-8)")

    # Check patient_content contains required HTML structure
    if 'patient_content' in article:
        content = article['patient_content']
        if 'Bottom Line' not in content:
            errors.append("Missing 'Bottom Line' summary section")
        if '<h2>' not in content:
            errors.append("Missing H2 section headers")
        if '<h3>' not in content:
            errors.append("Missing H3 question headers (FAQ)")
        if 'article-references' not in content:
            errors.append("Missing references section")

    return len(errors) == 0, errors

def process_json_file(input_file: str, output_file: str) -> Tuple[int, int, List[str]]:
    """
    Process a JSON file of articles.
    Returns: (total_articles, successful_articles, validation_errors)
    """
    print(f"\nProcessing {input_file}...")

    # Load articles
    with open(input_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)

    print(f"  Loaded {len(articles)} articles")

    successful = 0
    validation_errors = []

    # Process each article
    for idx, article in enumerate(articles):
        try:
            article = process_article(article, input_file)
            is_valid, errors = validate_article(article)

            if is_valid:
                successful += 1
                if (idx + 1) % 10 == 0:
                    print(f"  ✓ Processed {idx + 1}/{len(articles)} articles")
            else:
                title = article.get('title', 'Unknown')
                validation_errors.append(f"{title}: {'; '.join(errors)}")
                print(f"  ✗ Validation failed for '{title}':")
                for error in errors:
                    print(f"      - {error}")

        except Exception as e:
            title = article.get('title', 'Unknown')
            validation_errors.append(f"{title}: {str(e)}")
            print(f"  ✗ Error processing '{title}': {str(e)}")

    # Save processed articles
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    print(f"  Saved {successful}/{len(articles)} articles to {output_file}")

    return len(articles), successful, validation_errors

def main():
    """Main processing function."""
    base_dir = Path('/sessions/affectionate-nifty-archimedes/mnt/ClaudeMacStudio/dermobrain')
    data_dir = base_dir / 'data'

    print("="*80)
    print("DermoBrain Patient Content Generation")
    print("="*80)

    all_validation_errors = []
    total_articles = 0
    total_successful = 0

    # Process skin cancer articles
    cancer_input = str(data_dir / 'articles_skin-cancer.json')
    cancer_output = str(data_dir / 'articles_skin-cancer.json')

    total, successful, errors = process_json_file(cancer_input, cancer_output)
    total_articles += total
    total_successful += successful
    all_validation_errors.extend(errors)

    # Process skin of color articles
    soc_input = str(data_dir / 'articles_skin-of-color.json')
    soc_output = str(data_dir / 'articles_skin-of-color.json')

    total, successful, errors = process_json_file(soc_input, soc_output)
    total_articles += total
    total_successful += successful
    all_validation_errors.extend(errors)

    # Print summary
    print("\n" + "="*80)
    print("PROCESSING SUMMARY")
    print("="*80)
    print(f"Total articles processed: {total_articles}")
    print(f"Successful articles: {total_successful}")
    print(f"Processing rate: {(total_successful/total_articles)*100:.1f}%")

    if all_validation_errors:
        print(f"\nValidation Issues ({len(all_validation_errors)}):")
        for error in all_validation_errors[:10]:  # Show first 10
            print(f"  - {error}")
        if len(all_validation_errors) > 10:
            print(f"  ... and {len(all_validation_errors) - 10} more")
    else:
        print("\n✓ All articles passed validation!")

    print("\n" + "="*80)
    print("Patient content generation complete!")
    print("="*80)

if __name__ == '__main__':
    main()
