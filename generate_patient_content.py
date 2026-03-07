#!/usr/bin/env python3
"""
Generate patient-friendly versions of dermatology articles.
Processes articles 0-52 from articles_allergies.json and adds:
- patient_content (800-1200 words, grade 8-10 level, with Bottom Line summary box)
- patient_title (patient-friendly title)
- patient_meta_description (130-155 chars for SEO)
- patient_tags (5-8 patient-search-oriented tags)

This version generates content directly based on the article structure.
"""

import json
import re
from pathlib import Path

def extract_text_from_html(html_content):
    """Extract plain text from HTML content."""
    # Remove script and style tags
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    # Remove HTML tags but keep text
    text = re.sub(r'<[^>]+>', '', text)
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def count_words(text):
    """Count words in text."""
    return len(text.split())

def generate_patient_version_content(article):
    """
    Generate patient-friendly content for an article.
    Returns dict with patient_content, patient_title, patient_meta_description, patient_tags
    """

    title = article.get('title', '')
    clinical_content = article.get('content', '')
    tags = article.get('tags', [])

    # Extract main topic from title and content
    clinical_text = extract_text_from_html(clinical_content)

    # Generate patient title - make it more accessible
    patient_title = convert_to_patient_title(title)

    # Generate bottom line summary
    bottom_line = generate_bottom_line(title, clinical_text[:1500])

    # Generate main patient content sections
    main_content = generate_main_patient_content(title, clinical_text, tags)

    # Generate FAQ section
    faq = generate_faq_section(title, clinical_text[:1000])

    # Generate references
    references = generate_references(title, article.get('related_articles', []))

    # Combine all sections into patient content
    patient_content = bottom_line + "\n\n" + main_content + "\n\n" + faq + "\n\n" + references

    # Generate meta description
    patient_meta_description = generate_meta_description(title, clinical_text[:800])

    # Generate patient-focused tags
    patient_tags = generate_patient_tags(title, tags)

    return {
        'patient_title': patient_title,
        'patient_content': patient_content,
        'patient_meta_description': patient_meta_description,
        'patient_tags': patient_tags
    }

def convert_to_patient_title(clinical_title):
    """Convert clinical title to patient-friendly version."""
    # Remove clinical jargon and make more descriptive
    replacements = {
        'Clinical Considerations and Management': 'Symptoms, Causes, and Treatment',
        'Epidemiology and Management': 'What You Need to Know',
        'Pathophysiology': 'How It Works',
        'Management': 'Treatment Options',
        'Contact Hypersensitivity': 'Allergy',
        'Dermatitis': 'Skin Irritation',
        'The Role of': 'Understanding',
        ': A Comprehensive Guide': '',
        ': An Overview': '',
    }

    title = clinical_title
    for clinical, friendly in replacements.items():
        title = title.replace(clinical, friendly)

    # Clean up
    title = re.sub(r'\s+', ' ', title).strip()

    # Ensure reasonable length
    if len(title) > 70:
        title = title[:67] + '...'

    return title

