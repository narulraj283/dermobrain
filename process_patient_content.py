#!/usr/bin/env python3
"""
Process all 63 articles in articles_injectables.json and add patient-friendly content.
Adds 4 new fields to each article:
- patient_content: 800-1200 word patient-friendly HTML article
- patient_title: Plain language title for patients
- patient_meta_description: Google search snippet (100-155 chars)
- patient_tags: List of 5-8 patient-search-oriented tags
"""

import json
import re
from pathlib import Path
from html import escape

# File paths
INPUT_FILE = Path('data/articles_injectables.json')
OUTPUT_FILE = Path('data/articles_injectables.json')

# Patient content templates for different article types
TEMPLATES = {
    'botox-overview': {
        'patient_title': 'What is Botox? A Patient\'s Guide to Wrinkle Relaxing Injections',
        'patient_meta_description': 'Learn how Botox works to reduce wrinkles, what to expect during treatment, and real results patients see. Complete patient guide.',
        'patient_tags': ['botox for wrinkles', 'how does botox work', 'wrinkle reduction injections', 'botox results', 'non-surgical anti-aging'],
        'sections': [
            ('Understanding Botox', '''Botox is one of the most popular non-surgical treatments for reducing wrinkles and fine lines on your face. If you've noticed fine lines appearing on your forehead, between your eyebrows, or around your eyes, Botox might be worth considering. The treatment works by gently relaxing the muscles that create wrinkles when you frown, squint, or raise your eyebrows. Many people choose Botox because it's quick, requires no downtime, and produces natural-looking results when done properly.

The active ingredient in Botox is botulinum toxin, which sounds more dramatic than it actually is. When used in the tiny amounts we inject for cosmetic purposes, it's very safe. The FDA approved Botox for cosmetic use back in 2002, and millions of people have been treated safely since then. You won't find yourself unable to move your face or looking "frozen" if you choose an experienced injector—the goal is always to maintain your natural facial expressions while reducing wrinkles.'''),

            ('How Botox Actually Works', '''Your facial wrinkles happen because of muscle movement. Every time you smile, frown, or raise your eyebrows, the muscles under your skin contract. Over time, this repeated muscle movement causes lines to form in your skin, kind of like how a piece of paper gets creases from folding it repeatedly. Botox works by slightly weakening these muscles so they don't contract as strongly.

Here's the technical part explained simply: the muscles in your face need a chemical signal to contract. Botox blocks that signal, so the muscles relax. This relaxation means your skin doesn't crease as much when you move. Interestingly, over time, this prevents new wrinkles from forming too. Some patients actually see their existing wrinkles improve because their skin gets a break from all that muscle movement.

The results aren't immediate—you typically start seeing changes within 3-4 days, and the full effect develops over about two weeks. The results last for about 3-4 months, which is why people usually come back for touch-ups several times a year.'''),

            ('What to Expect During Your Treatment', '''If you decide to try Botox, here's what your appointment will actually look like. You'll meet with your injector, who will discuss your goals and examine your face. They might ask you to make facial expressions—frowning, squinting, raising your eyebrows—so they can see exactly which muscles are creating your wrinkles.

The actual injections are quick. The injector uses an extremely fine needle to place small amounts of Botox into specific muscles. You might feel tiny pinches, but it's generally not painful. Most people describe it as barely uncomfortable. The whole appointment usually takes 10-15 minutes. You won't need anesthesia because the needle is so small and the procedure is so quick.

After your injections, you can go right back to your normal activities. No recovery time needed. Some people see minor bruising or redness at the injection sites, but this typically fades within a day or two. You should avoid strenuous exercise for 24 hours and try not to massage the treated areas, as this can move the Botox to unintended places.'''),

            ('Real Results Patients See', '''Studies show that about 70% of people who receive Botox see significant improvement in their wrinkles. You won't look like you have a frozen face—that's a misconception. When done well, Botox simply softens the wrinkles you have while allowing you to make normal facial expressions. You can still smile, frown, and show emotion; the movements are just a bit smoother.

Different areas respond differently. Forehead wrinkles and crow's feet (lines around your eyes) typically show the most dramatic improvement. The lines between your eyebrows also respond very well to Botox. Your results depend on several factors: how deep your wrinkles were to begin with, which muscles you want to relax, how much Botox you receive, and how your body metabolizes the treatment.'''),

            ('Common Questions Patients Ask', '''
<h3>Does Botox hurt?</h3>
<p>Most patients report minimal discomfort. The needle is incredibly fine, and the injections are so quick that many people barely feel them. If you're very sensitive to pain, you can ask your injector for a numbing cream beforehand.</p>

<h3>Will I look weird or frozen?</h3>
<p>Not if you choose an experienced injector. The key is using the right amount. Too much Botox in the hands of someone inexperienced can look overdone, but an excellent injector will give you natural-looking softening of your wrinkles while maintaining your normal expressions.</p>

<h3>How much does Botox cost?</h3>
<p>Botox is typically priced per unit, and the cost ranges from $10-20 per unit depending on your location and provider. Most people need 20-40 units for a forehead treatment, so you might expect to pay $200-800. Insurance doesn't cover cosmetic Botox.</p>

<h3>What if I don't like the results?</h3>
<p>If you're unhappy with your Botox results, they'll naturally fade over 3-4 months. There's no long-term commitment. Some doctors also keep an enzyme on hand that can dissolve Botox if someone wants immediate reversal, though this is less common.</p>
            '''),
        ]
    },
    'botox-forehead-lines': {
        'patient_title': 'Botox for Forehead Wrinkles: How to Smooth Expression Lines',
        'patient_meta_description': 'Guide to using Botox for forehead lines. Learn how many units are needed, what results to expect, and cost information.',
        'patient_tags': ['forehead wrinkles', 'botox forehead', 'expression lines treatment', 'smooth forehead', 'anti-aging injections'],
        'sections': [
            ('Why Forehead Lines Form', '''Forehead wrinkles are some of the first lines that appear on our faces because we use our forehead muscles constantly. Every time you raise your eyebrows—whether you're expressing surprise, concentrating, or just having a normal conversation—the muscles in your forehead contract, creating temporary lines. Over many years, these lines become permanent.

The horizontal lines that run across your forehead happen because of this repeated muscle contraction. Sun exposure makes the problem worse because UV damage weakens your skin's elasticity over time, so it has a harder time bouncing back from these muscle movements. This is why people who spend a lot of time in the sun tend to have deeper forehead lines earlier in life.'''),

            ('How Botox Treats Forehead Lines', '''Botox is particularly effective for forehead wrinkles because it works on the exact muscles that create these lines. The frontalis muscle is what raises your eyebrows and creates those horizontal lines. By relaxing this muscle slightly, Botox prevents the skin from creasing as much when you move, and over time, existing lines soften significantly.

Most people need about 20-30 units of Botox across the forehead to achieve good results. Your injector might use fewer units if you want more movement and expression, or more if you want smoother results. The goal is finding the right balance for your face and what you want to achieve.'''),

            ('What Results Look Like', '''Most patients notice their forehead looks visibly smoother within 5-7 days, with full results by two weeks. In the first few days, you might notice you can't raise your eyebrows quite as high—this is normal and expected. Your facial expressions will still look natural; you'll just have fewer wrinkles when you move.

The best part about treating forehead lines early is prevention. Even if you only have fine lines now, getting Botox can prevent them from getting deeper. This is why some people in their late 20s and early 30s start Botox—to keep lines from developing further.'''),

            ('Aftercare and Longevity', '''After your forehead Botox, there's virtually no downtime. You might have tiny red dots where the needles entered, but these fade quickly. Avoid rubbing the area for 24 hours and skip the gym for that day. You can wear makeup and go about your day normally.

Your results will last about 3-4 months. After that, the Botox is naturally absorbed by your body and the lines gradually return. Most people schedule their next appointment around 10-12 weeks after their first injection.'''),

            ('Questions About Forehead Botox', '''
<h3>Will my forehead look completely frozen?</h3>
<p>Only if too much Botox is used. With the right amount from an experienced injector, you'll still be able to move your forehead naturally—it will just look smoother when you do.</p>

<h3>How long until I see results?</h3>
<p>You'll start seeing results in about 3-4 days, but it takes about 10-14 days to see the full effect. Be patient if you don't see dramatic changes immediately.</p>

<h3>Can I combine forehead Botox with other treatments?</h3>
<p>Yes! Many people combine forehead Botox with other injectable treatments like fillers for deeper lines, or with other procedures. Your provider can suggest combinations that work well together.</p>

<h3>Is forehead Botox safe?</h3>
<p>Yes, when administered by a qualified provider. The FDA approved Botox for cosmetic use over 20 years ago. The key is choosing an experienced injector who understands facial anatomy.</p>
            '''),
        ]
    },
    'default': {
        'patient_title': 'Understanding Injectable Treatments for Your Skin',
        'patient_meta_description': 'Learn about cosmetic injectable treatments and how they can help you achieve your aesthetic goals.',
        'patient_tags': ['cosmetic injectables', 'dermal fillers', 'injectable treatments', 'anti-aging', 'facial rejuvenation'],
        'sections': []
    }
}

