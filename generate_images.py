#!/usr/bin/env python3
"""Generate branded images for DermoBrain categories using Pillow."""

import json
import os
from PIL import Image, ImageDraw, ImageFont

# Brand colors
PRIMARY = '#1A6B54'
ACCENT = '#E8734A'
WHITE = '#FFFFFF'
DARK = '#1a1a1a'

# Category icons (emoji/text representations)
CATEGORY_ICONS = {
    "skin-conditions": "🔬",
    "skincare-science": "🧪",
    "hair-scalp": "💇",
    "injectables": "💉",
    "lasers": "✨",
    "rejuvenation": "🌟",
    "skin-cancer": "🎗️",
    "pediatric": "👶",
    "mohs-surgery": "🔬",
    "procedures": "🏥",
    "allergies": "🤧",
    "body-contouring": "💪",
    "lifestyle": "🌿",
    "mens-derm": "👨",
    "myths": "❓",
    "nails": "💅",
    "skin-of-color": "🌍",
    "womens-derm": "👩",
    "pre-post-op": "📋",
    "procedures-az": "📖",
}


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_font(size):
    try:
        return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', size)
    except:
        return ImageFont.load_default()


def get_font_regular(size):
    try:
        return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)
    except:
        return ImageFont.load_default()


def create_category_header(category_name, slug, output_dir):
    """Create a 1200x400 category header image."""
    width, height = 1200, 400
    img = Image.new('RGB', (width, height), hex_to_rgb(PRIMARY))
    draw = ImageDraw.Draw(img)

    # Decorative accent bar at top
    draw.rectangle([0, 0, width, 6], fill=hex_to_rgb(ACCENT))

    # Diagonal accent stripe
    for i in range(0, 60, 2):
        draw.line([(width - 200 + i, 0), (width + i, height)], fill=hex_to_rgb('#1D7A60'), width=1)

    # Category name
    font_large = get_font(48)
    font_small = get_font_regular(22)

    # Center text
    bbox = draw.textbbox((0, 0), category_name, font=font_large)
    text_w = bbox[2] - bbox[0]
    x = (width - text_w) // 2
    draw.text((x, 140), category_name, fill=WHITE, font=font_large)

    # Subtitle
    subtitle = "DermoBrain — Your Trusted Dermatology Encyclopedia"
    bbox2 = draw.textbbox((0, 0), subtitle, font=font_small)
    text_w2 = bbox2[2] - bbox2[0]
    x2 = (width - text_w2) // 2
    draw.text((x2, 210), subtitle, fill='#B0D4C8', font=font_small)

    # Bottom accent bar
    draw.rectangle([0, height - 6, width, height], fill=hex_to_rgb(ACCENT))

    filepath = os.path.join(output_dir, f"{slug}.png")
    img.save(filepath, quality=95)
    return filepath


def create_og_image(title, category_name, slug, output_dir):
    """Create a 1200x630 OG image for an article."""
    width, height = 1200, 630
    img = Image.new('RGB', (width, height), hex_to_rgb(PRIMARY))
    draw = ImageDraw.Draw(img)

    # Accent bar top
    draw.rectangle([0, 0, width, 8], fill=hex_to_rgb(ACCENT))

    # White content area
    margin = 60
    draw.rounded_rectangle(
        [margin, margin + 20, width - margin, height - margin - 20],
        radius=20, fill=WHITE
    )

    # Logo area
    font_logo = get_font(28)
    draw.text((margin + 30, margin + 40), "DermoBrain", fill=hex_to_rgb(PRIMARY), font=font_logo)

    # Category badge
    font_cat = get_font_regular(16)
    draw.rounded_rectangle([margin + 30, margin + 90, margin + 30 + len(category_name) * 10 + 20, margin + 120], radius=12, fill=hex_to_rgb(ACCENT))
    draw.text((margin + 40, margin + 95), category_name, fill=WHITE, font=font_cat)

    # Title (word wrap)
    font_title = get_font(36)
    max_width = width - margin * 2 - 60

    words = title.split()
    lines = []
    current_line = ""
    for word in words:
        test = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font_title)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    y = margin + 150
    for line in lines[:3]:  # Max 3 lines
        draw.text((margin + 30, y), line, fill=hex_to_rgb(DARK), font=font_title)
        y += 48

    # Bottom text
    font_bottom = get_font_regular(16)
    draw.text((margin + 30, height - margin - 55), "dermobrain.com", fill='#999', font=font_bottom)

    # Bottom accent
    draw.rectangle([0, height - 8, width, height], fill=hex_to_rgb(ACCENT))

    filepath = os.path.join(output_dir, f"{slug}.png")
    img.save(filepath, quality=90)
    return filepath


def main():
    # Create directories
    cat_dir = "assets/images/categories"
    og_dir = "assets/images/articles"
    os.makedirs(cat_dir, exist_ok=True)
    os.makedirs(og_dir, exist_ok=True)

    # Load categories
    with open("data/categories.json", 'r') as f:
        categories = json.load(f)['categories']

    # Generate category header images
    print("Generating category header images...")
    for cat in categories:
        name = cat['name']
        slug = cat['slug']
        filepath = create_category_header(name, slug, cat_dir)
        print(f"  Created: {filepath}")

    # Generate OG images for new articles (sample from each category)
    print("\nGenerating article OG images...")
    count = 0
    for cat in categories:
        slug = cat['slug']
        try:
            with open(f"data/articles_{slug}.json", 'r') as f:
                articles = json.load(f)
        except:
            continue

        for article in articles:
            article_slug = article.get('slug', '')
            title = article.get('title', '')
            if article_slug and title:
                create_og_image(title, cat['name'], article_slug, og_dir)
                count += 1

    print(f"\nTotal article OG images: {count}")
    print(f"Category headers: {len(categories)}")
    print("Done!")


if __name__ == "__main__":
    main()
