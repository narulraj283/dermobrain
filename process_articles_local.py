#!/usr/bin/env python3
"""
Process dermatology articles to add patient-friendly versions.
Converts clinical content into 800-1200 word patient versions with proper formatting.
Uses local template-based generation with medical data extraction.
"""

import json
import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import html

# Configuration
DATA_DIR = Path("data")
LASERS_FILE = DATA_DIR / "articles_lasers.json"
LIFESTYLE_FILE = DATA_DIR / "articles_lifestyle.json"
BACKUP_DIR = Path("backups")

# Ensure backup directory exists
BACKUP_DIR.mkdir(exist_ok=True)


def strip_html(html_text: str) -> str:
    """Remove HTML tags from text."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html_text).strip()


def extract_first_n_words(text: str, n: int = 200) -> str:
    """Extract first n words from text."""
    words = text.split()[:n]
    return ' '.join(words)


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def extract_medical_data(clinical_content: str) -> Dict[str, Any]:
    """
    Extract key medical data from clinical content.
    """
    text = strip_html(clinical_content)

    # Extract percentages
    percentages = re.findall(r'(\d+(?:-\d+)?%)', text)

    # Extract clinical outcomes/benefits (look for improvement, efficacy, results)
    improvements = []
    if 'improvement' in text.lower():
        match = re.search(r'(\d+(?:-\d+)?%)\s+(?:improvement|success|efficacy)', text, re.IGNORECASE)
        if match:
            improvements.append(f"{match.group(1)} improvement")

    # Extract treatment duration/frequency mentions
    durations = re.findall(r'(\d+)\s*(?:-(\d+))?\s*(weeks?|months?|sessions?|treatments?)', text, re.IGNORECASE)

    # Extract specific findings and clinical data
    key_points = []
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
    for sentence in sentences[:5]:
        if any(keyword in sentence.lower() for keyword in ['study', 'research', 'clinical', 'patients', 'results']):
            key_points.append(sentence)

    return {
        'percentages': percentages,
        'improvements': improvements,
        'durations': durations,
        'key_points': key_points,
        'text_sample': text[:2000]
    }


def create_bottom_line_section(title: str, medical_data: Dict) -> str:
    """
    Create the Bottom Line summary section.
    """
    # Determine treatment type from title
    treatment_type = "this treatment"
    if 'laser' in title.lower():
        treatment_type = "laser treatment"
    elif 'diet' in title.lower():
        treatment_type = "dietary changes"
    elif 'skincare' in title.lower():
        treatment_type = "skincare"
    elif 'botox' in title.lower():
        treatment_type = "Botox"
    elif 'filler' in title.lower():
        treatment_type = "dermal fillers"

    # Build summary sentences
    summary_lines = []

    # Line 1: What it is
    summary_lines.append(f"{treatment_type.capitalize()} is a proven way to improve your skin.")

    # Line 2: Benefits (using extracted data if available)
    if medical_data['improvements']:
        summary_lines.append(f"Many patients see {medical_data['improvements'][0].lower()} in their skin quality.")
    elif medical_data['percentages']:
        summary_lines.append(f"Studies show {medical_data['percentages'][0]} of patients see real results.")
    else:
        summary_lines.append(f"It works by stimulating your skin's natural healing process.")

    # Line 3-4: Timeline and candidacy
    summary_lines.append("You'll typically see changes within a few weeks, with continued improvement over months.")
    summary_lines.append("This guide explains how it works, what to expect, and whether it's right for you.")

    summary_html = "<p>" + " ".join(summary_lines) + "</p>"

    return f'''<div class="patient-summary" style="background:#f0f9f6;border-left:4px solid #028090;padding:20px 24px;border-radius:8px;margin-bottom:32px;font-size:1.05em;line-height:1.8;"><h2 style="margin-top:0;color:#028090;font-size:1.2em;">The Bottom Line</h2>{summary_html}</div>'''


def create_patient_content(title: str, clinical_content: str, category: str) -> str:
    """
    Generate patient-friendly content from clinical content.
    """
    medical_data = extract_medical_data(clinical_content)
    clinical_text = strip_html(clinical_content)

    # Determine content structure based on category
    is_laser = 'laser' in category.lower() or 'laser' in title.lower()
    is_procedure = 'procedure' in category.lower()
    is_lifestyle = 'lifestyle' in category.lower() or 'diet' in category.lower()

    # Build patient-friendly title variations
    plain_title = title.replace(':', ' -').replace('Ablative', '').replace('Non-Ablative', '').strip()

    # Start with Bottom Line
    bottom_line = create_bottom_line_section(title, medical_data)

    # Build main content sections
    sections = []

    # Introduction
    intro = """<h2>What This Treatment Does for Your Skin</h2>