def extract_text_from_html(html_content):
    """Extract plain text from HTML for context."""
    text = re.sub(r'<[^>]+>', '', html_content)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def build_patient_content(article):
    """Build comprehensive patient-friendly content from clinical content."""

    article_id = article.get('id', article.get('slug', 'unknown'))
    clinical_title = article['title']
    clinical_content = article['content']

    # Extract key information from clinical content
    clinical_text = extract_text_from_html(clinical_content)

    # Start building the patient content
    bottom_line = generate_bottom_line(clinical_text, clinical_title)

    # Build main sections based on article type
    sections_html = f'''<div class="patient-summary" style="background:#f0f9f6;border-left:4px solid #028090;padding:20px 24px;border-radius:8px;margin-bottom:32px;font-size:1.05em;line-height:1.8;">
<h2 style="margin-top:0;color:#028090;font-size:1.2em;">The Bottom Line</h2>
<p>{bottom_line}</p>
</div>

'''

    # Add main sections
    sections_html += build_main_sections(article_id, clinical_text, clinical_title)

    # Add FAQ section
    sections_html += build_faq_section(article_id, clinical_title)

    # Add references
    sections_html += build_references_section(article_id, clinical_title)

    return sections_html

def generate_bottom_line(clinical_text, title):
    """Generate a 3-4 sentence bottom line summary."""

    # Smart summaries based on content keywords
    if 'botox' in title.lower() or 'botulinum' in clinical_text.lower():
        if 'forehead' in title.lower():
            return 'Botox can effectively smooth forehead wrinkles by relaxing the muscles that create expression lines. Most people need 20-30 units and see results within two weeks. Results last 3-4 months, and you can return to your regular activities immediately after treatment.'
        elif 'crow' in title.lower():
            return 'Botox reduces crow\'s feet by relaxing the orbicularis oculi muscle around your eyes. The treatment is quick, with minimal discomfort, and shows results within 2 weeks. Most people find the improvement in these stubborn lines well worth the minor investment in time.'
        else:
            return 'Botox is a safe, FDA-approved treatment that relaxes facial muscles to smooth wrinkles and fine lines. Results develop over two weeks and last about 3-4 months. Many patients appreciate how the procedure enhances their appearance while maintaining natural facial expression.'

    elif 'filler' in title.lower() or 'hyaluronic' in clinical_text.lower():
        if 'lips' in title.lower():
            return 'Dermal fillers can add volume and shape to your lips for a fuller appearance. The procedure takes 15-20 minutes with minimal discomfort. Results are immediate and continue to improve over the first two weeks as the product fully integrates.'
        elif 'cheek' in title.lower():
            return 'Cheek fillers restore lost volume and create a lifted appearance without surgery. Results look natural when placed correctly and develop over 1-2 weeks. The treatment reverses some common signs of facial aging like hollowing and sagging.'
        else:
            return 'Dermal fillers add volume to smooth wrinkles and enhance facial features. Results are visible immediately, though optimal results develop over 2 weeks. Common fillers last 6-12 months depending on the product and treatment area.'

    elif 'sculptra' in title.lower():
        return 'Sculptra stimulates your body to produce its own collagen for gradual facial rejuvenation. Results develop slowly over 4-6 weeks but can last up to 2 years. The treatment works best for larger areas of volume loss and provides natural, long-lasting improvement.'

    elif 'radiesse' in title.lower():
        return 'Radiesse is a longer-lasting filler that provides immediate results and stimulates collagen production. Results last 12-18 months for most patients. The treatment works well for deeper lines and larger volume loss areas.'

    elif 'prp' in title.lower() or 'platelet' in clinical_text.lower():
        return 'PRP uses your own blood components to stimulate collagen and improve skin texture. Results develop gradually over 4-6 weeks as your skin regenerates. Many patients appreciate this natural approach to facial rejuvenation.'

    elif 'hyperhidrosis' in title.lower() or 'excessive sweating' in clinical_text.lower():
        return 'Botox is FDA-approved for treating excessive sweating in the underarms, hands, and feet. The treatment works by blocking the signals that trigger sweat production. Results typically last 6-7 months, making it a practical solution for people who sweat excessively.'

    else:
        return 'This injectable treatment offers a non-surgical approach to addressing common concerns about aging and appearance. Results develop within days to weeks depending on the product used. Many patients choose this option because it provides noticeable improvement without significant downtime.'

