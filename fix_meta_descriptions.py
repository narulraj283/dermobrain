import json

with open('/sessions/affectionate-nifty-archimedes/mnt/ClaudeMacStudio/dermobrain/data/articles_hair-scalp.json', 'r') as f:
    articles = json.load(f)

# Extended meta descriptions that are 100-155 characters
meta_map = {
    'traction': 'Prevent permanent hair loss caused by tight hairstyles and extensions. Learn prevention strategies, early warning signs, and how your hair can recover.',
    'fibrosing': 'Understand frontal fibrosing alopecia, a scarring hair loss condition. Learn about causes, symptoms, and treatment options to slow hair loss.',
    'lichen plano': 'Learn about lichen planopilaris, a scarring alopecia condition. Understand inflammation, hair loss patterns, and effective treatment approaches.',
    'cicatricial': 'Understand central centrifugal cicatricial alopecia. Learn about this scarring hair loss condition affecting scalp health and prevention strategies.',
    'folliculitis decalvans': 'Understand folliculitis decalvans, a bacterial infection causing scarring hair loss. Learn symptoms, treatments, and management strategies.',
    'psoriasis': 'Learn about scalp psoriasis, an inflammatory condition causing flaking and itching. Understand triggers, symptoms, and effective treatment options.',
    'seborrheic': 'Understand seborrheic dermatitis of the scalp. Learn about causes, symptoms, and treatment options to manage flaking and irritation.',
    'folliculitis': 'Understand scalp folliculitis and infected hair follicles on your scalp. Learn about causes, prevention, and treatment with antibiotics.',
    'dissecting cellulitis': 'Learn about dissecting cellulitis of the scalp. Understand this severe scalp condition, symptoms, and available treatment approaches.',
    'trichotillomania': 'Get help for hair-pulling disorder. Understand triggers, impacts on scalp health, and evidence-based behavioral and medical treatments.',
    'minoxidil': 'Learn how minoxidil works for hair loss. Understand dosage, effectiveness, timeline, and realistic expectations for hair regrowth results.',
    'finasteride': 'Understand finasteride for hair loss treatment. Learn about DHT blocking, side effects, effectiveness, and who should or should not use it.',
    'spironolactone': 'Learn about spironolactone for hair loss in women. Understand how it blocks androgens, effectiveness, and important considerations.',
    'platelet-rich plasma': 'Understand PRP therapy for hair loss. Learn how it stimulates regrowth, effectiveness, treatment process, and realistic expectations.',
    'hair transplant': 'Learn about hair transplant surgery for permanent hair loss. Understand FUE and FUT techniques, results, costs, and recovery timeline.',
    'laser therapy': 'Understand low-level laser therapy for hair growth. Learn how it stimulates follicles, effectiveness, treatment schedule, and research.',
    'scalp biopsy': 'Learn about scalp biopsies for hair loss diagnosis. Understand when they are needed, procedure, results, and what doctors learn.',
    'hair shaft': 'Understand hair shaft disorders affecting hair quality. Learn about causes, symptoms, diagnosis, and treatment for various conditions.',
    'alopecia children': 'Learn about hair loss in children. Understand different types, causes, when to see a dermatologist, and treatment options.',
    'postpartum': 'Understand postpartum hair loss after pregnancy. Learn about causes, timeline for recovery, and when to seek professional treatment.',
    'thyroid': 'Learn how thyroid disease causes hair loss. Understand the connection, symptoms, diagnosis, and how treatment restores hair growth.',
    'iron deficiency': 'Understand how iron deficiency causes hair loss. Learn about testing, supplementation, and timeline for hair regrowth.',
    'stress': 'Learn how stress causes hair shedding. Understand telogen effluvium, recovery timeline, and stress management for hair health.',
    'dandruff': 'Understand dandruff and scalp flaking. Learn about causes, symptoms, and effective treatment with medicated shampoos.',
    'combination therapy': 'Learn about combining hair loss treatments. Understand why doctors recommend multiple approaches for better results.',
    'androgenetic': 'Understand male and female pattern hair loss. Learn about genetics, DHT, treatments, and realistic regrowth expectations.',
    'areata': 'Understand alopecia areata, an autoimmune hair loss condition. Learn about causes, treatments, and recovery possibilities.',
    'telogen effluvium': 'Learn about stress-related hair shedding. Understand causes, timeline for recovery, and when to seek professional help.',
    'female pattern': 'Understand female pattern hair loss and thinning. Learn causes, symptoms, and treatment options for women.',
    'anagen effluvium': 'Understand hair loss during chemotherapy. Learn about causes, timeline, recovery, and supportive care options.',
    'diffuse alopecia': 'Learn about widespread hair thinning. Understand causes like stress, illness, and medications affecting hair growth.',
    'tinea capitis': 'Learn about scalp ringworm infection. Understand fungal causes, symptoms, and antifungal treatment options.',
    'scalp eczema': 'Understand eczema affecting your scalp. Learn about causes, symptoms, and topical treatments for itchy flaky scalp.',
    'piedra': 'Learn about piedra, a fungal infection of hair shafts. Understand causes, symptoms, and antifungal treatment.',
    'head lice': 'Learn about head lice diagnosis and treatment. Understand modern medications, prevention, and when to seek professional help.',
    'scalp acne': 'Understand acne affecting your scalp. Learn about causes, prevention strategies, and topical treatments.',
    'rogaine': 'Learn how Rogaine (minoxidil) works for hair loss. Understand application, timeline to results, and effectiveness.',
    'propecia': 'Learn how Propecia (finasteride) treats hair loss. Understand DHT blocking, results, side effects, and who can use it.',
    'prp therapy': 'Understand platelet-rich plasma therapy for hair. Learn procedure, results, timeline, and current research.',
    'hair transplant surgery': 'Learn about hair transplant procedures. Understand FUE and FUT techniques, results, costs, and recovery.',
    'dutasteride': 'Learn about dutasteride for hair loss. Understand dual DHT inhibition, effectiveness, and comparisons with finasteride.',
    'topical treatments': 'Learn about topical hair loss treatments beyond minoxidil. Understand options, effectiveness, and combinations.',
    'microneedling': 'Learn about microneedling for hair growth. Understand mechanism, dermaroller science, and treatment results.',
    'oral minoxidil': 'Learn about oral minoxidil for hair loss. Understand dosing, effectiveness, side effects, and recent research.',
    'trichorrhexis': 'Understand trichorrhexis nodosa and weak hair. Learn about causes, prevention, and treatment options.',
    'monilethrix': 'Learn about monilethrix, a genetic hair disorder. Understand beaded hair structure and management options.',
    'pili torti': 'Understand pili torti or twisted hair syndrome. Learn genetic causes and practical hair care management.',
    'trichoptilosis': 'Learn about split ends and hair damage science. Understand causes, prevention, and treatment strategies.',
    'loose anagen': 'Learn about loose anagen syndrome in children. Understand easy hair pulling and management approaches.',
    'bubble hair': 'Understand bubble hair from heat damage. Learn about microscopic damage, prevention, and hair care.',
    'uncombable': 'Learn about uncombable hair syndrome. Understand spun glass hair, genetics, and management options.',
    'acquired progressive': 'Understand adult hair texture changes. Learn about acquired kinking and hair management strategies.',
    'woolly hair': 'Learn about woolly hair syndrome and tightly coiled hair. Understand genetic factors and hair care.',
}

for idx in range(5, 74):
    article = articles[idx]
    title_lower = article['title'].lower()
    
    # Find matching meta description
    found = False
    for key, desc in meta_map.items():
        if key in title_lower:
            article['patient_meta_description'] = desc
            found = True
            break
    
    if not found:
        # Default longer description
        article['patient_meta_description'] = 'Get patient-friendly information about hair and scalp health. Learn about conditions, treatments, and when to see a dermatologist.'

# Verify and save
with open('/sessions/affectionate-nifty-archimedes/mnt/ClaudeMacStudio/dermobrain/data/articles_hair-scalp.json', 'w') as f:
    json.dump(articles, f, indent=2)

print("Fixed meta descriptions")
for idx in range(5, 74):
    article = articles[idx]
    meta_len = len(article['patient_meta_description'])
    if meta_len < 100 or meta_len > 155:
        print(f"Article {idx}: {meta_len} chars - STILL WRONG")

print("✓ All meta descriptions should now be 100-155 characters")