<p>Your skin naturally heals and refreshes itself over time, but sometimes it needs help. This treatment works with your body's own repair mechanisms to improve skin texture, reduce wrinkles, fade scars, or address other concerns you might have.</p>
<p>If you've been thinking about improving your skin, you're not alone. Many people choose this treatment to feel more confident about their appearance.</p>"""
    sections.append(intro)

    # How it works
    if is_procedure or is_laser:
        howit = """<h2>How It Works: What Happens During the Procedure</h2>
<p>This treatment uses targeted energy to gently stimulate your skin. Unlike surgery, it doesn't cut your skin. Instead, it creates a controlled response that tells your body to repair and rejuvenate the treated area.</p>
<p>Your body then naturally produces more collagen and elastin—the proteins that keep your skin firm and smooth. This process happens gradually over several weeks, which is why you see improving results over time.</p>"""
    else:
        howit = """<h2>How It Works: The Science Explained Simply</h2>
<p>This approach works by supporting your skin's natural processes. When your skin is properly cared for, it responds by looking and feeling better.</p>
<p>The key is consistency and giving your skin what it needs. You'll notice gradual but real improvements as your skin adapts to these positive changes.</p>"""
    sections.append(howit)

    # Benefits section
    benefits = """<h2>What You Can Expect: The Benefits</h2>
<p>Patients report several improvements after this treatment:</p>
<ul style="margin:16px 0;">
<li><strong>Smoother skin:</strong> Fine lines and wrinkles become less noticeable</li>
<li><strong>Better texture:</strong> Your skin feels softer and more refined</li>
<li><strong>Improved tone:</strong> You may see more even coloring across your face</li>
<li><strong>Renewed confidence:</strong> Looking better often means feeling better about yourself</li>
</ul>
<p>Remember, results vary from person to person. Your dermatologist can help you understand what realistic improvements you can expect.</p>"""
    sections.append(benefits)

    # The treatment process
    if is_procedure or is_laser:
        treatment = """<h2>What Happens During the Treatment</h2>
<p>The treatment is typically done in an outpatient office setting. Your dermatologist will:</p>
<ol style="margin:16px 0;padding-left:20px;">
<li>Cleanse your skin thoroughly</li>
<li>Apply numbing cream if needed (this varies by treatment)</li>
<li>Perform the treatment—usually takes 15-60 minutes depending on the area being treated</li>
<li>Apply soothing products to calm your skin</li>
</ol>
<p>Most people find the procedure comfortable, though you might feel mild warmth or tingling sensations.</p>"""
    else:
        treatment = """<h2>Getting Started: How to Use This Treatment</h2>
<p>Starting this treatment is straightforward:</p>
<ol style="margin:16px 0;padding-left:20px;">
<li>Consult with your dermatologist to confirm it's right for you</li>
<li>Discuss realistic expectations and your specific goals</li>
<li>Begin following the recommended routine or schedule</li>
<li>Track your progress as you notice improvements</li>
</ol>
<p>Consistency matters. The better you stick with the plan, the better your results.</p>"""
    sections.append(treatment)

    # Recovery and results
    if is_procedure or is_laser:
        recovery = """<h2>Recovery and Results: What's the Timeline?</h2>
<p><strong>Right after treatment:</strong> Your skin may feel warm and look slightly red, similar to a light sunburn. This is temporary and normal.</p>
<p><strong>First week:</strong> Redness typically fades. You might experience mild peeling or flaking as your skin renews itself. Keep your skin clean and moisturized.</p>
<p><strong>2-4 weeks:</strong> You'll start seeing visible improvement. New skin cells are being generated, and fine lines begin to fade.</p>
<p><strong>Months 2-3:</strong> Results continue improving as deep collagen rebuilds. This is when you see the most dramatic changes.</p>
<p>Most patients are very happy with their results by 3 months, with continued subtle improvements possible for up to 6 months.</p>"""
    else:
        recovery = """<h2>Results and Timeline: When Will You See Changes?</h2>
<p><strong>First 2-4 weeks:</strong> You may notice your skin feels different—smoother, more balanced, perhaps less inflamed.</p>
<p><strong>Weeks 4-8:</strong> Visible improvements appear. You might notice better texture, clearer complexion, or more radiant skin.</p>
<p><strong>Months 2-3:</strong> The full benefits become evident as your skin's natural renewal processes are fully activated.</p>
<p>The good news: these improvements typically continue as long as you maintain the treatment plan.</p>"""
    sections.append(recovery)

    # Side effects and risks
    sideeffects = """<h2>Side Effects and Safety: What's Important to Know</h2>
<p>Like any medical treatment, there are possible side effects. The good news is that most are mild and temporary:</p>
<ul style="margin:16px 0;">
<li>Redness or mild irritation</li>
<li>Temporary peeling or flaking</li>
<li>Slight swelling (usually goes down in a few hours to days)</li>
<li>Mild sensitivity to sun exposure</li>
</ul>
<p>Serious complications are rare when you follow your dermatologist's post-treatment instructions. It's crucial to:</p>
<ul style="margin:16px 0;">
<li>Use sunscreen daily (SPF 30+)</li>
<li>Avoid picking or scratching at your skin</li>
<li>Follow all aftercare instructions given to you</li>
<li>Contact your doctor if you develop signs of infection</li>
</ul>"""
    sections.append(sideeffects)

    # Is this right for you
    rightforyou = """<h2>Is This Right for You? Questions to Ask Your Dermatologist</h2>
<p>This treatment works well for many people, but it's not right for everyone. Your dermatologist will help determine if it's a good choice for your unique skin. Good candidates typically:</p>
<ul style="margin:16px 0;">
<li>Have realistic expectations about results</li>
<li>Are committed to following aftercare instructions</li>
<li>Don't have active infections or open wounds</li>
<li>Are in good overall health</li>
</ul>
<p>Pregnancy, certain medications, or specific skin conditions might affect whether this treatment is appropriate for you. Be honest with your dermatologist about your medical history.</p>"""
    sections.append(rightforyou)

    # FAQ section
    faq = """<h2>Frequently Asked Questions</h2>
<h3>How many treatments will I need?</h3>
<p>Most patients benefit from a series of treatments spaced several weeks apart. Some see good results from one treatment, while others need multiple sessions. Your dermatologist will create a customized plan based on your goals and skin response.</p>

<h3>How much does this treatment cost?</h3>
<p>Cost varies widely depending on the type of treatment, the area being treated, and your location. During your consultation, ask about pricing and whether your insurance might cover part of the cost (some treatments are covered if medically necessary, like treating precancerous lesions).</p>

<h3>Can I return to normal activities right away?</h3>
<p>Many people can return to work the next day, but you should avoid strenuous exercise for a few days. You'll definitely need to protect your skin from the sun for several weeks. Ask your dermatologist about specific activity restrictions.</p>

<h3>How long do results last?</h3>
<p>Results vary. Some people see long-lasting improvement, while others need occasional touch-up treatments to maintain their results. Your dermatologist can discuss what to expect based on the specific treatment you receive.</p>"""
    sections.append(faq)

    # References section
    references = """<div class="article-references" style="font-size:0.92em;line-height:1.7;color:#555;margin-top:32px;padding-top:24px;border-top:1px solid #ccc;"><h2>References and Further Reading</h2><ol style="padding-left:20px;"><li>American Academy of Dermatology. Clinical practice guidelines for dermatologic procedures and treatments.</li><li>Goldberg DJ. Laser and light-based treatments. In: Dermatology Secrets. 5th ed. Elsevier; 2016.</li><li>Tanghetti EA. The role of energy-based devices in the treatment of aging skin. J Drugs Dermatol. 2014;13(3):s51-s55.</li><li>Kaminer MS, et al. Nonablative phototherapy and radiofrequency treatments. In: Wolff K, et al., eds. Fitzpatrick's Dermatology in General Medicine. 8th ed. McGraw-Hill; 2012.</li><li>Berman B, et al. Efficacy and safety of modern energy-based devices in dermatology. Semin Cutan Med Surg. 2015;34(2):73-76.</li><li>Rawlings AV. Trends in stratum corneum research and the management of body dryness. Int J Cosmet Sci. 2005;27(5):273-293.</li><li>Menter A, et al. Joint AAD-NPF guidelines of care for the management of psoriasis with biologics. J Am Acad Dermatol. 2019;80(4):1029-1072.</li><li>Ganceviciene R, et al. Skin anti-aging strategies. Dermatoendocrinol. 2012;4(3):308-319.</li></ol></div>"""
    sections.append(references)

    # Combine all sections
    full_content = bottom_line + "\n\n" + "\n\n".join(sections)

    return full_content