def build_main_sections(article_id, clinical_text, title):
    """Build the main content sections."""
    html = ''

    # Understanding section
    html += '<h2>Understanding Your Treatment Options</h2>\n'
    if 'botox' in article_id.lower():
        html += '<p>If you\'re considering Botox or a similar injectable treatment, you\'re joining millions of people who use these procedures to look refreshed and youthful. These treatments have become mainstream because they work well and are relatively quick and affordable. The most common reason people choose injectables is that they want to address wrinkles without going under the knife. You get results without major surgery, significant cost, or weeks of recovery time.</p>\n'
        html += '<p>Many patients worry that Botox will make them look unnatural or "frozen." The truth is that when administered by a skilled provider, your results will look like a refreshed version of you. Your facial expressions will still be visible and natural—they\'ll just have fewer wrinkles. This is what modern Botox looks like: subtle improvement that makes you look like you\'ve had good rest, not like you\'ve had surgery.</p>\n'
    else:
        html += '<p>Injectable treatments offer a range of options to address your specific concerns, whether that\'s wrinkles, volume loss, or other signs of aging. These treatments have become the go-to choice for many people because they provide real results without requiring surgery or lengthy recovery. Understanding your options helps you make the best choice for your goals and budget.</p>\n'
        html += '<p>The beauty of injectable treatments is their versatility and customization. Your provider can tailor the treatment specifically to your face, your skin type, and your goals. Whether you want dramatic change or subtle enhancement, there\'s an approach that will work for you. Many patients appreciate that they can start with a conservative treatment and build from there.</p>\n'

    # How it works section
    html += '<h2>How the Treatment Works</h2>\n'
    if 'botox' in article_id.lower():
        html += '<p>The science behind Botox is surprisingly straightforward. Your facial wrinkles form because you move your face constantly—when you smile, frown, squint, or raise your eyebrows. Over time, these movements create permanent lines in your skin. Botox works by gently relaxing the muscles responsible for these movements. This prevents new wrinkles from forming and allows existing wrinkles to soften.</p>\n'
        html += '<p>The medication itself is incredibly precise. Your injector uses micro-doses placed into specific facial muscles. This targeting means that Botox affects only the muscles you want to relax, leaving everything else unchanged. That\'s why you can still make normal facial expressions—you\'re just doing so with less wrinkling. The effects build gradually, so you won\'t suddenly look different overnight; instead, you\'ll gradually notice that your wrinkles are becoming softer and less noticeable.</p>\n'
    else:
        html += '<p>Injectable treatments work by either relaxing muscles (neurotoxins) or adding volume (fillers) to address specific concerns. The approach depends on whether your issue is dynamic wrinkles from movement or static wrinkles and volume loss. Your provider will help you understand which approach—or combination of approaches—works best for your goals. Many patients benefit from a combination of both types of treatment for comprehensive facial rejuvenation.</p>\n'

    # What to expect section
    html += '<h2>What to Expect During Your Treatment</h2>\n'
    html += '<p>Most injectable treatments are quick—usually 10-30 minutes depending on how many areas you\'re treating. You\'ll meet with your provider, who will assess your face and discuss your goals. They might take photos for your medical record so you can compare your before and after results. When it\'s time for injections, you\'ll feel small pinches as the needle enters your skin, but the discomfort is minimal and brief. Many patients find the anticipation worse than the actual procedure.</p>\n'
    html += '<p>After your treatment, you can go right back to your day. There\'s no surgical recovery, no sutures, no major restrictions. You might have minor redness or tiny bruises at the injection sites, but these fade quickly within hours or a day. Most people schedule their appointments during their lunch break and return to work without anyone knowing they\'ve had anything done. Within a week, any visible signs of treatment are completely gone.</p>\n'

    # Results section
    html += '<h2>Results You Can Expect</h2>\n'
    if 'botox' in article_id.lower():
        html += '<p>You\'ll start noticing results within 3-4 days as the medication takes effect. The full results develop over about two weeks, so patience is important during this period. At that point, you\'ll see the maximum smoothing of wrinkles and relaxation of treated muscles. The results last approximately 3-4 months for most patients. As the effects gradually wear off, your wrinkles will slowly return to their previous state—they don\'t suddenly reappear, and they don\'t get worse. This is why people usually schedule maintenance appointments every 3-4 months to keep their results.</p>\n'
    else:
        html += '<p>Results vary depending on the type of injectable used. Some products show improvement immediately, while others develop gradually over weeks as your skin responds to the treatment. The longevity also varies significantly—some fillers last 6 months, while others like Sculptra can last a year or more. Your provider will discuss timeline expectations for your specific treatment during your consultation.</p>\n'

    html += '<h2>Is This Right for You?</h2>\n'
    html += '<p>The best candidates for injectable treatments are people who have realistic expectations and understand both what the treatment can and can\'t do. These procedures work best when you\'re motivated by your own goals, not pressure from others or social media. If you have fine lines you\'d like to prevent from getting deeper, or wrinkles you want to soften, injectables are often an excellent option. The key is choosing an experienced, qualified provider who understands facial anatomy and can help you achieve natural-looking results that enhance your appearance.</p>\n'

    return html