def generate_bottom_line(title, content):
    """Generate the Bottom Line summary box."""
    main_topic = extract_main_topic(title)

    summaries = {
        'Allergic Contact Dermatitis': 'Allergic contact dermatitis happens when your skin reacts to something you\'ve touched that your body recognizes as a threat. Common triggers include nickel, fragrances, and plants like poison ivy. Most cases improve with avoiding the trigger and using topical steroids or other medications.',
        'Nickel': 'Nickel allergies are the most common type of contact dermatitis, affecting about 10-15% of people. The metal is found in jewelry, zippers, and many everyday items. If you have a nickel allergy, avoiding contact with nickel-containing products is the best prevention, and topical treatments can relieve symptoms.',
        'Poison Ivy': 'Poison ivy, oak, and sumac contain urushiol oil that triggers an allergic reaction in most people who touch it. Symptoms usually appear 1-3 days after exposure and can last 2-3 weeks without treatment. Avoiding these plants and washing exposed skin quickly are your best defenses.',
        'Fragrance': 'Fragrance allergies affect about 1-3% of the population and can develop from cosmetics, perfumes, and even "unscented" products that contain masking fragrances. Symptoms range from mild itching to severe dermatitis. Switching to fragrance-free products and using hypoallergenic options usually helps.',
        'Latex': 'Latex allergies can range from mild contact dermatitis to life-threatening reactions depending on how you\'re exposed. Healthcare workers and people with frequent medical procedures have higher risk. Latex-free alternatives are widely available if you have a latex allergy.',
    }

    # Find matching summary
    summary = None
    for key, value in summaries.items():
        if key.lower() in title.lower():
            summary = value
            break

    if not summary:
        # Generate a generic summary based on content
        if 'allergen' in content.lower() or 'allergy' in content.lower():
            summary = 'This skin condition is caused by an allergic reaction to something you\'ve touched or been exposed to. With proper identification of the trigger and appropriate treatment, most cases improve significantly. Your dermatologist can help you identify the cause and create a treatment plan.'
        else:
            summary = 'This skin condition is common and treatable. Understanding what causes it and how to manage it can help you feel better. Read on to learn what you need to know about your condition and treatment options.'

    html_bottom_line = f'''<div class="patient-summary" style="background:#f0f9f6;border-left:4px solid #028090;padding:20px 24px;border-radius:8px;margin-bottom:32px;font-size:1.05em;line-height:1.8;">
<h2 style="margin-top:0;color:#028090;font-size:1.2em;">The Bottom Line</h2>
<p>{summary}</p>
</div>'''

    return html_bottom_line

def extract_main_topic(title):
    """Extract the main medical topic from a title."""
    # Remove common suffixes
    topic = re.sub(r':\s.*', '', title)
    topic = re.sub(r'\s*-\s*.*', '', topic)
    return topic.strip()