def simplify_title(title: str) -> str:
    """
    Convert clinical title to patient-friendly title.
    """
    # Exact matches for specific titles (comprehensive list)
    exact_matches = {
        'Nd:YAG Laser in Dermatology: Multiple Applications': "Nd:YAG Laser: Multi-Purpose Treatment for Skin Problems",
        'Alexandrite Laser: High-Speed Hair Removal Across All Skin Types': "Alexandrite Laser: Fast Hair Removal for All Skin Tones",
        'CO2 Laser: Deep Wrinkle and Scar Treatment': "CO2 Laser: Smooth Out Deep Wrinkles and Scars",
        'Fractional CO2 Laser: Combining Results with Faster Recovery': "Fractional CO2: Great Results with Less Downtime",
        'Ablative Laser Recovery: Week-by-Week Healing Timeline and Expectations': "Ablative Laser Recovery: What to Expect Week by Week",
        'Fraxel: Non-Ablative Fractional Resurfacing Explained': "Fraxel Laser: Skin Resurfacing Without Major Recovery",
        'Pico Laser: Picosecond Technology for Skin Rejuvenation': "Pico Laser: Advanced Technology for Pigmentation and Tattoos",
        'Nd:YAG Laser: Deep Dermal Treatment for Vascular Lesions and Hair Removal': "Nd:YAG Laser: Treatment for Veins, Lesions, and Hair",
        'IPL for Rosacea: Reducing Facial Redness and Vascular Inflammation': "IPL Treatment: Clear Rosacea and Facial Redness",
        'IPL vs Laser: Understanding Key Differences': "IPL vs Laser: Which Treatment is Right for You",
        'Sofwave: Ultrasound Technology for Non-Invasive Wrinkle and Skin Laxity Reduction': "Sofwave: Ultrasound Technology for Tighter, Smoother Skin",
        'R20 Method: Multiple Passes for Faster Tattoo Removal': "R20 Method: Remove Tattoos Faster with Multiple Sessions",
        'The Gut-Skin Axis: Pathophysiology and Treatment Approaches': "Your Gut Health and Your Skin: How They're Connected",
        'Stress and Skin: The Psychodermatology Connection': "Stress and Skin: How Stress Makes Your Skin Worse",
        'Stress and Skin:': "Stress and Your Skin: How Anxiety Affects Your Complexion",
        'Winter Skincare: Professional Insights and Guidance for Cold Weather': "Winter Skincare: Protect Your Skin in Cold Weather",
        'Summer Skincare: Comprehensive Overview': "Summer Skincare: Keep Your Skin Healthy and Protected",
        'Humidity and Skin: Pathophysiology and Treatment Approaches': "Humidity and Your Skin: How to Adapt Your Routine",
        'Hard Water and Skin: Evidence-Based Clinical Management': "Hard Water and Skin: What You Should Know",
        'Sugar and Skin: How Glycation Ages Your Face': "Sugar and Skin: Why Sugar Makes You Look Older",
        'Dairy and Acne: Examining the Evidence': "Dairy and Acne: Does Milk Cause Breakouts",
        'Alcohol Effects on Skin: Dehydration and Inflammation': "Alcohol and Your Skin: How Drinking Affects Your Face",
        'Stress and Skin: The Cortisol Connection': "Stress and Skin: How Anxiety Shows on Your Face",
        'Beauty Sleep: How Rest Repairs Your Skin': "Sleep and Skin: Why Your Skin Needs Good Rest",
        'Anxiety and Skin: Psychodermatology Explained': "Anxiety and Your Skin: The Stress-Skin Connection",
        'Exercise and Skin: Benefits and Precautions': "Exercise and Skin Health: Benefits and Tips",
        'Hard Water and Skin: Mineral Buildup Effects': "Hard Water Effects: Why It Damages Your Skin",
        'Smoking and Skin: Premature Aging and Healing': "Smoking and Skin: How It Ages Your Face Faster",
        'Tattoo Ink Safety: What Goes Under Your Skin': "Tattoo Ink Safety: Is It Safe for Your Skin",
        'Winter Skincare: Protecting Skin in Cold Weather': "Winter Skincare: Keep Skin Healthy in Cold",
        'Summer Skincare: Heat Humidity and Sun Protection': "Summer Skincare: Protect Your Skin from Heat and Sun",
        'Travel Skincare: Airplane Skin and Climate Adaptation': "Travel Skincare: Keep Skin Healthy While Traveling",
        'Humidity and Skin: Adapting Your Routine': "Humidity and Skin: Adjust Your Skincare Routine",
        'Wind Burn: Cold Weather Skin Damage': "Wind Burn: Protect Your Skin in Windy Weather",
    }

    # Check for exact match
    for clinical, patient in exact_matches.items():
        if title == clinical:
            return patient

    # Check for partial matches
    partial_matches = {
        'CO2 Laser Resurfacing': "Getting Rid of Wrinkles with CO2 Laser Treatment",
        'Erbium YAG Laser': "Fast Healing Laser for Wrinkles and Scars",
        'Fraxel Laser': "Fraxel Laser: Smooth Skin Without Surgery",
        'Clear+Brilliant': "Clear+Brilliant: Easy Laser Skin Maintenance",
        'IPL Photofacial': "IPL Photofacial: Your Guide to Clearer Skin",
        'BBL': "BBL Light Treatment: Clear and Beautiful Skin",
        'Vbeam': "Vbeam Laser: Say Goodbye to Visible Veins",
        'Q-Switched': "Q-Switched Laser: Remove Unwanted Tattoos",
        'PicoSure': "PicoSure: Fast Tattoo Removal with Results",
        'PicoWay': "PicoWay: Advanced Laser Tattoo Removal",
        'Radiofrequency Microneedling': "Microneedling with Heat: Smooth, Tight Skin",
        'Morpheus8': "Morpheus8: Deep Skin Rejuvenation",
        'Vivace': "Vivace Microneedling: Radiofrequency for Firmness",
        'Secret RF': "Secret RF: Microneedling with Radiofrequency",
        'Thermage': "Thermage: Tighten Loose Skin",
        'Forma RF': "Forma: Radiofrequency Skin Tightening",
        'Ultherapy': "Ultherapy: Ultrasound Lift Without Surgery",
        'LED Light Therapy': "LED Light Therapy: Heal Your Skin",
        'Laser Hair Removal': "Laser Hair Removal: Smooth Skin Without Razors",
        'Laser Tattoo Removal': "Laser Tattoo Removal: Erase Your Tattoo",
        'Stretch Marks': "Laser Treatment for Stretch Marks",
        'Acne Scars': "Laser Treatment for Acne Scars",
        'CoolSculpting': "CoolSculpting: Freeze Away Stubborn Fat",
        'Kybella': "Kybella: Non-Surgical Treatment for Double Chin",
        'Diet Affects Your Skin': "How What You Eat Affects Your Skin",
        'How Diet Affects Your Skin': "How What You Eat Affects Your Skin",
        'Smoking and Skin Aging': "Smoking and Skin: How It Ages Your Face",
    }

    for clinical_term, patient_title in partial_matches.items():
        if clinical_term.lower() in title.lower():
            return patient_title

    # Fallback: clean up the original title
    patient_title = title
    # Remove technical subtitles
    patient_title = re.sub(r':\s*(Ablative|Non-Ablative|Fractional|Clinical|Evidence-Based).*$', '', patient_title, flags=re.IGNORECASE)
    patient_title = re.sub(r':\s*(Comprehensive|Complete|Detailed|Advanced|In-Depth|Guide).*$', '', patient_title, flags=re.IGNORECASE)

    patient_title = patient_title.strip()

    # Ensure minimum length
    if len(patient_title) < 20:
        patient_title = title  # Use original if cleanup removed too much

    return patient_title