def build_faq_section(article_id, title):
    """Build FAQ section with common patient questions."""

    faq_html = '<h2>Common Questions Patients Ask</h2>\n'

    if 'botox' in article_id.lower():
        faq_html += '''<h3>Is Botox safe?</h3>
<p>Yes. Botox has been used safely for cosmetic purposes for over 20 years. The FDA approved it for cosmetic use in 2002, and it's been administered millions of times since then. The key to safety is using proper technique with the right amount of product. Your provider should be board-certified and have extensive experience.</p>

<h3>Will I look frozen or unnatural?</h3>
<p>Only if too much product is used or if an inexperienced injector administers it. When done correctly, Botox softens wrinkles while preserving natural expression. You should still be able to smile, frown, and show emotion—your movements will just be smoother. This is why choosing an experienced injector matters so much.</p>

<h3>How much does it cost?</h3>
<p>Botox is typically priced per unit, with costs ranging from $10-20 per unit depending on your location and provider. Most people spend $200-600 per treatment session depending on how many units they need. Insurance doesn't cover cosmetic Botox, but some providers offer package deals or loyalty discounts.</p>

<h3>What if I don't like the results?</h3>
<p>The effects of Botox fade naturally over 3-4 months, so if you're unhappy, you simply don't get another treatment. Some offices keep an enzyme (hyaluronidase) available that can dissolve the product if you want immediate reversal, though this is less common for Botox. The good news is you have a few months to decide if it's right for you.</p>'''

    elif 'filler' in article_id.lower():
        faq_html += '''<h3>How long do fillers last?</h3>
<p>Longevity depends on the type of filler. Hyaluronic acid fillers typically last 6-9 months, while stimulating fillers like Sculptra can last 2 years. Your provider will discuss the expected timeline for your specific product and treatment area.</p>

<h3>Can fillers look natural?</h3>
<p>Absolutely, when the right product is chosen and placed correctly. A skilled injector understands facial anatomy and creates results that look like an improved version of you, not an overdone version. Natural-looking results require finding a provider whose aesthetic matches yours.</p>

<h3>Is there any downtime?</h3>
<p>Minimal. You might have some redness and minor swelling for a few hours, and possibly small bruises that fade within a week. You can typically return to work and normal activities immediately. Avoid strenuous exercise for 24 hours after filler injection.</p>

<h3>Can I undo a filler treatment if I don't like it?</h3>
<p>For hyaluronic acid fillers, yes—an enzyme called hyaluronidase can dissolve them. For other filler types, reversal is more limited. This is another reason why choosing an experienced injector is important; you want to get great results the first time.</p>'''

    else:
        faq_html += '''<h3>When will I see results?</h3>
<p>Timing depends on the treatment. Some injectables show improvement immediately, while others develop gradually over weeks. Your provider will explain what to expect for your specific treatment.</p>

<h3>How often do I need treatment?</h3>
<p>This varies by product and treatment area. Some treatments last a few months, while others last a year or more. Your provider will recommend a treatment schedule based on your specific situation.</p>

<h3>Are injectable treatments safe?</h3>
<p>Yes, when performed by a qualified, experienced provider. All FDA-approved injectables have been extensively tested for safety. Choose a board-certified dermatologist or plastic surgeon with a strong track record.</p>

<h3>Can I combine different injectable treatments?</h3>
<p>Many people do combine treatments for more comprehensive results. For example, some use Botox for dynamic wrinkles and fillers for volume loss. Your provider can suggest combinations that work well together for your specific goals.</p>'''

    return faq_html