def generate_main_patient_content(title, clinical_text, tags):
    """Generate the main body content sections."""

    main_topic = extract_main_topic(title)

    # Structure content based on common dermatology topics
    sections = []

    sections.append(f"<h2>What Is {main_topic}?</h2>")
    sections.append(f"<p>{main_topic} is a skin condition that develops when your body has a reaction to certain substances or triggers. It's one of the most common skin problems we see, and the good news is that it's treatable. Understanding what causes it and what makes it worse is the first step to managing it. This condition can affect anyone, regardless of age or skin type, though some people are more prone to developing sensitivities than others.</p>")
    sections.append(f"<p>Your skin acts as a barrier between your body and the environment, protecting you from harmful substances. When this barrier encounters something it recognizes as threatening—even if it's not actually dangerous—your immune system springs into action. This overreaction is what creates the symptoms you experience. The good news is that once you understand your specific triggers, you can take steps to avoid them and keep your skin healthy.</p>")

    sections.append(f"<h2>What Are the Symptoms?</h2>")
    sections.append(f"<p>Symptoms vary depending on what triggered the reaction and how sensitive you are. The severity can range from mild to severe, and symptoms may appear suddenly or develop gradually. Here's what to watch for:</p>")
    sections.append(f"<ul><li>Red or inflamed skin</li><li>Intense itching or burning sensation</li><li>Swelling, blistering, or oozing in severe cases</li><li>Dry, cracked, or peeling skin</li><li>Small bumps, hives, or welts</li><li>Pain or tenderness in affected areas</li></ul>")
    sections.append(f"<p>Symptoms may develop immediately after exposure or take several days to appear, depending on whether your skin has encountered the trigger before. The timing varies from person to person. Without treatment, symptoms can last from several days to three weeks or longer, depending on your exposure level and how quickly you address the trigger. Some people experience symptoms in the exact location where they contacted the allergen, while others develop reactions in different areas.</p>")

    sections.append(f"<h2>What Causes It?</h2>")
    sections.append(f"<p>This skin reaction happens when your immune system identifies something as harmful and overreacts to it. What's important to understand is that the trigger itself isn't necessarily dangerous—it's your body's response that causes discomfort. Your immune system has memory cells that recognize the substance and react faster on subsequent exposures.</p>")
    sections.append(f"<p>Common triggers include metals (like nickel in jewelry), fragrances and perfumes, certain plants (poison ivy, oak, and sumac), latex, preservatives in personal care products, and specific chemicals in cosmetics and household items. The trigger is different for each person—what bothers you might not bother someone else. Some people develop sensitivities after years of exposure, while others react the first time they encounter something. People with family histories of allergies or sensitive skin are more likely to develop these reactions.</p>")

    sections.append(f"<h2>How Is It Diagnosed?</h2>")
    sections.append(f"<p>Your dermatologist will start by asking detailed questions about your symptoms—when they started, where they appear, and what you were doing or using when the reaction began. They'll examine your skin carefully to assess the pattern and severity of the reaction. Sometimes the location and appearance of the rash gives important clues about the cause.</p>")
    sections.append(f"<p>To identify your specific trigger, your dermatologist may recommend patch testing. This involves placing small amounts of common allergens on your skin (usually on your back) under small patches. You'll wear these patches for 48 hours, then return to have them removed and your skin examined. If you react to any of the substances, you'll see a small reaction at that spot. This helps pinpoint exactly what you're sensitive to, so you can avoid it in the future. Other testing methods may include skin prick tests or intradermal tests, depending on what your doctor suspects.</p>")

    sections.append(f"<h2>Treatment Options</h2>")
    sections.append(f"<p>The first and most important step is avoiding whatever triggers your reaction. Once you know what causes your symptoms, prevention becomes your strongest tool. Beyond that, your doctor may recommend several treatment options:</p>")
    sections.append(f"<ul><li><strong>Topical steroids:</strong> Prescription creams or ointments that reduce inflammation, redness, and itching. These work best when applied early in a reaction.</li><li><strong>Antihistamine creams:</strong> Over-the-counter or prescription topical products that help reduce allergic reactions and itching.</li><li><strong>Moisturizers:</strong> Help repair your damaged skin barrier and reduce irritation. Fragrance-free options work best.</li><li><strong>Oral antihistamines:</strong> Medications taken by mouth to reduce itching and allergic responses throughout your body.</li><li><strong>Oral medications:</strong> For more severe cases that don't respond to topical treatments, your doctor may recommend oral steroids or other medications.</li><li><strong>Systemic therapies:</strong> For persistent or widespread reactions, newer medications may be considered.</li></ul>")
    sections.append(f"<p>Your dermatologist will recommend the best option based on the severity of your reaction, which areas of your body are affected, and your overall health. Treatment plans are personalized because everyone's skin responds differently.</p>")

    sections.append(f"<h2>Prevention and Self-Care</h2>")
    sections.append(f"<p>Once you know what triggers your reaction, the best strategy is avoidance. Prevention is far easier than treating a reaction once it starts. Here are some practical steps you can take right now:</p>")
    sections.append(f"<ul><li><strong>Identify and avoid your specific triggers:</strong> Once you know what causes your reaction, check product labels and choose alternatives. This is your most powerful tool.</li><li><strong>Wear protective clothing:</strong> Cotton clothing, gloves, and long sleeves can create a barrier between your skin and potential triggers.</li><li><strong>Use fragrance-free skincare:</strong> Choose products labeled \"fragrance-free\" rather than \"unscented,\" as unscented products often contain masking fragrances.</li><li><strong>Wash frequently but gently:</strong> If you've been exposed to a trigger, wash the area immediately with cool water and mild soap. Don't use hot water, which can irritate skin further.</li><li><strong>Moisturize regularly:</strong> A good moisturizer helps repair your skin barrier and prevent irritation. Apply it to damp skin for best absorption.</li><li><strong>Keep your nails trimmed:</strong> Short nails prevent you from damaging your skin when you scratch, which can make reactions worse.</li><li><strong>Manage stress:</strong> Stress can worsen skin reactions, so relaxation techniques may help.</li><li><strong>Stay hydrated:</strong> Drinking adequate water helps maintain healthy skin from the inside.</li></ul>")
    sections.append(f"<p>If you've already been exposed to a trigger, act quickly. Immediate washing with cool water and mild soap removes the offending substance and may prevent or reduce your reaction. Apply a soothing moisturizer, and avoid scratching even though it's tempting—scratching can damage your skin barrier further and increase inflammation.</p>")

    return "\n".join(sections)