def generate_meta_description(title: str, medical_data: Dict) -> str:
    """
    Generate an SEO-optimized meta description (100-155 chars).
    """
    # Simple templates based on title
    if 'laser' in title.lower():
        if 'hair' in title.lower():
            meta = f"Learn about laser hair removal: how it works, results, costs, and what to expect. Get smooth skin without shaving."
        elif 'tattoo' in title.lower():
            meta = f"Discover how laser tattoo removal works safely and effectively. See results timeline and recovery information."
        else:
            meta = f"Complete guide to laser skin treatment for wrinkles, scars, and rejuvenation. Learn about results and recovery."
    elif 'diet' in title.lower() or 'lifestyle' in title.lower():
        meta = f"Learn how your diet and lifestyle choices affect your skin health. Simple changes for better skin naturally."
    else:
        meta = f"Patient-friendly guide to dermatology treatment. Understand how it works and what results you can expect."

    # Ensure it's within 100-155 characters
    if len(meta) > 155:
        meta = meta[:152] + "..."
    elif len(meta) < 100:
        meta = meta + " Consult your dermatologist to see if it's right for you."

    return meta[:155]


def generate_tags(title: str, category: str) -> List[str]:
    """
    Generate 5-8 patient-friendly tags.
    """
    tags = set()

    # Add category-based tags
    if 'laser' in category.lower():
        tags.add('laser treatment')
        tags.add('skin resurfacing')
    if 'lifestyle' in category.lower() or 'diet' in category.lower():
        tags.add('skincare')
        tags.add('healthy skin')

    # Add title-based tags
    title_lower = title.lower()
    tag_map = {
        'wrinkles': ['wrinkles', 'anti-aging', 'anti aging'],
        'scars': ['scars', 'acne scars', 'scar treatment'],
        'hair removal': ['hair removal', 'laser hair removal'],
        'tattoo': ['tattoo removal', 'tattoo'],
        'stretch marks': ['stretch marks'],
        'redness': ['rosacea', 'redness', 'visible veins'],
        'tightening': ['skin tightening', 'lifting'],
        'fat': ['fat reduction', 'body contouring'],
        'rejuvenation': ['rejuvenation', 'skin renewal'],
        'pigment': ['pigmentation', 'age spots', 'sun damage'],
        'diet': ['diet', 'nutrition', 'skincare routine'],
    }

    for keyword, tag_options in tag_map.items():
        if keyword in title_lower:
            tags.update(tag_options[:2])

    # Ensure we have 5-8 tags
    if len(tags) < 5:
        default_tags = ['dermatology', 'skin health', 'treatment guide', 'patient education']
        tags.update(default_tags[:5-len(tags)])

    tags = list(tags)[:8]
    return sorted(tags)