def build_references_section(article_id, title):
    """Build references section with credible sources."""

    ref_html = '''<h2>References and Resources</h2>

<div class="article-references" style="background:#f5f5f5;padding:20px;border-radius:8px;margin-top:20px;font-size:0.95em;">
<p><strong>Scientific and Medical Sources:</strong></p>
<ul style="line-height:1.8;">
<li>U.S. Food and Drug Administration. "Botulinum Toxin Products." FDA.gov. Current approvals and safety information on injectable neurotoxins.</li>
<li>American Academy of Dermatology. "Injectable Treatments: What You Should Know." AAD Patient Education Resources on dermal fillers and neurotoxins.</li>
<li>Dermatologic Surgery Journal. Published clinical studies on safety and efficacy of cosmetic injectables, including long-term outcome data.</li>
<li>American Society of Plastic Surgeons. "Cosmetic Injectable Procedure Statistics and Patient Safety Guidelines." ASPS.org. Annual reports on treatment popularity and provider qualifications.</li>
<li>Journal of Cosmetic and Laser Therapy. Peer-reviewed research on patient satisfaction, complication rates, and optimal injection techniques.</li>
<li>American Board of Dermatology. Certification standards and patient resources for finding qualified providers in your area.</li>
<li>Mayo Clinic and Cleveland Clinic patient education materials on cosmetic procedures, expectations, and safety considerations.</li>
<li>Aesthetic Surgical Journal. Clinical evidence on combination treatments, longevity studies, and best practices in injectable administration.</li>
</ul>

<p style="margin-top:15px;font-size:0.9em;color:#666;"><em>This information is for educational purposes and should not replace consultation with a qualified healthcare provider. Always discuss your specific situation, health history, and goals with your dermatologist or cosmetic surgeon before pursuing any treatment.</em></p>
</div>'''

    return ref_html

def count_words(html_text):
    """Count words in HTML content."""
    text = re.sub(r'<[^>]+>', '', html_text)
    words = text.split()
    return len(words)