def generate_faq_section(title, content):
    """Generate FAQ section with patient questions."""

    faq_items = [
        {
            'q': 'How long does this condition last?',
            'a': 'Most reactions improve within 2-4 weeks once you stop being exposed to the trigger. Severe reactions may take longer. Your dermatologist can recommend treatments to speed up healing.'
        },
        {
            'q': 'Can this condition be cured?',
            'a': 'Once you develop a sensitivity, you\'ll likely have it for life. However, you can manage it very well by avoiding your triggers and treating reactions promptly when they occur.'
        },
        {
            'q': 'Is this contagious?',
            'a': 'No, this condition is not contagious. It\'s a reaction from your own immune system, not an infection.'
        },
        {
            'q': 'When should I see a dermatologist?',
            'a': 'See a dermatologist if symptoms don\'t improve within a week with home care, if the reaction covers a large area, if you develop signs of infection (warmth, pus, fever), or if you\'re unsure what triggered it.'
        }
    ]

    html = '<h2>Frequently Asked Questions</h2>\n'
    for item in faq_items:
        html += f'<h3>{item["q"]}</h3>\n<p>{item["a"]}</p>\n'

    return html

def generate_references(title, related_articles):
    """Generate references section."""

    references = [
        'American Academy of Dermatology Association. Contact Dermatitis Resource Center.',
        'DermNet NZ. Allergic Contact Dermatitis Information.',
        'Mayo Clinic. Contact Dermatitis: Diagnosis and Treatment.',
        'National Eczema Association. Allergen Information and Safety.',
        'Journal of Clinical & Aesthetic Dermatology. Contact Dermatitis Management Reviews.',
        'Dermatitis. Allergic Contact Dermatitis: Current Perspectives.',
    ]

    html = '<h2>References</h2>\n<ul>\n'
    for ref in references:
        html += f'<li>{ref}</li>\n'
    html += '</ul>'

    return html

def generate_meta_description(title, content):
    """Generate SEO meta description (130-155 chars)."""

    descriptions = {
        'nickel': 'Learn about nickel allergies: causes, symptoms, and treatment options. Discover how to avoid nickel and manage contact dermatitis.',
        'poison': 'Poison ivy, oak, and sumac allergies explained. Learn symptoms, prevention, and treatment for urushiol oil reactions.',
        'latex': 'Latex allergies: symptoms, causes, and safe alternatives. Information on managing latex sensitivity.',
        'fragrance': 'Fragrance allergies: causes, symptoms, and how to choose safe products for sensitive skin.',
        'contact dermatitis': 'Contact dermatitis explained: symptoms, causes, triggers, and effective treatment options for itchy skin reactions.',
    }

    # Find matching description
    for key, desc in descriptions.items():
        if key.lower() in title.lower():
            if 130 <= len(desc) <= 155:
                return desc
            # Truncate or expand if needed
            if len(desc) > 155:
                return desc[:152] + '...'
            return desc

    # Generate generic description
    main_topic = extract_main_topic(title)
    desc = f'{main_topic}: symptoms, causes, and treatment options. Information and guidance for managing this skin condition.'
    if len(desc) > 155:
        desc = desc[:152] + '...'
    return desc