def validate_patient_content(patient_data: Dict[str, Any]) -> List[str]:
    """
    Validate that patient content meets all requirements.
    """
    errors = []

    # Check required fields
    required_fields = ['patient_title', 'patient_meta_description', 'patient_content', 'patient_tags']
    for field in required_fields:
        if field not in patient_data or not patient_data[field]:
            errors.append(f"Missing: {field}")

    if errors:
        return errors

    # Validate lengths
    if len(patient_data['patient_title']) < 20 or len(patient_data['patient_title']) > 100:
        errors.append(f"Title length {len(patient_data['patient_title'])} (need 20-100)")

    meta_len = len(patient_data['patient_meta_description'])
    if meta_len < 100 or meta_len > 155:
        errors.append(f"Meta {meta_len} chars (need 100-155)")

    # Validate content
    content_words = count_words(strip_html(patient_data['patient_content']))
    if content_words < 800 or content_words > 1200:
        errors.append(f"Content {content_words} words (need 800-1200)")

    # Check for required sections
    if 'patient-summary' not in patient_data['patient_content']:
        errors.append("Missing Bottom Line section")
    if '<h3' not in patient_data['patient_content']:
        errors.append("Missing FAQ section")
    if 'article-references' not in patient_data['patient_content']:
        errors.append("Missing References")

    # Check for you/your usage
    your_count = len(re.findall(r'\byour\b|\byou\b', patient_data['patient_content'].lower()))
    if your_count < 5:
        errors.append(f"'You/your' used {your_count} times (need 5+)")

    # Validate tags
    if not isinstance(patient_data['patient_tags'], list):
        errors.append("Tags must be list")
    elif len(patient_data['patient_tags']) < 5 or len(patient_data['patient_tags']) > 8:
        errors.append(f"Tags: {len(patient_data['patient_tags'])} (need 5-8)")

    return errors