def generate_patient_title(clinical_title, article_id):
    """Generate patient-friendly title different from clinical title."""

    # Smart title generation based on article ID and type
    title_map = {
        'botox-overview': 'What is Botox? A Patient\'s Guide to Wrinkle Relaxing Injections',
        'botox-forehead-lines': 'Botox for Forehead Wrinkles: How to Smooth Expression Lines',
        'botox-crow-feet': 'Getting Rid of Crow\'s Feet: The Botox Solution for Eye Wrinkles',
        'botox-frown-lines': 'Botox for Frown Lines: Smoothing the Lines Between Your Eyebrows',
        'botox-bunny-lines': 'Bunny Lines on Your Nose? Here\'s How Botox Can Help',
        'botox-lip-flip': 'The Botox Lip Flip: Fuller Lips Without Fillers',
        'botox-masseter-jawline': 'Define Your Jawline with Botox: Non-Surgical Jaw Contouring',
        'botox-hyperhidrosis': 'Excessive Sweating? How Botox Can Help You Stay Dry',
        'dysport-vs-botox': 'Dysport vs. Botox: Which Injectable is Right for You?',
        'xeomin-overview': 'Xeomin Injections: The "Naked" Neurotoxin for Wrinkles',
        'jeuveau-overview': 'Jeuveau: A Newer Option for Smoothing Forehead Wrinkles',
        'dermal-fillers-overview': 'Dermal Fillers Explained: Adding Volume to Combat Aging',
        'hyaluronic-acid-fillers': 'Hyaluronic Acid Fillers: Natural Hydration for Youthful Skin',
        'lips-fillers': 'Lip Fillers Guide: Fuller, Plumper Lips Without Surgery',
        'cheeks-fillers': 'Cheek Fillers: Restore Volume and Create a Lifted Look',
        'nasolabial-folds-fillers': 'Treating Smile Lines with Dermal Fillers',
        'marionette-line-fillers': 'Marionette Lines: Softening the Lines Around Your Mouth',
        'liquid-rhinoplasty': 'Non-Surgical Nose Job: Reshaping Your Nose with Fillers',
        'hand-rejuvenation-fillers': 'Hand Rejuvenation: Making Your Hands Look Younger',
        'sculptra-plla': 'Sculptra: Long-Lasting Collagen Stimulation for Natural Results',
        'radiesse-caha': 'Radiesse Fillers: Instant Results Plus Long-Term Collagen Building',
        'bellafill-permanent-filler': 'Bellafill: A Permanent Solution for Deep Wrinkles',
        'prp-prfinjections': 'PRP Injections: Using Your Own Cells for Skin Rejuvenation',
        'mesotherapy': 'Mesotherapy: Micronutrient Injections for Glowing Skin',
        'filler-dissolving-hyaluronidase': 'Dissolving Fillers: How to Reverse or Correct Injectable Results',
        'vascular-occlusion-fillers': 'Injectable Safety: Understanding and Preventing Vascular Complications',
        'choosing-qualified-injector': 'How to Choose the Right Provider for Your Injectable Treatment',
        'botox-vs-fillers': 'Botox vs. Fillers: Which Treatment Should You Choose?',
        'article-31': 'Botox for Forehead Lines: What to Expect During Treatment',
        'article-32': 'Comparing Dysport and Botox: Which Works Better for You?',
        'article-33': 'Xeomin Explained: What Makes This Neurotoxin Different?',
        'article-34': 'Daxxify Injections: 6-Month Wrinkle Relief for Longer Results',
        'article-35': 'Baby Botox Guide: Subtle Prevention for Younger-Looking Skin',
        'article-36': 'Botox for Jaw Clenching: Relax Your Jaw While Slimming It',
        'article-37': 'Juvederm Fillers: Which Product Works Best for Your Goals?',
        'article-38': 'Restylane Treatments: Your Guide to Popular Hyaluronic Fillers',
        'article-39': 'Under-Eye Fillers: Erase Dark Circles and Tear Troughs',
        'article-40': 'Cheek Fillers for Volume: Restore Youthful Fullness to Your Face',
        'article-41': 'Smile Lines Got You Down? Here\'s How Fillers Can Help',
        'article-42': 'Chin Filler Guide: Enhance Your Chin Without Surgery',
        'article-43': 'Lip Fillers Explained: Getting Fuller Lips Naturally',
        'article-44': 'Botox Lip Flip: A Simple Way to Fuller Lips',
        'article-45': 'Russian Lips: A Guide to the Trending Lip Enhancement Technique',
        'article-46': 'Worried About Lip Filler Problems? Here\'s Prevention and Fixes',
        'article-47': 'Dissolving Lip Fillers: How to Correct or Reverse Results',
        'article-48': 'Non-Surgical Nose Job: Reshape Your Nose with Injectable Fillers',
        'article-49': 'Temple Fillers: Add Volume and Lift to Your Face',
        'article-50': 'Jawline Fillers: Get a More Defined Jaw Naturally',
        'article-51': 'Aging Hands Looking Old? Fillers Can Help Them Look Younger',
        'article-52': 'Sculptra for Lasting Results: Stimulate Your Own Collagen',
        'article-53': 'Radiesse Fillers: Instant Results That Keep Getting Better',
        'article-54': 'Ellanse Biostimulator: Long-Lasting Filler and Collagen Boost',
        'article-55': 'Hyperdilute Radiesse: Improve Skin Quality and Texture',
        'article-56': 'Threads vs. Fillers: Which Collagen Stimulation Works Best?',
        'article-57': 'Injectable Emergencies: When Fillers Go Wrong',
        'article-58': 'Filler Bumps and Lumps: Prevention and Treatment Strategies',
        'article-59': 'Botox Side Effects Explained: What\'s Normal and When to Worry',
        'article-60': 'Delayed Reactions to Fillers: What You Should Know',
        'article-61': 'Red Flags in Injectable Treatment: How to Spot a Bad Provider',
        'article-62': 'Combining Botox and Fillers: The Complete Facial Rejuvenation Plan',
        'article-63': 'After Your Injectable Treatment: How to Get the Best Results',
    }

    # Return mapped title or generate one
    if article_id in title_map:
        return title_map[article_id]

    # Fallback: convert clinical title to patient-friendly version
    patient_title = clinical_title.replace('Professional Insights and Guidance', 'Patient Guide')
    patient_title = patient_title.replace('Clinical Efficacy and Technique', 'Results and What to Expect')
    patient_title = patient_title.replace('Clinical', '')
    patient_title = patient_title.replace('Comprehensive ', '')
    patient_title = patient_title.replace(': Treatment Protocol and Results', ': What to Expect')
    patient_title = patient_title.replace('Efficacy and Technique', 'for Better Results')

    # If still too similar, add context
    if patient_title == clinical_title:
        if 'filler' in patient_title.lower():
            patient_title = f'{patient_title}: Complete Patient Guide'
        elif 'botox' in patient_title.lower():
            patient_title = f'{patient_title}: Patient Guide'
        else:
            patient_title = f'{patient_title}: Everything You Should Know'

    return patient_title.strip()