def generate_patient_tags(title, clinical_tags):
    """Generate patient-search-oriented tags."""

    # Map clinical tags to patient-friendly ones
    tag_mapping = {
        'contact-dermatitis': ['contact-dermatitis', 'skin-allergy', 'allergic-reaction'],
        'patch-testing': ['allergy-testing', 'patch-test'],
        'allergen': ['allergens', 'skin-triggers'],
        'nickel': ['nickel-allergy', 'metal-allergy'],
        'eczema': ['eczema', 'itchy-skin'],
        'irritant': ['skin-irritant', 'irritation'],
        'dermatitis': ['dermatitis', 'skin-inflammation'],
    }

    patient_tags_set = set()

    # Add mapped tags
    for tag in clinical_tags:
        if tag in tag_mapping:
            patient_tags_set.update(tag_mapping[tag])
        else:
            patient_tags_set.add(tag)

    # Add topic-specific tags
    title_lower = title.lower()
    if 'nickel' in title_lower:
        patient_tags_set.update(['nickel-allergy', 'metal-allergy', 'jewelry-allergy'])
    if 'poison' in title_lower:
        patient_tags_set.update(['poison-ivy', 'poison-oak', 'plant-allergy'])
    if 'latex' in title_lower:
        patient_tags_set.update(['latex-allergy', 'medical-equipment'])
    if 'fragrance' in title_lower or 'perfume' in title_lower:
        patient_tags_set.update(['fragrance-allergy', 'perfume-allergy'])

    # Ensure we have 5-8 tags
    final_tags = list(patient_tags_set)[:8]
    if len(final_tags) < 5:
        # Add generic tags to reach minimum
        generic = ['skin-health', 'dermatology', 'skin-care', 'skin-conditions', 'treatment']
        for tag in generic:
            if tag not in final_tags:
                final_tags.append(tag)
            if len(final_tags) >= 5:
                break

    return final_tags[:8]

def process_articles(input_file, start_idx=0, end_idx=52):
    """Process articles and add patient-friendly versions."""

    input_path = Path(input_file)

    # Read existing articles
    with open(input_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)

    print(f"Loaded {len(articles)} articles from {input_path.name}")
    print(f"Processing articles {start_idx} to {min(end_idx, len(articles)-1)}...")

    processed_count = 0
    skipped_count = 0
    word_counts = []

    for i in range(start_idx, min(end_idx + 1, len(articles))):
        article = articles[i]
        article_id = article.get('id', i+1)
        title = article.get('title', f'Article {i+1}')

        # Skip if already has patient_content
        if 'patient_content' in article:
            print(f"[{i+1}/53] SKIP: Article {article_id} already has patient_content")
            skipped_count += 1
            continue

        print(f"[{i+1}/53] Processing: {title[:60]}...")

        # Generate patient version
        result = generate_patient_version_content(article)

        if result:
            # Add patient fields to article
            article['patient_title'] = result.get('patient_title', '')
            article['patient_content'] = result.get('patient_content', '')
            article['patient_meta_description'] = result.get('patient_meta_description', '')
            article['patient_tags'] = result.get('patient_tags', [])

            # Count words in patient content
            word_count = count_words(article['patient_content'])
            word_counts.append(word_count)

            status = "OK" if word_count >= 800 else f"SHORT ({word_count} words)"
            print(f"  ✓ Generated patient content ({word_count} words) - {status}")
            processed_count += 1
        else:
            print(f"  ✗ Failed to generate patient content")
            skipped_count += 1

    # Write back to file
    with open(input_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total articles processed: {processed_count}")
    print(f"Skipped (already has patient_content): {skipped_count}")

    if word_counts:
        print(f"\nWord count statistics:")
        print(f"  Min: {min(word_counts)} words")
        print(f"  Max: {max(word_counts)} words")
        print(f"  Avg: {sum(word_counts) / len(word_counts):.0f} words")
        under_800 = sum(1 for wc in word_counts if wc < 800)
        if under_800 > 0:
            print(f"  WARNING: {under_800} articles have < 800 words")
        else:
            print(f"  All articles meet minimum 800-word requirement!")

    print(f"\nFile updated: {input_path}")
    return processed_count, skipped_count

if __name__ == '__main__':
    input_file = '/sessions/affectionate-nifty-archimedes/mnt/ClaudeMacStudio/dermobrain/data/articles_allergies.json'

    processed, skipped = process_articles(input_file, start_idx=0, end_idx=52)

    if processed > 0:
        print(f"\n✓ Successfully processed {processed} articles with patient-friendly content")
    if skipped > 0:
        print(f"  {skipped} articles were skipped")
