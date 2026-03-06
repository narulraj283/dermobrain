#!/usr/bin/env python3
import json
import re
from html.parser import HTMLParser

class HTMLWordCounter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.words = []

    def handle_data(self, data):
        words = data.split()
        self.words.extend(words)

def count_words(html_content):
    parser = HTMLWordCounter()
    parser.feed(html_content)
    return len(parser.words)

def is_filler(article):
    """Check if article meets filler criteria"""
    content = article.get('content', '')
    word_count = count_words(content)

    filler_phrases = [
        'multisystem concern',
        'integrated treatment approaches',
        'emerging therapies target',
        'favorable safety profiles',
        'diverse clinical phenotypes'
    ]

    has_references = '<h2>References</h2>' in content
    has_filler_phrase = any(phrase in content for phrase in filler_phrases)

    # Filler if: word count < 800, no references, or has filler phrases
    is_filler_flag = word_count < 800 or not has_references or has_filler_phrase

    return is_filler_flag, word_count

# Load articles
with open('/sessions/affectionate-nifty-archimedes/mnt/ClaudeMacStudio/dermobrain/data/articles_skin-conditions.json', 'r') as f:
    articles = json.load(f)

fillers = []
for article in articles:
    filler_flag, word_count = is_filler(article)
    if filler_flag:
        fillers.append({
            'slug': article.get('slug'),
            'title': article.get('title'),
            'word_count': word_count
        })

print(f"Total articles: {len(articles)}")
print(f"Filler articles: {len(fillers)}\n")
print("Filler articles to rewrite:")
for i, item in enumerate(fillers, 1):
    print(f"{i}. {item['slug']} ({item['word_count']} words) - {item['title']}")