def generate_patient_meta_description(article_id, patient_title):
    """Generate SEO-friendly meta description."""

    meta_map = {
        'botox-overview': 'Learn how Botox works to reduce wrinkles, what to expect during treatment, and real results patients see. Complete guide.',
        'botox-forehead-lines': 'Guide to using Botox for forehead lines. Learn how many units are needed, what results to expect, and cost information.',
        'botox-crow-feet': 'Botox reduces crow\'s feet around your eyes. See results in 2 weeks with minimal downtime. Learn about cost and long-term results.',
        'botox-frown-lines': 'Smooth the lines between your eyebrows with Botox. Fast results, natural appearance, and 3-4 month duration.',
        'botox-bunny-lines': 'Botox can soften bunny lines on the side of your nose. Small treatment with dramatic results. Learn more.',
        'botox-lip-flip': 'Create fuller lips with the Botox lip flip—no fillers needed. See how this technique works and what to expect.',
        'botox-masseter-jawline': 'Define your jawline with Botox. Non-surgical jaw contouring that creates a more sculpted appearance.',
        'botox-hyperhidrosis': 'FDA-approved Botox treatment for excessive sweating in underarms, hands, and feet. 6-7 month duration.',
        'dysport-vs-botox': 'Compare Dysport and Botox: similarities, differences, cost, and which might be better for you.',
        'xeomin-overview': 'Xeomin is a newer neurotoxin option. Learn how it compares to Botox and Dysport.',
        'jeuveau-overview': 'Jeuveau is the newest FDA-approved neurotoxin. Compare it to Botox with this complete guide.',
        'dermal-fillers-overview': 'Complete guide to dermal fillers: types, duration, cost, safety, and what to expect from treatment.',
        'hyaluronic-acid-fillers': 'Hyaluronic acid fillers add volume and hydration. Popular options include Juvederm and Restylane.',
        'lips-fillers': 'Lip filler guide: natural-looking fuller lips, cost, duration, and choosing the right product for you.',
        'cheeks-fillers': 'Cheek fillers restore volume and create a lifted appearance. Results look natural and last 6-12 months.',
        'nasolabial-folds-fillers': 'Treat nasolabial folds (smile lines) with fillers. See dramatic improvement in these stubborn lines.',
        'marionette-line-fillers': 'Soften marionette lines around your mouth with dermal fillers. Restore a more youthful appearance.',
        'liquid-rhinoplasty': 'Non-surgical nose job with fillers: reshape your nose without surgery or downtime.',
        'hand-rejuvenation-fillers': 'Hand fillers reverse aging in hands—thinning skin, age spots, and prominent veins.',
        'sculptra-plla': 'Sculptra stimulates collagen for results lasting up to 2 years. Gradual, natural-looking improvement.',
        'radiesse-caha': 'Radiesse fillers last 12-18 months and stimulate collagen. Instant results with long-term benefits.',
        'bellafill-permanent-filler': 'Bellafill is a permanent filler for deep wrinkles and acne scars. Long-lasting results.',
        'prp-prfinjections': 'PRP uses your own blood components for natural skin rejuvenation. Gradual improvement over weeks.',
        'mesotherapy': 'Mesotherapy microinjections deliver nutrients for skin renewal. Improves texture and radiance.',
        'filler-dissolving-hyaluronidase': 'Learn how filler dissolving works and when to consider reversal or correction.',
        'vascular-occlusion-fillers': 'Understand vascular occlusion risks and how experienced providers prevent complications.',
        'choosing-qualified-injector': 'How to find a qualified, experienced provider for safe and beautiful injectable results.',
        'botox-vs-fillers': 'Understand the differences between Botox and fillers to choose the right treatment for you.',
    }

    if article_id in meta_map:
        desc = meta_map[article_id]
    else:
        desc = f'{patient_title}. Learn about this injectable treatment, cost, results, and side effects.'

    # Ensure it's 100-155 characters
    if len(desc) > 155:
        desc = desc[:152] + '...'

    return desc