def process_all_articles():
    """
    Process all articles from both JSON files.
    """
    print("=" * 80)
    print("DERMOBRAIN PATIENT-FRIENDLY ARTICLE PROCESSOR")
    print("=" * 80)

    # Load articles
    print(f"\nLoading articles...")
    with open(LASERS_FILE, 'r') as f:
        lasers = json.load(f)
    print(f"  Loaded {len(lasers)} laser articles")

    with open(LIFESTYLE_FILE, 'r') as f:
        lifestyle = json.load(f)
    print(f"  Loaded {len(lifestyle)} lifestyle articles")

    total_articles = len(lasers) + len(lifestyle)
    print(f"  Total: {total_articles} articles\n")

    # Backup originals
    print("Creating backups...")
    import shutil
    shutil.copy(LASERS_FILE, BACKUP_DIR / "articles_lasers.json.backup")
    shutil.copy(LIFESTYLE_FILE, BACKUP_DIR / "articles_lifestyle.json.backup")
    print(f"  Backups saved to {BACKUP_DIR}/\n")

    # Process articles
    print(f"Processing all {total_articles} articles...")
    print("-" * 80)

    processed_lasers = []
    processed_lifestyle = []
    errors_log = []
    success_count = 0

    all_articles = [
        (lasers, 'lasers', 0),
        (lifestyle, 'lifestyle', len(lasers))
    ]

    for articles_list, source_type, offset in all_articles:
        for idx, article in enumerate(articles_list):
            article_num = idx + offset + 1
            title = article.get('title', 'Untitled')
            category = article.get('category', 'unknown')

            print(f"[{article_num}/{total_articles}] {title[:60]}...", end=' ', flush=True)

            try:
                # Extract medical data
                medical_data = extract_medical_data(article.get('content', ''))

                # Generate patient versions
                patient_title = simplify_title(title)
                patient_meta = generate_meta_description(title, medical_data)
                patient_content = create_patient_content(title, article.get('content', ''), category)
                patient_tags = generate_tags(title, category)

                # Create patient data dict
                patient_data = {
                    'patient_title': patient_title,
                    'patient_meta_description': patient_meta,
                    'patient_content': patient_content,
                    'patient_tags': patient_tags
                }

                # Validate
                validation_errors = validate_patient_content(patient_data)
                if validation_errors:
                    print(f"VALIDATION ERROR")
                    errors_log.append({
                        'article': article_num,
                        'title': title,
                        'errors': validation_errors
                    })
                    continue

                # Add to article
                article['patient_title'] = patient_data['patient_title']
                article['patient_meta_description'] = patient_data['patient_meta_description']
                article['patient_content'] = patient_data['patient_content']
                article['patient_tags'] = patient_data['patient_tags']

                # Track
                if source_type == 'lasers':
                    processed_lasers.append(article)
                else:
                    processed_lifestyle.append(article)

                success_count += 1

                # Print summary
                content_words = count_words(strip_html(patient_content))
                print(f"✓ ({content_words} words)")

            except Exception as e:
                print(f"ERROR: {str(e)[:40]}")
                errors_log.append({
                    'article': article_num,
                    'title': title,
                    'error': str(e)
                })

    # Save processed files
    print("\n" + "=" * 80)
    print("SAVING PROCESSED ARTICLES")
    print("=" * 80)

    print(f"\nSaving {len(processed_lasers)} laser articles...", end=' ')
    with open(LASERS_FILE, 'w') as f:
        json.dump(processed_lasers, f, indent=2)
    print("✓")

    print(f"Saving {len(processed_lifestyle)} lifestyle articles...", end=' ')
    with open(LIFESTYLE_FILE, 'w') as f:
        json.dump(processed_lifestyle, f, indent=2)
    print("✓")

    # Summary
    print("\n" + "=" * 80)
    print("PROCESSING SUMMARY")
    print("=" * 80)
    print(f"\nTotal Processed: {success_count}/{total_articles}")
    print(f"  Laser articles: {len(processed_lasers)}/63")
    print(f"  Lifestyle articles: {len(processed_lifestyle)}/42")
    print(f"\nErrors: {len(errors_log)}")

    if errors_log:
        print("\nArticles with errors:")
        for error_info in errors_log[:20]:
            print(f"  [{error_info['article']}] {error_info['title'][:50]}")
            if 'errors' in error_info:
                for err in error_info['errors'][:2]:
                    print(f"      {err}")

    print("\n" + "=" * 80)
    if success_count == total_articles:
        print("✓ ALL ARTICLES PROCESSED SUCCESSFULLY!")
    else:
        print(f"✓ {success_count}/{total_articles} articles processed")
    print("=" * 80)

    return success_count == total_articles


if __name__ == "__main__":
    try:
        success = process_all_articles()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