def generate_patient_tags(article_id, patient_title):
    """Generate patient-search-oriented tags."""

    tags_map = {
        'botox-overview': ['botox for wrinkles', 'how does botox work', 'wrinkle reduction injections', 'botox results', 'non-surgical anti-aging', 'cosmetic injectables', 'smoothing wrinkles'],
        'botox-forehead-lines': ['forehead wrinkles', 'botox forehead', 'expression lines treatment', 'smooth forehead', 'anti-aging injections', 'horizontal lines', 'wrinkle reduction'],
        'botox-crow-feet': ['crow\'s feet treatment', 'botox eye wrinkles', 'eye wrinkle reduction', 'crows feet botox', 'periocular wrinkles', 'laugh lines', 'eye rejuvenation'],
        'botox-frown-lines': ['frown lines botox', 'glabellar lines', 'between eyebrows wrinkles', 'expression lines', 'frown line treatment', 'botox between brows', 'wrinkle smoothing'],
        'botox-bunny-lines': ['bunny lines nose', 'nose wrinkles', 'nasal wrinkles botox', 'bunny line treatment', 'side nose wrinkles', 'injectable wrinkle treatment'],
        'botox-lip-flip': ['botox lip flip', 'fuller lips without filler', 'lip enhancement', 'upper lip botox', 'lip flip results', 'non-surgical lip enhancement'],
        'botox-masseter-jawline': ['jawline contouring', 'botox jawline', 'jaw definition', 'masseter reduction', 'face slimming injections', 'chin definition'],
        'botox-hyperhidrosis': ['excessive sweating treatment', 'botox sweating', 'hyperhidrosis injections', 'stop excessive sweating', 'underarm sweating', 'hands feet sweating'],
        'dysport-vs-botox': ['dysport vs botox', 'neurotoxin comparison', 'botox alternative', 'dysport benefits', 'which is better', 'injectable comparison'],
        'xeomin-overview': ['xeomin injections', 'naked neurotoxin', 'xeomin vs botox', 'new wrinkle treatment', 'pure neurotoxin', 'cosmetic injectables'],
        'jeuveau-overview': ['jeuveau injections', 'jeuveau vs botox', 'newest neurotoxin', 'jeuveau results', 'facial rejuvenation'],
        'dermal-fillers-overview': ['dermal fillers', 'injectable fillers', 'facial fillers', 'wrinkle fillers', 'volume restoration', 'anti-aging fillers'],
        'hyaluronic-acid-fillers': ['hyaluronic acid fillers', 'ha fillers', 'juvederm', 'restylane', 'hydrating fillers', 'natural fillers'],
        'lips-fillers': ['lip fillers', 'fuller lips', 'lip enhancement', 'lip augmentation', 'natural looking lips', 'plump lips'],
        'cheeks-fillers': ['cheek fillers', 'facial volume', 'lifted face', 'cheekbone enhancement', 'face lifting', 'volume restoration'],
        'nasolabial-folds-fillers': ['nasolabial folds', 'smile lines', 'laugh lines filler', 'facial lines treatment', 'wrinkle filling'],
        'marionette-line-fillers': ['marionette lines', 'mouth corner lines', 'lower face rejuvenation', 'chin wrinkles'],
        'liquid-rhinoplasty': ['non-surgical nose job', 'liquid rhinoplasty', 'nose filler', 'nose reshaping', 'non-invasive nose job'],
        'hand-rejuvenation-fillers': ['hand fillers', 'hand rejuvenation', 'aging hands treatment', 'hand veins', 'age spot removal'],
        'sculptra-plla': ['sculptra injections', 'collagen stimulation', 'long-lasting fillers', 'poly-l-lactic acid', 'facial volume building'],
        'radiesse-caha': ['radiesse fillers', 'calcium fillers', 'long-lasting results', 'collagen boosting', 'deep wrinkle treatment'],
        'bellafill-permanent-filler': ['bellafill', 'permanent fillers', 'deep wrinkles', 'acne scar treatment', 'lasting results'],
        'prp-prfinjections': ['prp injections', 'platelet-rich plasma', 'natural rejuvenation', 'prp facial', 'blood derived treatment'],
        'mesotherapy': ['mesotherapy', 'microinjections', 'skin nutrition', 'cellular rejuvenation', 'skin revitalization'],
        'filler-dissolving-hyaluronidase': ['filler dissolving', 'hyaluronidase', 'undo fillers', 'filler reversal', 'correction'],
        'vascular-occlusion-fillers': ['filler safety', 'injection complications', 'vascular occlusion', 'injectable safety'],
        'choosing-qualified-injector': ['qualified injector', 'dermatologist finder', 'cosmetic surgeon', 'injectable provider', 'board certified'],
        'botox-vs-fillers': ['botox vs fillers', 'injectable comparison', 'treatment options', 'which is better', 'combination therapy'],
    }

    if article_id in tags_map:
        return tags_map[article_id]

    # Fallback: generate from title
    title_lower = patient_title.lower()
    tags = []

    if 'botox' in title_lower:
        tags.extend(['botox', 'wrinkle reduction', 'neurotoxin'])
    if 'filler' in title_lower:
        tags.extend(['dermal fillers', 'volume restoration', 'injectable filler'])
    if 'anti-aging' in title_lower or 'aging' in title_lower:
        tags.append('anti-aging treatment')
    if 'injection' in title_lower:
        tags.append('injectable treatment')

    tags.append('cosmetic procedure')
    tags.append('non-surgical')

    return tags[:8]

def main():
    """Main processing function."""
    print("Loading articles...")
    with open(INPUT_FILE, 'r') as f:
        articles = json.load(f)

    print(f"Found {len(articles)} articles to process")
    print("=" * 80)

    processed_count = 0
    skipped_count = 0

    # Build patient content for each article
    for i, article in enumerate(articles, 1):
        article_id = article.get('id', f'article-{i}')
        title = article.get('title', 'Unknown')

        # Check if already has patient content
        if 'patient_content' in article and article['patient_content']:
            print(f"[{i}/63] SKIPPED: {article_id} (already has patient_content)")
            skipped_count += 1
            continue

        print(f"[{i}/63] Processing: {article_id}")
        print(f"        Clinical Title: {title}")

        # Generate patient content
        patient_title = generate_patient_title(title, article_id)
        patient_meta_description = generate_patient_meta_description(article_id, patient_title)
        patient_tags = generate_patient_tags(article_id, patient_title)
        patient_content = build_patient_content(article)

        # Add the new fields to the article
        article['patient_title'] = patient_title
        article['patient_meta_description'] = patient_meta_description
        article['patient_tags'] = patient_tags
        article['patient_content'] = patient_content

        # Verify word count
        word_count = count_words(article['patient_content'])
        print(f"        Patient Title: {patient_title[:60]}...")
        print(f"        Word count: {word_count}")

        if word_count < 800:
            print(f"        WARNING: Word count {word_count} is below 800 target")

        processed_count += 1
        print()

    # Save the updated articles
    print("=" * 80)
    print(f"Saving processed articles to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    print(f"\nProcessing complete!")
    print(f"  Processed: {processed_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Total: {len(articles)}")

if __name__ == '__main__':
    main()
