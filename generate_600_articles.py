#!/usr/bin/env python3
"""Generate 600 new articles for DermoBrain.com across all 20 categories."""

import json
import os
import re
import random

# Article topics per category with subcategory assignments
ARTICLE_TOPICS = {
    "skin-conditions": {
        "count": 89,
        "topics": [
            # acne (15)
            ("Acne Mechanica: Sports Equipment and Friction-Induced Breakouts", "acne"),
            ("Neonatal Acne: Understanding Newborn Skin Breakouts", "acne"),
            ("Acne Conglobata: Severe Interconnected Nodular Acne", "acne"),
            ("Acne Keloidalis Nuchae: Bumps on the Back of the Neck", "acne"),
            ("Chloracne: Industrial Chemical-Induced Acne", "acne"),
            ("Acne Excoriée: When Picking Makes Acne Worse", "acne"),
            ("Steroid Acne: Corticosteroid-Induced Breakouts", "acne"),
            ("Infantile Acne: Persistent Acne in Babies", "acne"),
            ("Acne Fulminans: Acute Ulcerative Acne Emergency", "acne"),
            ("Gram-Negative Folliculitis: Antibiotic-Resistant Acne", "acne"),
            ("Pomade Acne: Hair Product-Related Breakouts", "acne"),
            ("Occupational Acne: Workplace Chemical Exposure and Skin", "acne"),
            ("Tropical Acne: Heat and Humidity-Related Breakouts", "acne"),
            ("Drug-Induced Acne: Medications That Cause Breakouts", "acne"),
            ("Pre-Menstrual Acne Flares: Cyclical Breakout Patterns", "acne"),
            # eczema-dermatitis (12)
            ("Nummular Eczema: Coin-Shaped Patches of Irritated Skin", "eczema-dermatitis"),
            ("Dyshidrotic Eczema: Blisters on Hands and Feet", "eczema-dermatitis"),
            ("Stasis Dermatitis: Eczema from Poor Circulation", "eczema-dermatitis"),
            ("Seborrheic Dermatitis: Flaky Skin on the Face and Scalp", "eczema-dermatitis"),
            ("Neurodermatitis: The Itch-Scratch Cycle", "eczema-dermatitis"),
            ("Asteatotic Eczema: Dry Winter Skin Condition", "eczema-dermatitis"),
            ("Photoallergic Dermatitis: Sun-Triggered Skin Reactions", "eczema-dermatitis"),
            ("Hand Eczema: Occupational and Chronic Hand Dermatitis", "eczema-dermatitis"),
            ("Eyelid Dermatitis: Sensitive Skin Around the Eyes", "eczema-dermatitis"),
            ("Venous Eczema: Lower Leg Skin Changes", "eczema-dermatitis"),
            ("Perioral Dermatitis: Rash Around the Mouth", "eczema-dermatitis"),
            ("Eczema Herpeticum: When Herpes Complicates Eczema", "eczema-dermatitis"),
            # psoriasis (10)
            ("Guttate Psoriasis: Small Drop-Like Lesions After Infection", "psoriasis"),
            ("Inverse Psoriasis: Smooth Red Patches in Skin Folds", "psoriasis"),
            ("Pustular Psoriasis: Pus-Filled Blisters on Red Skin", "psoriasis"),
            ("Erythrodermic Psoriasis: Life-Threatening Skin Inflammation", "psoriasis"),
            ("Nail Psoriasis: How Psoriasis Affects Your Nails", "psoriasis"),
            ("Psoriatic Arthritis: When Psoriasis Attacks Your Joints", "psoriasis"),
            ("Scalp Psoriasis: Beyond Dandruff", "psoriasis"),
            ("Palmoplantar Psoriasis: Hands and Feet Involvement", "psoriasis"),
            ("Psoriasis and Cardiovascular Risk: The Heart Connection", "psoriasis"),
            ("Biologic Therapy for Psoriasis: A Patient Guide", "psoriasis"),
            # rosacea (8)
            ("Ocular Rosacea: When Rosacea Affects Your Eyes", "rosacea"),
            ("Phymatous Rosacea: Skin Thickening and Rhinophyma", "rosacea"),
            ("Papulopustular Rosacea: Inflammatory Bumps and Pimples", "rosacea"),
            ("Erythematotelangiectatic Rosacea: Persistent Facial Redness", "rosacea"),
            ("Rosacea Triggers: Foods, Weather, and Lifestyle Factors", "rosacea"),
            ("Demodex Mites and Rosacea: The Microscopic Connection", "rosacea"),
            ("Rosacea vs Acne: How to Tell the Difference", "rosacea"),
            ("Managing Rosacea Flares: A Practical Action Plan", "rosacea"),
            # fungal-infections (8)
            ("Tinea Versicolor: Multicolored Patches on the Skin", "fungal-infections"),
            ("Tinea Corporis: Ringworm of the Body", "fungal-infections"),
            ("Tinea Pedis: Athlete's Foot Complete Guide", "fungal-infections"),
            ("Tinea Cruris: Jock Itch Prevention and Treatment", "fungal-infections"),
            ("Candidal Intertrigo: Yeast Infections in Skin Folds", "fungal-infections"),
            ("Tinea Capitis: Fungal Scalp Infections in Children", "fungal-infections"),
            ("Sporotrichosis: The Rose Gardener's Disease", "fungal-infections"),
            ("Majocchi Granuloma: Deep Follicular Fungal Infection", "fungal-infections"),
            # bacterial-infections (8)
            ("Cellulitis: Deep Skin Bacterial Infection", "bacterial-infections"),
            ("Impetigo: Highly Contagious Skin Infection in Children", "bacterial-infections"),
            ("MRSA Skin Infections: Resistant Staph Awareness", "bacterial-infections"),
            ("Folliculitis: Infected Hair Follicles", "bacterial-infections"),
            ("Erysipelas: Superficial Skin Infection with Sharp Borders", "bacterial-infections"),
            ("Furuncles and Carbuncles: Boils and Skin Abscesses", "bacterial-infections"),
            ("Necrotizing Fasciitis: Understanding Flesh-Eating Bacteria", "bacterial-infections"),
            ("Staphylococcal Scalded Skin Syndrome: Toxin-Mediated Disease", "bacterial-infections"),
            # viral-infections (8)
            ("Molluscum Contagiosum: Pearly Bumps in Children and Adults", "viral-infections"),
            ("Herpes Zoster: Shingles Causes and Modern Treatment", "viral-infections"),
            ("Common Warts: HPV Types and Removal Options", "viral-infections"),
            ("Plantar Warts: Painful Foot Warts Guide", "viral-infections"),
            ("Hand Foot and Mouth Disease: Viral Skin Rash in Kids", "viral-infections"),
            ("Herpes Simplex: Cold Sores and Genital Herpes Management", "viral-infections"),
            ("Pityriasis Rosea: The Christmas Tree Rash", "viral-infections"),
            ("Viral Exanthems: Childhood Rashes from Common Viruses", "viral-infections"),
            # autoimmune (8)
            ("Dermatomyositis: Muscle Weakness with Skin Rash", "autoimmune"),
            ("Morphea: Localized Scleroderma of the Skin", "autoimmune"),
            ("Pemphigus Vulgaris: Autoimmune Blistering Disease", "autoimmune"),
            ("Bullous Pemphigoid: Blistering in Older Adults", "autoimmune"),
            ("Systemic Lupus Erythematosus: The Butterfly Rash", "autoimmune"),
            ("Cutaneous Vasculitis: When Blood Vessels Become Inflamed", "autoimmune"),
            ("Scleroderma: Hardening and Tightening of the Skin", "autoimmune"),
            ("Lichen Planus: Purple Polygonal Papules", "autoimmune"),
            # pigmentation (6)
            ("Melasma: The Mask of Pregnancy", "pigmentation"),
            ("Vitiligo: Autoimmune Depigmentation of the Skin", "pigmentation"),
            ("Post-Inflammatory Hyperpigmentation: Dark Spots After Skin Injury", "pigmentation"),
            ("Albinism: Genetic Absence of Melanin", "pigmentation"),
            ("Solar Lentigines: Age Spots and Sun Damage", "pigmentation"),
            ("Pityriasis Alba: White Patches on Children's Skin", "pigmentation"),
            # other-conditions (6)
            ("Hidradenitis Suppurativa: Chronic Skin Abscesses", "other-conditions"),
            ("Granuloma Annulare: Ring-Shaped Skin Bumps", "other-conditions"),
            ("Lichen Sclerosus: White Patches on Genital Skin", "other-conditions"),
            ("Pyoderma Gangrenosum: Rapidly Enlarging Skin Ulcers", "other-conditions"),
            ("Pityriasis Rubra Pilaris: Orange-Red Scaling Disorder", "other-conditions"),
            ("Sweet Syndrome: Acute Febrile Neutrophilic Dermatosis", "other-conditions"),
        ]
    },
    "skincare-science": {
        "count": 44,
        "topics": [
            ("Niacinamide: The Multi-Benefit Skincare Powerhouse", "active-ingredients"),
            ("Hyaluronic Acid: Science Behind Skin Hydration", "active-ingredients"),
            ("Vitamin C Serums: Antioxidant Protection for Skin", "active-ingredients"),
            ("Bakuchiol: The Natural Retinol Alternative", "active-ingredients"),
            ("Azelaic Acid: Versatile Treatment for Acne and Rosacea", "active-ingredients"),
            ("Tranexamic Acid: Emerging Ingredient for Hyperpigmentation", "active-ingredients"),
            ("Peptides in Skincare: Building Blocks for Younger Skin", "active-ingredients"),
            ("Ceramides: Restoring Your Skin Barrier", "active-ingredients"),
            ("Glycolic Acid vs Salicylic Acid: Choosing Your Exfoliant", "active-ingredients"),
            ("Zinc Oxide in Skincare: Beyond Sunscreen Protection", "active-ingredients"),
            ("Mineral vs Chemical Sunscreen: Which Is Better for You", "sun-protection"),
            ("SPF Explained: Understanding Sun Protection Factor", "sun-protection"),
            ("UVA vs UVB: Different Rays Different Damage", "sun-protection"),
            ("Sunscreen for Dark Skin: Avoiding the White Cast", "sun-protection"),
            ("Sun Protection After Procedures: Post-Treatment Care", "sun-protection"),
            ("Blue Light and Skin: Does Screen Time Damage Your Skin", "sun-protection"),
            ("Sunscreen Myths Debunked: What Science Actually Says", "sun-protection"),
            ("Water-Resistant Sunscreen: Swimming and Sweat Guide", "sun-protection"),
            ("The 10-Step Korean Skincare Routine: Evidence Review", "skincare-routines"),
            ("Minimalist Skincare: Less Is More Approach", "skincare-routines"),
            ("Anti-Aging Skincare Routine for Your 30s", "skincare-routines"),
            ("Nighttime Skincare Routine: Maximizing Skin Repair", "skincare-routines"),
            ("Building a Routine for Sensitive Skin", "skincare-routines"),
            ("Skincare Routine for Oily Acne-Prone Skin", "skincare-routines"),
            ("Post-Workout Skincare: Sweat Pimples and Prevention", "skincare-routines"),
            ("Skincare Layering: The Correct Order of Products", "skincare-routines"),
            ("Double Cleansing: Is It Worth the Extra Step", "cleansing"),
            ("Oil Cleansing Method: Benefits and Risks", "cleansing"),
            ("Micellar Water: Gentle Cleansing Science", "cleansing"),
            ("Moisturizer Types: Creams Lotions and Ointments Explained", "cleansing"),
            ("Toner vs Essence: Understanding Asian Skincare Steps", "cleansing"),
            ("Exfoliation Guide: Physical vs Chemical Methods", "cleansing"),
            ("Face Masks: Sheet Masks Clay Masks and Overnight Masks", "cleansing"),
            ("The Science of Skin pH: Why It Matters for Product Choice", "barrier-microbiome"),
            ("Skin Microbiome: The Invisible Ecosystem on Your Skin", "barrier-microbiome"),
            ("Barrier Repair: How to Fix a Damaged Skin Barrier", "barrier-microbiome"),
            ("Skin Purging vs Breakouts: How to Tell the Difference", "barrier-microbiome"),
            ("Retinoids 101: Retinol Retinal and Prescription Tretinoin", "active-ingredients"),
            ("Alpha Hydroxy Acids: Glycolic Lactic and Mandelic Acid Guide", "active-ingredients"),
            ("Beta Hydroxy Acid: Salicylic Acid Deep Dive", "active-ingredients"),
            ("Benzoyl Peroxide: How It Works and How to Use It", "active-ingredients"),
            ("Squalane Oil: Lightweight Moisturizing Science", "active-ingredients"),
            ("Adapalene: Over-the-Counter Retinoid Guide", "active-ingredients"),
            ("Centella Asiatica: Traditional Remedy Meets Modern Science", "active-ingredients"),
        ]
    },
    "hair-scalp": {
        "count": 44,
        "topics": [
            ("Androgenetic Alopecia: Pattern Hair Loss Explained", "hair-loss"),
            ("Alopecia Areata: Autoimmune Hair Loss Patches", "hair-loss"),
            ("Telogen Effluvium: Stress-Related Hair Shedding", "hair-loss"),
            ("Female Pattern Hair Loss: Women's Hair Thinning Guide", "hair-loss"),
            ("Traction Alopecia: Hairstyle-Related Hair Loss", "hair-loss"),
            ("Anagen Effluvium: Chemotherapy-Induced Hair Loss", "hair-loss"),
            ("Postpartum Hair Loss: Shedding After Pregnancy", "hair-loss"),
            ("Diffuse Alopecia: Widespread Hair Thinning Causes", "hair-loss"),
            ("Hair Loss and Thyroid Disease: The Hormonal Connection", "hair-loss"),
            ("Iron Deficiency and Hair Loss: Nutritional Factors", "hair-loss"),
            ("Frontal Fibrosing Alopecia: Receding Hairline in Women", "scarring-alopecia"),
            ("Central Centrifugal Cicatricial Alopecia: Hair Loss in Black Women", "scarring-alopecia"),
            ("Lichen Planopilaris: Scarring Alopecia from Inflammation", "scarring-alopecia"),
            ("Discoid Lupus and Hair Loss: Autoimmune Scarring", "scarring-alopecia"),
            ("Folliculitis Decalvans: Infected Follicles Causing Hair Loss", "scarring-alopecia"),
            ("Dissecting Cellulitis of the Scalp: Perifolliculitis Treatment", "scarring-alopecia"),
            ("Scalp Psoriasis: More Than Just Dandruff", "scalp-conditions"),
            ("Seborrheic Dermatitis of the Scalp: Causes and Solutions", "scalp-conditions"),
            ("Scalp Folliculitis: Itchy Bumps on Your Head", "scalp-conditions"),
            ("Tinea Capitis: Ringworm of the Scalp", "scalp-conditions"),
            ("Scalp Eczema: Managing Itchy Flaky Scalp", "scalp-conditions"),
            ("Piedra: Fungal Infection of the Hair Shaft", "scalp-conditions"),
            ("Head Lice: Diagnosis and Modern Treatment Options", "scalp-conditions"),
            ("Scalp Acne: Causes Prevention and Treatment", "scalp-conditions"),
            ("Minoxidil: How It Works and What to Expect", "hair-treatments"),
            ("Finasteride for Hair Loss: Benefits Risks and Alternatives", "hair-treatments"),
            ("PRP Therapy for Hair Loss: Platelet-Rich Plasma Treatment", "hair-treatments"),
            ("Hair Transplant Surgery: FUE vs FUT Explained", "hair-treatments"),
            ("Low-Level Laser Therapy for Hair Regrowth", "hair-treatments"),
            ("Dutasteride for Hair Loss: Stronger DHT Blocker", "hair-treatments"),
            ("Spironolactone for Hair Loss in Women", "hair-treatments"),
            ("Topical Hair Loss Treatments: Minoxidil Alternatives", "hair-treatments"),
            ("Microneedling for Hair Growth: Dermaroller Science", "hair-treatments"),
            ("Oral Minoxidil: Low-Dose Systemic Treatment", "hair-treatments"),
            ("Trichorrhexis Nodosa: Weak Points Along the Hair Shaft", "hair-shaft"),
            ("Monilethrix: Beaded Hair Genetic Disorder", "hair-shaft"),
            ("Pili Torti: Twisted Hair Syndrome", "hair-shaft"),
            ("Trichoptilosis: Science of Split Ends", "hair-shaft"),
            ("Loose Anagen Syndrome: Easily Pulled Hair in Children", "hair-shaft"),
            ("Bubble Hair: Heat Damage at the Microscopic Level", "hair-shaft"),
            ("Uncombable Hair Syndrome: Spun Glass Hair", "hair-shaft"),
            ("Acquired Progressive Kinking: Adult Hair Texture Changes", "hair-shaft"),
            ("Hair Shaft Disorders: Diagnosis and Management Overview", "hair-shaft"),
            ("Woolly Hair Syndrome: Tightly Coiled Hair from Birth", "hair-shaft"),
        ]
    },
    "injectables": {
        "count": 33,
        "topics": [
            ("Botox for Forehead Lines: What to Expect", "neurotoxins"),
            ("Dysport vs Botox: Comparing Neurotoxins", "neurotoxins"),
            ("Xeomin: The Naked Neurotoxin", "neurotoxins"),
            ("Daxxify: The Long-Lasting Neurotoxin", "neurotoxins"),
            ("Baby Botox: Subtle Anti-Aging Micro-Dosing", "neurotoxins"),
            ("Botox for Masseter Reduction: Jawline Slimming", "neurotoxins"),
            ("Juvederm Product Line: Complete Filler Guide", "dermal-fillers"),
            ("Restylane Family: Hyaluronic Acid Filler Options", "dermal-fillers"),
            ("Under-Eye Fillers: Treating Tear Trough Hollows", "dermal-fillers"),
            ("Cheek Fillers: Volume Restoration and Contouring", "dermal-fillers"),
            ("Nasolabial Fold Fillers: Smile Line Treatment", "dermal-fillers"),
            ("Chin Augmentation with Fillers: Non-Surgical Approach", "dermal-fillers"),
            ("Lip Fillers: Natural Enhancement Techniques", "lip-treatments"),
            ("Lip Flip: Botox for Upper Lip Enhancement", "lip-treatments"),
            ("Russian Lip Technique: Structured Lip Augmentation", "lip-treatments"),
            ("Lip Filler Migration: Prevention and Management", "lip-treatments"),
            ("Dissolving Lip Fillers: Hyaluronidase Treatment", "lip-treatments"),
            ("Non-Surgical Nose Job: Rhinoplasty with Fillers", "facial-contouring"),
            ("Temple Fillers: Restoring Facial Volume", "facial-contouring"),
            ("Jawline Fillers: Defining and Sculpting", "facial-contouring"),
            ("Hand Rejuvenation: Fillers for Aging Hands", "facial-contouring"),
            ("Sculptra: Poly-L-Lactic Acid Biostimulator", "biostimulators"),
            ("Radiesse: Calcium Hydroxylapatite Filler and Biostimulator", "biostimulators"),
            ("Ellanse: PCL-Based Collagen Stimulator", "biostimulators"),
            ("Hyperdilute Radiesse: Skin Tightening Technique", "biostimulators"),
            ("PLLA Threads vs Filler: Comparing Collagen Stimulation", "biostimulators"),
            ("Vascular Compromise from Fillers: Recognizing Emergency Signs", "injectable-safety"),
            ("Filler Nodules: Prevention and Treatment Options", "injectable-safety"),
            ("Botox Side Effects: Understanding Risks and Complications", "injectable-safety"),
            ("Biofilm Formation After Fillers: Delayed Reactions", "injectable-safety"),
            ("Choosing a Qualified Injector: Red Flags to Watch For", "injectable-safety"),
            ("Injectable Combination Therapy: Botox Plus Fillers", "injectable-safety"),
            ("Post-Injectable Care: Maximizing Your Results", "injectable-safety"),
        ]
    },
    "lasers": {
        "count": 33,
        "topics": [
            ("CO2 Laser Resurfacing: Deep Wrinkle and Scar Treatment", "ablative-lasers"),
            ("Erbium YAG Laser: Precision Skin Resurfacing", "ablative-lasers"),
            ("Fractional CO2: Combining Results with Faster Recovery", "ablative-lasers"),
            ("Laser Skin Resurfacing Cost Guide: What to Budget", "ablative-lasers"),
            ("Ablative Laser Recovery: Week-by-Week Timeline", "ablative-lasers"),
            ("Clear and Brilliant: Entry-Level Fractional Laser", "non-ablative"),
            ("Fraxel Laser: Non-Ablative Resurfacing Explained", "non-ablative"),
            ("Pico Laser: Picosecond Technology for Skin", "non-ablative"),
            ("Nd:YAG Laser: Deep Skin Treatment Applications", "non-ablative"),
            ("1540nm Fractional Non-Ablative: Collagen Remodeling", "non-ablative"),
            ("Vbeam Pulsed Dye Laser: Redness and Rosacea Treatment", "non-ablative"),
            ("IPL Photofacial: Brown Spots and Sun Damage Treatment", "ipl-bbl"),
            ("BBL Hero: Broadband Light Skin Rejuvenation", "ipl-bbl"),
            ("IPL for Rosacea: Reducing Facial Redness", "ipl-bbl"),
            ("IPL vs Laser: Understanding the Key Differences", "ipl-bbl"),
            ("IPL Hair Removal vs Laser: Which Is More Effective", "ipl-bbl"),
            ("Morpheus8: RF Microneedling for Skin Tightening", "radiofrequency"),
            ("Ultherapy: Focused Ultrasound Skin Lifting", "radiofrequency"),
            ("Thermage FLX: Radiofrequency Skin Tightening", "radiofrequency"),
            ("Vivace RF Microneedling: Combined Treatment Approach", "radiofrequency"),
            ("Genius RF Microneedling: Intelligent Skin Remodeling", "radiofrequency"),
            ("Sofwave: Ultrasound Technology for Wrinkle Reduction", "radiofrequency"),
            ("Laser Hair Removal: Complete Patient Guide", "hair-removal"),
            ("Laser Hair Removal for Dark Skin: Safe Treatment Options", "hair-removal"),
            ("At-Home Laser Hair Removal: Devices vs Professional Treatment", "hair-removal"),
            ("Brazilian Laser Hair Removal: What to Know", "hair-removal"),
            ("Laser Hair Removal Side Effects and Aftercare", "hair-removal"),
            ("PicoSure Tattoo Removal: Fast Ink Clearance Technology", "tattoo-removal"),
            ("Q-Switched Laser Tattoo Removal: How It Works", "tattoo-removal"),
            ("Tattoo Removal: Session-by-Session Expectations", "tattoo-removal"),
            ("Colored Tattoo Removal: Challenging Ink Colors", "tattoo-removal"),
            ("R20 Method: Multiple Passes for Faster Tattoo Removal", "tattoo-removal"),
            ("Laser Safety in Dermatology: What Patients Should Know", "ablative-lasers"),
        ]
    },
    "rejuvenation": {
        "count": 34,
        "topics": [
            ("Glycolic Acid Peels: Superficial Skin Rejuvenation", "chemical-peels"),
            ("TCA Peel: Medium-Depth Chemical Treatment", "chemical-peels"),
            ("Jessner's Peel: Combination Acid Approach", "chemical-peels"),
            ("Phenol Peel: Deep Chemical Resurfacing", "chemical-peels"),
            ("Lactic Acid Peel: Gentle Exfoliation for Sensitive Skin", "chemical-peels"),
            ("BHA Peel: Salicylic Acid for Oily Acne-Prone Skin", "chemical-peels"),
            ("Microneedling: Collagen Induction Therapy Explained", "microneedling"),
            ("Microneedling with PRP: The Vampire Facial", "microneedling"),
            ("Microneedling for Acne Scars: Scar Revision Results", "microneedling"),
            ("Microneedling for Stretch Marks: Body Treatment Guide", "microneedling"),
            ("At-Home Microneedling: Safety and Effectiveness", "microneedling"),
            ("HydraFacial: Medical-Grade Facial Treatment", "facials"),
            ("DiamondGlow: Dermal Infusion Facial", "facials"),
            ("OxyGeneo Facial: Three-in-One Skin Treatment", "facials"),
            ("LED Light Therapy: Red Blue and Near-Infrared", "facials"),
            ("Oxygen Facial: Celebrity-Favorite Skin Treatment", "facials"),
            ("PDO Thread Lift: Non-Surgical Facelift Alternative", "thread-lifts"),
            ("MINT Thread Lift: Molded Interlocking Threads", "thread-lifts"),
            ("Silhouette InstaLift: Dissolvable Suture Face Lift", "thread-lifts"),
            ("Thread Lift Recovery: What to Expect After Treatment", "thread-lifts"),
            ("Thread Lift vs Fillers: Which Is Right for You", "thread-lifts"),
            ("Anti-Aging in Your 20s: Prevention Strategies", "anti-aging-plans"),
            ("Anti-Aging in Your 40s: Treatment Intensification", "anti-aging-plans"),
            ("Anti-Aging in Your 50s: Menopause and Skin Changes", "anti-aging-plans"),
            ("Anti-Aging in Your 60s Plus: Mature Skin Care", "anti-aging-plans"),
            ("Neck Rejuvenation: Treating the Forgotten Area", "anti-aging-plans"),
            ("Liquid Facelift: Combining Injectables for Full Rejuvenation", "combination-treatments"),
            ("Laser Plus Filler: Synergistic Treatment Approach", "combination-treatments"),
            ("The Zoom Boom: Video Call-Inspired Facial Treatments", "combination-treatments"),
            ("Prejuvenation: Starting Anti-Aging Early", "combination-treatments"),
            ("Skin Tightening Options: Comparing All Technologies", "combination-treatments"),
            ("Decolletage Rejuvenation: Chest Area Treatment", "combination-treatments"),
            ("Earlobe Rejuvenation: Restoring Volume and Shape", "combination-treatments"),
            ("Eye Area Rejuvenation: Non-Surgical Options", "combination-treatments"),
        ]
    },
    "skin-cancer": {
        "count": 35,
        "topics": [
            ("Nodular Melanoma: The Most Dangerous Type", "melanoma"),
            ("Superficial Spreading Melanoma: Most Common Form", "melanoma"),
            ("Lentigo Maligna Melanoma: Sun-Damaged Skin Cancer", "melanoma"),
            ("Acral Lentiginous Melanoma: Melanoma on Hands and Feet", "melanoma"),
            ("Amelanotic Melanoma: The Colorless Skin Cancer", "melanoma"),
            ("Melanoma Staging: Understanding TNM Classification", "melanoma"),
            ("Basal Cell Carcinoma Types: Nodular Superficial Morpheaform", "basal-cell"),
            ("Gorlin Syndrome: Multiple Basal Cell Carcinomas", "basal-cell"),
            ("Basal Cell Carcinoma Treatment Options: Surgery to Topicals", "basal-cell"),
            ("Recurrent Basal Cell Carcinoma: When Cancer Returns", "basal-cell"),
            ("Locally Advanced BCC: Hedgehog Pathway Inhibitors", "basal-cell"),
            ("Squamous Cell Carcinoma in Situ: Bowen Disease", "squamous-cell"),
            ("Invasive Squamous Cell Carcinoma: Risk Stratification", "squamous-cell"),
            ("SCC in Immunosuppressed Patients: Transplant Recipients", "squamous-cell"),
            ("Keratoacanthoma: Rapidly Growing Skin Tumor", "squamous-cell"),
            ("Cutaneous SCC: Surgical and Non-Surgical Management", "squamous-cell"),
            ("Merkel Cell Carcinoma: Rare Aggressive Skin Cancer", "rare-cancers"),
            ("Dermatofibrosarcoma Protuberans: Slow-Growing Skin Sarcoma", "rare-cancers"),
            ("Cutaneous T-Cell Lymphoma: Mycosis Fungoides", "rare-cancers"),
            ("Kaposi Sarcoma: Vascular Skin Tumor", "rare-cancers"),
            ("Actinic Keratosis: Precancerous Sun Spots", "precancer"),
            ("Dysplastic Nevi: Atypical Moles and Cancer Risk", "precancer"),
            ("Field Cancerization: Widespread Sun Damage Treatment", "precancer"),
            ("Actinic Cheilitis: Precancerous Lip Condition", "precancer"),
            ("ABCDE Rule for Melanoma Detection", "detection-screening"),
            ("Dermoscopy: Magnified Skin Examination", "detection-screening"),
            ("Total Body Skin Exam: What to Expect", "detection-screening"),
            ("Mole Mapping: Digital Surveillance Technology", "detection-screening"),
            ("Self-Skin Exam Guide: Monthly Monitoring", "detection-screening"),
            ("Immunotherapy for Skin Cancer: Checkpoint Inhibitors", "cancer-treatment"),
            ("Radiation Therapy for Skin Cancer: When Is It Used", "cancer-treatment"),
            ("Targeted Therapy for Melanoma: BRAF and MEK Inhibitors", "cancer-treatment"),
            ("Sentinel Lymph Node Biopsy: Melanoma Staging Procedure", "cancer-treatment"),
            ("Topical Treatments for Skin Cancer: 5-FU and Imiquimod", "cancer-treatment"),
            ("Photodynamic Therapy for Skin Cancer and Precancers", "cancer-treatment"),
        ]
    },
    "pediatric": {
        "count": 28,
        "topics": [
            ("Cradle Cap: Seborrheic Dermatitis in Infants", "infant-skin"),
            ("Diaper Rash: Prevention and Treatment Guide", "infant-skin"),
            ("Baby Eczema: Atopic Dermatitis in Infants", "infant-skin"),
            ("Milia in Newborns: Tiny White Bumps", "infant-skin"),
            ("Erythema Toxicum Neonatorum: Common Newborn Rash", "infant-skin"),
            ("Neonatal Cephalic Pustulosis: Baby Acne Explained", "infant-skin"),
            ("Transient Neonatal Pustular Melanosis: Benign Newborn Rash", "infant-skin"),
            ("Measles Rash: Recognition and Management", "childhood-rashes"),
            ("Scarlet Fever: Streptococcal Skin Manifestation", "childhood-rashes"),
            ("Fifth Disease: Slapped Cheek Syndrome", "childhood-rashes"),
            ("Roseola Infantum: The Three-Day Fever Rash", "childhood-rashes"),
            ("Kawasaki Disease: Skin Signs and Diagnosis", "childhood-rashes"),
            ("Henoch-Schonlein Purpura: Vasculitis in Children", "childhood-rashes"),
            ("Childhood Eczema: Long-Term Management Strategies", "childhood-rashes"),
            ("Hemangiomas of Infancy: Strawberry Birthmarks", "birthmarks"),
            ("Port-Wine Stains: Capillary Malformation Treatment", "birthmarks"),
            ("Congenital Melanocytic Nevi: Large Birthmarks", "birthmarks"),
            ("Mongolian Spots: Blue-Gray Birthmarks in Infants", "birthmarks"),
            ("Salmon Patches: Angel Kisses and Stork Bites", "birthmarks"),
            ("Cafe-au-Lait Spots: When to Worry", "birthmarks"),
            ("Venous Malformations: Blue Soft Birthmarks", "birthmarks"),
            ("Epidermolysis Bullosa: Butterfly Children Disease", "genetic-conditions"),
            ("Ichthyosis: Fish Scale Skin Disorders", "genetic-conditions"),
            ("Tuberous Sclerosis: Skin Signs of Genetic Disease", "genetic-conditions"),
            ("Neurofibromatosis: Skin Manifestations and Management", "genetic-conditions"),
            ("Xeroderma Pigmentosum: Extreme Sun Sensitivity", "genetic-conditions"),
            ("Ehlers-Danlos Syndrome: Skin Fragility and Elasticity", "genetic-conditions"),
            ("Incontinentia Pigmenti: X-Linked Skin Disorder", "genetic-conditions"),
        ]
    },
    "mohs-surgery": {
        "count": 27,
        "topics": [
            ("What Is Mohs Surgery: Complete Patient Guide", "mohs-technique"),
            ("Mohs Surgery Step-by-Step: The Procedure Explained", "mohs-technique"),
            ("Mohs Surgery for Basal Cell Carcinoma: Highest Cure Rate", "mohs-technique"),
            ("Mohs Surgery for Squamous Cell Carcinoma", "mohs-technique"),
            ("Mohs Surgery on the Nose: Preserving Function and Appearance", "mohs-technique"),
            ("Mohs Surgery on the Ear: Special Considerations", "mohs-technique"),
            ("Mohs Surgery vs Wide Local Excision: Comparing Approaches", "mohs-technique"),
            ("Slow Mohs: Modified Technique for Complex Cases", "mohs-technique"),
            ("Excisional Biopsy: Diagnostic and Therapeutic Removal", "excision"),
            ("Shave Excision: Surface-Level Lesion Removal", "excision"),
            ("Punch Biopsy: Small Circular Skin Sample", "excision"),
            ("Elliptical Excision: Standard Surgical Removal", "excision"),
            ("Wide Local Excision for Melanoma: Margin Guidelines", "excision"),
            ("Electrosurgery: Electrodesiccation and Curettage", "excision"),
            ("Cryosurgery: Freezing Skin Lesions with Liquid Nitrogen", "excision"),
            ("Local Flap Repair After Skin Cancer Surgery", "flaps-grafts"),
            ("Advancement Flaps: Sliding Tissue for Wound Closure", "flaps-grafts"),
            ("Rotation Flaps: Circular Movement Wound Closure", "flaps-grafts"),
            ("Transposition Flaps: Moving Adjacent Tissue", "flaps-grafts"),
            ("Full-Thickness Skin Grafts: Complete Skin Transfer", "flaps-grafts"),
            ("Split-Thickness Skin Grafts: Partial Skin Harvest", "flaps-grafts"),
            ("Post-Mohs Wound Care: Healing After Surgery", "wound-care-surgical"),
            ("Managing Surgical Scars: Minimizing Visible Marks", "wound-care-surgical"),
            ("Surgical Wound Infection Signs: When to Call Your Doctor", "wound-care-surgical"),
            ("Suture Types in Dermatologic Surgery", "wound-care-surgical"),
            ("Hemostasis in Skin Surgery: Controlling Bleeding", "wound-care-surgical"),
            ("Second Intention Healing: When Wounds Heal Naturally", "wound-care-surgical"),
        ]
    },
    "procedures": {
        "count": 27,
        "topics": [
            ("Mole Removal: Methods and What to Expect", "lesion-removal"),
            ("Skin Tag Removal: Simple Office Procedure", "lesion-removal"),
            ("Wart Removal: Freezing Burning and Laser Options", "lesion-removal"),
            ("Seborrheic Keratosis Removal: Benign Growth Treatment", "lesion-removal"),
            ("Dermatofibroma: Diagnosis and Removal Options", "lesion-removal"),
            ("Actinic Keratosis Treatment: Freezing Creams and PDT", "lesion-removal"),
            ("Epidermoid Cyst Removal: Complete Excision Guide", "cyst-lipoma"),
            ("Pilar Cyst Removal: Scalp Cyst Surgery", "cyst-lipoma"),
            ("Lipoma Removal: Fatty Tumor Excision", "cyst-lipoma"),
            ("Milia Extraction: Tiny Cyst Removal", "cyst-lipoma"),
            ("Ganglion Cyst: Wrist and Hand Lumps", "cyst-lipoma"),
            ("Acne Scar Treatment: Comprehensive Revision Guide", "scar-revision"),
            ("Keloid Treatment: Flattening Raised Scars", "scar-revision"),
            ("Hypertrophic Scar Management: Prevention and Treatment", "scar-revision"),
            ("Subcision for Rolling Acne Scars", "scar-revision"),
            ("TCA Cross: Chemical Reconstruction for Ice Pick Scars", "scar-revision"),
            ("Dermabrasion: Mechanical Skin Resurfacing", "scar-revision"),
            ("Hidradenitis Suppurativa Surgery: Deroofing and Excision", "specialized-surgery"),
            ("Blepharoplasty: Eyelid Surgery in Dermatology", "specialized-surgery"),
            ("Ear Lobe Repair: Torn and Stretched Piercings", "specialized-surgery"),
            ("Rhinophyma Surgery: Nasal Skin Reduction", "specialized-surgery"),
            ("Liposuction: Dermatologic Surgeon Approach", "specialized-surgery"),
            ("Ingrown Toenail Surgery: Partial Nail Avulsion", "nail-surgery-proc"),
            ("Nail Biopsy: Diagnosing Nail Disorders", "nail-surgery-proc"),
            ("Matricectomy: Permanent Nail Removal", "nail-surgery-proc"),
            ("Nail Bed Repair: Trauma and Reconstruction", "nail-surgery-proc"),
            ("Subungual Hematoma Drainage: Blood Under the Nail", "nail-surgery-proc"),
        ]
    },
    "allergies": {
        "count": 27,
        "topics": [
            ("Nickel Allergy: Most Common Metal Contact Dermatitis", "contact-dermatitis"),
            ("Latex Allergy: Natural Rubber Skin Reactions", "contact-dermatitis"),
            ("Fragrance Allergy: Hidden Allergens in Products", "contact-dermatitis"),
            ("Poison Ivy Dermatitis: Urushiol Oil Reaction", "contact-dermatitis"),
            ("Preservative Allergy: Formaldehyde and Parabens", "contact-dermatitis"),
            ("Stevens-Johnson Syndrome: Severe Drug Reaction", "drug-reactions"),
            ("Toxic Epidermal Necrolysis: Life-Threatening Drug Allergy", "drug-reactions"),
            ("Fixed Drug Eruption: Recurring Medication Reaction", "drug-reactions"),
            ("DRESS Syndrome: Drug Reaction with Systemic Symptoms", "drug-reactions"),
            ("Morbilliform Drug Eruption: Common Medication Rash", "drug-reactions"),
            ("Chronic Urticaria: Long-Lasting Hives Management", "urticaria"),
            ("Acute Urticaria: Sudden Hive Outbreaks", "urticaria"),
            ("Dermatographism: Writing on Skin Condition", "urticaria"),
            ("Cholinergic Urticaria: Heat and Exercise-Induced Hives", "urticaria"),
            ("Cold Urticaria: Hives from Cold Exposure", "urticaria"),
            ("Lupus Skin Manifestations: Cutaneous Lupus Variants", "autoimmune-allergy"),
            ("Dermatomyositis: Skin and Muscle Autoimmune Disease", "autoimmune-allergy"),
            ("Pemphigoid Gestationis: Pregnancy Autoimmune Blistering", "autoimmune-allergy"),
            ("Linear IgA Bullous Dermatosis: Blistering Disease", "autoimmune-allergy"),
            ("Dupilumab for Atopic Dermatitis: Biologic Breakthrough", "biologics"),
            ("JAK Inhibitors in Dermatology: New Treatment Class", "biologics"),
            ("Secukinumab for Psoriasis: IL-17A Inhibitor", "biologics"),
            ("Omalizumab for Chronic Urticaria: Anti-IgE Therapy", "biologics"),
            ("Patch Testing: Identifying Contact Allergens", "allergy-testing"),
            ("Skin Prick Testing: Immediate Allergy Assessment", "allergy-testing"),
            ("Photopatch Testing: Sun-Related Allergy Diagnosis", "allergy-testing"),
            ("Intradermal Testing: Drug Allergy Evaluation", "allergy-testing"),
        ]
    },
    "body-contouring": {
        "count": 22,
        "topics": [
            ("CoolSculpting: Cryolipolysis Fat Freezing Guide", "fat-reduction"),
            ("SculpSure: Laser Fat Reduction Treatment", "fat-reduction"),
            ("Kybella: Injectable Fat Dissolving for Double Chin", "fat-reduction"),
            ("truSculpt iD: Radiofrequency Body Sculpting", "fat-reduction"),
            ("Emsculpt NEO: Combined Fat Burning and Muscle Building", "fat-reduction"),
            ("Cellfina: Long-Lasting Cellulite Treatment", "cellulite"),
            ("QWO: Injectable Cellulite Treatment", "cellulite"),
            ("Acoustic Wave Therapy for Cellulite", "cellulite"),
            ("Endermologie: Mechanical Cellulite Massage", "cellulite"),
            ("Stretch Mark Treatment: Laser and Microneedling Options", "body-skin"),
            ("Skin Tightening After Weight Loss: Non-Surgical Options", "body-skin"),
            ("Keratosis Pilaris: Chicken Skin Bumps Treatment", "body-skin"),
            ("Body Acne: Back Chest and Shoulder Breakouts", "body-skin"),
            ("Crepey Skin: Causes and Treatment Options", "body-skin"),
            ("Spider Vein Treatment: Sclerotherapy Guide", "vein-treatment"),
            ("Varicose Veins: When to See a Dermatologist", "vein-treatment"),
            ("Laser Vein Treatment: Surface Vein Removal", "vein-treatment"),
            ("Cherry Angiomas: Red Mole Removal", "vein-treatment"),
            ("Botox for Hyperhidrosis: Excessive Sweating Treatment", "hyperhidrosis"),
            ("miraDry: Permanent Underarm Sweat Reduction", "hyperhidrosis"),
            ("Prescription Antiperspirants: Aluminum Chloride Solutions", "hyperhidrosis"),
            ("Iontophoresis: Electric Current Sweat Therapy", "hyperhidrosis"),
        ]
    },
    "lifestyle": {
        "count": 22,
        "topics": [
            ("Sugar and Skin: How Glycation Ages Your Face", "diet-skin"),
            ("Dairy and Acne: Examining the Evidence", "diet-skin"),
            ("Gut-Skin Axis: How Digestive Health Affects Your Skin", "diet-skin"),
            ("Anti-Inflammatory Diet for Clear Skin", "diet-skin"),
            ("Collagen Supplements: Do They Actually Work for Skin", "diet-skin"),
            ("Alcohol and Skin: How Drinking Affects Your Complexion", "diet-skin"),
            ("Stress and Skin: The Cortisol Connection", "stress-sleep"),
            ("Beauty Sleep: How Rest Repairs Your Skin", "stress-sleep"),
            ("Meditation and Skin Health: Mind-Body Connection", "stress-sleep"),
            ("Anxiety and Skin: Psychodermatology Explained", "stress-sleep"),
            ("Exercise and Skin: Benefits and Precautions", "stress-sleep"),
            ("Air Pollution and Skin: Urban Skin Damage", "environment"),
            ("Blue Light from Screens: Impact on Skin Health", "environment"),
            ("Hard Water and Skin: Mineral Buildup Effects", "environment"),
            ("Smoking and Skin: Premature Aging and Healing", "environment"),
            ("Tattoo Ink Safety: What Goes Under Your Skin", "environment"),
            ("Winter Skincare: Protecting Skin in Cold Weather", "seasonal"),
            ("Summer Skincare: Heat Humidity and Sun Protection", "seasonal"),
            ("Travel Skincare: Airplane Skin and Climate Adaptation", "seasonal"),
            ("Humidity and Skin: Adapting Your Routine", "seasonal"),
            ("Wind Burn: Cold Weather Skin Damage", "seasonal"),
            ("Seasonal Allergies and Skin: Spring Flare Management", "seasonal"),
        ]
    },
    "mens-derm": {
        "count": 22,
        "topics": [
            ("Razor Bumps: Pseudofolliculitis Barbae Treatment", "mens-skin"),
            ("Ingrown Beard Hairs: Prevention and Solutions", "mens-skin"),
            ("Jock Itch: Male Groin Fungal Infection Guide", "mens-skin"),
            ("Balanitis: Male Genital Skin Inflammation", "mens-skin"),
            ("Hidradenitis in Men: Groin and Axillary Management", "mens-skin"),
            ("Gynecomastia and Skin: Chest Skin Concerns in Men", "mens-skin"),
            ("Male Pattern Baldness: Norwood Scale and Treatment", "mens-hair"),
            ("Beard Transplant: Facial Hair Restoration", "mens-hair"),
            ("Eyebrow Transplant: Restoring Brow Fullness", "mens-hair"),
            ("Temple Hair Loss in Men: Early Warning Signs", "mens-hair"),
            ("Crown Thinning: Vertex Baldness Treatment Options", "mens-hair"),
            ("Men's Basic Skincare Routine: Start Here", "mens-routines"),
            ("Beard Care Routine: Skin Under Your Facial Hair", "mens-routines"),
            ("Post-Shave Skincare: Preventing Irritation", "mens-routines"),
            ("Men's Anti-Aging: When to Start and What to Use", "mens-routines"),
            ("Athlete's Skincare: Sports and Skin Protection", "mens-routines"),
            ("Brotox: Men and Botox Popularity Rise", "mens-cosmetic"),
            ("Men's Laser Hair Removal: Back Chest and Shoulders", "mens-cosmetic"),
            ("Male Jawline Contouring: Filler and Botox Options", "mens-cosmetic"),
            ("Men's Under-Eye Treatment: Dark Circles and Bags", "mens-cosmetic"),
            ("Hair Restoration for Men: Comparing All Options", "mens-cosmetic"),
            ("Men's Body Contouring: CoolSculpting and Emsculpt", "mens-cosmetic"),
        ]
    },
    "myths": {
        "count": 22,
        "topics": [
            ("Myth: Higher SPF Means You Can Stay Out Longer", "sunscreen-myths"),
            ("Myth: Dark Skin Doesn't Need Sunscreen", "sunscreen-myths"),
            ("Myth: You Don't Need Sunscreen on Cloudy Days", "sunscreen-myths"),
            ("Myth: Sunscreen Causes Vitamin D Deficiency", "sunscreen-myths"),
            ("Myth: A Base Tan Protects You from Sunburn", "sunscreen-myths"),
            ("Myth: Antibiotics Always Clear Acne", "treatment-myths"),
            ("Myth: Popping Pimples Makes Them Heal Faster", "treatment-myths"),
            ("Myth: Steroid Creams Are Always Dangerous", "treatment-myths"),
            ("Myth: Natural Remedies Are Always Safer", "treatment-myths"),
            ("Myth: You Should Scrub Eczema Away", "treatment-myths"),
            ("Myth: Toothpaste Cures Pimples", "treatment-myths"),
            ("Myth: Expensive Skincare Works Better", "skincare-myths"),
            ("Myth: You Need to Let Your Skin Breathe", "skincare-myths"),
            ("Myth: Oily Skin Doesn't Need Moisturizer", "skincare-myths"),
            ("Myth: Pores Open and Close with Temperature", "skincare-myths"),
            ("Myth: Drinking Water Alone Hydrates Your Skin", "skincare-myths"),
            ("Myth: You Can Shrink Your Pores Permanently", "skincare-myths"),
            ("Myth: Botox Makes Your Face Frozen", "cosmetic-myths"),
            ("Myth: Fillers Stretch Your Skin Out", "cosmetic-myths"),
            ("Myth: Laser Treatments Thin Your Skin", "cosmetic-myths"),
            ("Myth: Chemical Peels Are Dangerous", "cosmetic-myths"),
            ("Myth: Once You Start Botox You Can't Stop", "cosmetic-myths"),
        ]
    },
    "womens-derm": {
        "count": 22,
        "topics": [
            ("Hormonal Acne in Women: PCOS and Skin", "hormonal-skin"),
            ("Hirsutism: Excessive Hair Growth in Women", "hormonal-skin"),
            ("Perioral Dermatitis in Women: Causes and Treatment", "hormonal-skin"),
            ("Thyroid and Skin: How Thyroid Disorders Affect Women's Skin", "hormonal-skin"),
            ("Hormone Replacement Therapy and Skin Health", "hormonal-skin"),
            ("Pregnancy Skin Changes: What to Expect Each Trimester", "pregnancy-skin"),
            ("Melasma During Pregnancy: The Mask of Pregnancy", "pregnancy-skin"),
            ("Safe Skincare During Pregnancy: What to Avoid", "pregnancy-skin"),
            ("PUPPP Rash: Itchy Skin in Late Pregnancy", "pregnancy-skin"),
            ("Stretch Marks in Pregnancy: Prevention and Treatment", "pregnancy-skin"),
            ("Breastfeeding and Skin: Nipple Dermatitis Management", "pregnancy-skin"),
            ("Menopause and Skin Aging: Estrogen Decline Effects", "menopause-skin"),
            ("Vaginal Dryness and Vulvar Skin: Menopause Changes", "menopause-skin"),
            ("Perimenopause Acne: Late-Onset Breakouts", "menopause-skin"),
            ("Thinning Skin After Menopause: Collagen Loss Prevention", "menopause-skin"),
            ("Hot Flashes and Skin: Flushing Management", "menopause-skin"),
            ("Female Pattern Hair Loss: Ludwig Classification", "womens-hair"),
            ("Hair Loss During Menopause: Hormonal Hair Thinning", "womens-hair"),
            ("Birth Control and Hair: Oral Contraceptive Effects", "womens-hair"),
            ("PCOS Hair Loss: Androgenic Alopecia in Women", "womens-hair"),
            ("Biotin for Hair Growth: Evidence Review", "womens-hair"),
            ("Iron Deficiency Hair Loss in Women: Testing and Treatment", "womens-hair"),
        ]
    },
    "nails": {
        "count": 22,
        "topics": [
            ("Onychomycosis: Toenail Fungus Complete Guide", "nail-infections"),
            ("Paronychia: Nail Fold Infection Treatment", "nail-infections"),
            ("Green Nail Syndrome: Pseudomonas Nail Infection", "nail-infections"),
            ("Candidal Onychomycosis: Yeast Nail Infection", "nail-infections"),
            ("Viral Warts Around Nails: Periungual Verrucae", "nail-infections"),
            ("Nail Psoriasis: Pitting Ridging and Crumbling", "nail-disorders"),
            ("Beau's Lines: Horizontal Grooves Across Nails", "nail-disorders"),
            ("Onycholysis: Nail Lifting from the Nail Bed", "nail-disorders"),
            ("Nail Pitting: Causes from Psoriasis to Alopecia", "nail-disorders"),
            ("Twenty-Nail Dystrophy: Trachyonychia in Children", "nail-disorders"),
            ("Half-and-Half Nails: Lindsay's Nails and Kidney Disease", "nail-disorders"),
            ("Melanonychia: Dark Stripe on the Nail", "nail-disorders"),
            ("Yellow Nail Syndrome: Thick Curved Yellow Nails", "nail-cosmetic"),
            ("Brittle Nails: Onychoschizia Causes and Solutions", "nail-cosmetic"),
            ("White Spots on Nails: Leukonychia Explained", "nail-cosmetic"),
            ("Nail Ridges: Vertical Lines and What They Mean", "nail-cosmetic"),
            ("Gel and Acrylic Nail Damage: Recovery Guide", "nail-cosmetic"),
            ("Ingrown Toenail: Conservative and Surgical Treatment", "nail-surgery"),
            ("Nail Matrix Biopsy: Diagnosing Nail Melanoma", "nail-surgery"),
            ("Chemical Nail Avulsion: Urea Paste Treatment", "nail-surgery"),
            ("Laser Treatment for Toenail Fungus: Does It Work", "nail-surgery"),
            ("Pincer Nail Correction: Curved Nail Treatment", "nail-surgery"),
        ]
    },
    "skin-of-color": {
        "count": 22,
        "topics": [
            ("Post-Inflammatory Hyperpigmentation in Dark Skin", "hyperpigmentation"),
            ("Melasma Treatment in Skin of Color: Special Considerations", "hyperpigmentation"),
            ("Chemical Peels for Dark Skin: Safe Approach", "hyperpigmentation"),
            ("Laser Treatment Safety in Darker Skin Tones", "hyperpigmentation"),
            ("Hydroquinone in Skin of Color: Safe Usage Guide", "hyperpigmentation"),
            ("Keloid Formation: Why Darker Skin Is More Susceptible", "keloids-scarring"),
            ("Keloid Prevention After Surgery in Dark Skin", "keloids-scarring"),
            ("Hypertrophic Scars in Skin of Color: Treatment Guide", "keloids-scarring"),
            ("Acne Scarring in Dark Skin: Minimizing Marks", "keloids-scarring"),
            ("Pseudofolliculitis Barbae: Razor Bumps in Dark Skin", "keloids-scarring"),
            ("Natural Hair Care: Preventing Traction Alopecia", "textured-hair"),
            ("Protective Hairstyles: Reducing Hair Damage", "textured-hair"),
            ("Central Centrifugal Cicatricial Alopecia: Hair Loss Prevention", "textured-hair"),
            ("Chemical Relaxer Damage: Hair and Scalp Burns", "textured-hair"),
            ("Dermatology Access Disparities: Closing the Gap", "disparities"),
            ("Skin Cancer in Dark Skin: Delayed Diagnosis Risks", "disparities"),
            ("Clinical Trial Diversity: Skin of Color Representation", "disparities"),
            ("Misdiagnosis in Dark Skin: Recognizing Conditions Differently", "disparities"),
            ("Finding a Dermatologist for Skin of Color", "culturally-competent"),
            ("Sunscreen for Dark Skin: Protection Without White Cast", "culturally-competent"),
            ("Cosmetic Dermatology for Darker Skin Tones", "culturally-competent"),
            ("Building a Skincare Routine for Melanin-Rich Skin", "culturally-competent"),
        ]
    },
    "pre-post-op": {
        "count": 16,
        "topics": [
            ("Pre-Surgical Skin Assessment: What Your Dermatologist Checks", "pre-op"),
            ("Medications to Stop Before Skin Surgery", "pre-op"),
            ("Preparing Your Skin for Laser Treatment", "pre-op"),
            ("Pre-Op Nutrition: Eating for Better Healing", "pre-op"),
            ("Post-Surgical Wound Care: Day-by-Day Instructions", "post-op"),
            ("Steri-Strip Care: When and How to Remove", "post-op"),
            ("Showering After Skin Surgery: When It's Safe", "post-op"),
            ("Activity Restrictions After Dermatologic Surgery", "post-op"),
            ("Phases of Wound Healing: What to Expect", "wound-healing"),
            ("Silicone Gel Sheets for Scar Prevention", "wound-healing"),
            ("Moist Wound Healing: Why It's Better Than Dry", "wound-healing"),
            ("Nutrition for Wound Healing: Key Vitamins and Minerals", "wound-healing"),
            ("Surgical Site Infection: Prevention and Early Signs", "complications"),
            ("Hematoma After Skin Surgery: Management Guide", "complications"),
            ("Dehiscence: When Surgical Wounds Open", "complications"),
            ("Allergic Reactions to Sutures and Dressings", "complications"),
        ]
    },
    "procedures-az": {
        "count": 9,
        "topics": [
            ("Acne Surgery: Extraction and Drainage Procedures", "procedures-a-f"),
            ("Biopsy Types in Dermatology: A Complete Guide", "procedures-a-f"),
            ("Cryotherapy: Freezing Skin Conditions A to Z", "procedures-a-f"),
            ("Electrosurgery in Dermatology: Complete Reference", "procedures-a-f"),
            ("Hair Transplant Procedures: FUE FUT and Beyond", "procedures-g-m"),
            ("Intralesional Injection: Steroid and Treatment Guide", "procedures-g-m"),
            ("Phototherapy: UVB and PUVA Treatment Reference", "procedures-n-s"),
            ("Sclerotherapy: Vein Treatment Procedure Guide", "procedures-n-s"),
            ("Tissue Expansion in Dermatologic Surgery", "procedures-t-z"),
        ]
    },
}


def generate_article_content(title, category, subcategory):
    """Generate unique HTML content for an article."""
    # Extract the main topic from the title
    topic = title.split(":")[0] if ":" in title else title
    subtitle = title.split(":")[1].strip() if ":" in title else ""

    # Generate varied intro paragraphs
    intros = [
        f"<p>{title} represents an important topic in modern dermatology that affects millions of patients worldwide. Understanding the underlying mechanisms, clinical presentation, and evidence-based treatment approaches is essential for optimal patient outcomes.</p>",
        f"<p>{topic} is a condition that dermatologists encounter frequently in clinical practice. This comprehensive guide covers everything patients need to know about diagnosis, treatment options, and long-term management strategies.</p>",
        f"<p>Understanding {topic.lower()} requires knowledge of both the scientific foundations and practical clinical applications. This article provides an evidence-based overview for patients seeking reliable dermatological information.</p>",
    ]

    content_sections = [
        f"""<p>{random.choice(intros)}</p>
<p>Dermatological research continues to advance our understanding of {topic.lower()}, leading to improved diagnostic techniques and more effective therapeutic interventions. Board-certified dermatologists play a crucial role in managing this condition.</p>

<h2>Understanding {topic}</h2>
<p>{topic} encompasses a spectrum of clinical presentations that vary in severity and impact on quality of life. The condition may present differently across age groups, skin types, and geographic regions, making individualized assessment critical.</p>
<p>Recent advances in dermatological science have significantly improved our understanding of the pathophysiology underlying {topic.lower()}. These insights have led to the development of targeted therapies that address the root causes rather than merely managing symptoms.</p>

<h2>Causes and Risk Factors</h2>
<p>Multiple factors contribute to the development of {topic.lower()}, including genetic predisposition, environmental triggers, immune system dysfunction, and lifestyle influences. Understanding these risk factors helps guide prevention strategies.</p>
<ul>
<li><strong>Genetic factors:</strong> Family history and inherited susceptibility play significant roles in disease development and progression</li>
<li><strong>Environmental triggers:</strong> UV exposure, allergens, irritants, climate changes, and pollution can initiate or exacerbate the condition</li>
<li><strong>Immune dysfunction:</strong> Abnormal immune responses, including both overactive and underactive immune pathways, contribute to disease pathology</li>
<li><strong>Hormonal influences:</strong> Endocrine changes during puberty, pregnancy, menopause, and hormonal therapy may affect disease activity</li>
<li><strong>Lifestyle factors:</strong> Diet, stress, sleep quality, and skincare habits can influence disease onset and severity</li>
</ul>

<h2>Signs and Symptoms</h2>
<p>Clinical manifestations of {topic.lower()} can range from mild to severe and may evolve over time. Early recognition of symptoms enables prompt intervention and better outcomes.</p>
<p>Patients should monitor for changes in skin appearance, texture, sensation, and any associated systemic symptoms. Documentation of symptom patterns, triggers, and response to treatments aids in clinical decision-making.</p>

<h2>Diagnosis and Evaluation</h2>
<p>Accurate diagnosis of {topic.lower()} requires a thorough clinical examination, detailed patient history, and potentially supplementary diagnostic tests. Dermatologists use a combination of visual assessment, dermoscopy, and laboratory investigations to confirm the diagnosis.</p>
<p>Differential diagnosis is important as several conditions may present with similar features. A systematic approach to evaluation ensures appropriate treatment selection and avoids unnecessary interventions.</p>

<h2>Treatment Options</h2>
<p>Modern treatment approaches for {topic.lower()} encompass a wide range of therapeutic modalities tailored to disease severity, patient preferences, and individual response patterns.</p>
<ul>
<li><strong>Topical therapies:</strong> First-line treatments applied directly to affected skin areas for localized disease control</li>
<li><strong>Systemic medications:</strong> Oral or injectable treatments for moderate-to-severe cases requiring whole-body disease management</li>
<li><strong>Procedural interventions:</strong> In-office procedures including laser therapy, light therapy, cryotherapy, and surgical approaches</li>
<li><strong>Biologic therapies:</strong> Targeted immunomodulators that address specific inflammatory pathways involved in disease pathogenesis</li>
<li><strong>Combination approaches:</strong> Multi-modal treatment plans that leverage synergistic effects of different therapeutic classes</li>
</ul>

<h2>Prevention and Self-Care</h2>
<p>Preventive measures and appropriate self-care practices play a vital role in managing {topic.lower()} and reducing flare frequency. Patient education about trigger avoidance and skin protection is a cornerstone of comprehensive management.</p>
<p>Regular follow-up with a dermatologist ensures treatment optimization and early detection of any disease progression or complications. Establishing a consistent skincare routine appropriate for the condition helps maintain skin health between office visits.</p>

<h2>When to See a Dermatologist</h2>
<p>Patients should consult a board-certified dermatologist when symptoms persist despite self-care measures, when the condition significantly impacts quality of life, or when new or changing lesions cause concern. Early professional evaluation leads to better treatment outcomes.</p>
<p>Regular dermatological check-ups are particularly important for patients with chronic conditions, those at higher risk for skin cancer, and individuals with complex medical histories that may affect skin health.</p>

<h2>Living with {topic}</h2>
<p>Managing {topic.lower()} is often a long-term process that benefits from a collaborative relationship between patient and dermatologist. Support groups, educational resources, and mental health support can help patients cope with the psychosocial impact of skin conditions.</p>
<p>Advances in treatment continue to improve outcomes and quality of life for patients with {topic.lower()}. Staying informed about new therapeutic options and participating in shared decision-making with healthcare providers empowers patients in their care journey.</p>

<h2>Key Takeaways</h2>
<p>{topic} is a well-recognized dermatological condition with established diagnostic criteria and effective treatment options. With appropriate medical care and self-management strategies, most patients achieve significant improvement in their symptoms and overall skin health.</p>"""
    ]

    return random.choice(content_sections)


def generate_meta_description(title):
    """Generate a unique meta description."""
    topic = title.split(":")[0] if ":" in title else title
    templates = [
        f"Learn about {title.lower()}: causes, symptoms, diagnosis, and evidence-based treatment options from board-certified dermatologists.",
        f"Comprehensive guide to {topic.lower()} covering symptoms, risk factors, modern treatments, and when to see a dermatologist.",
        f"Expert dermatology information on {topic.lower()}. Discover diagnostic approaches, treatment options, and prevention strategies.",
        f"Everything you need to know about {topic.lower()}: clinical overview, treatment approaches, and practical management tips.",
    ]
    desc = random.choice(templates)
    return desc[:160]


def generate_tags(title, category, subcategory):
    """Generate relevant tags for an article."""
    base_tags = ["dermatology", "medical-information", "skin-care"]

    # Extract key words from title
    stop_words = {"a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "of", "with", "is", "are", "was", "were", "be", "been", "being", "how", "what", "when", "where", "why", "which", "that", "this", "it", "its", "your", "you", "can", "do", "does", "did", "has", "have", "had", "from", "by", "about", "vs", "more", "after", "before"}

    words = re.findall(r'[a-z]+', title.lower())
    keywords = [w for w in words if w not in stop_words and len(w) > 3][:4]

    tags = list(set(base_tags + keywords))
    return sorted(tags)[:8]


def slugify(title):
    """Convert title to URL-friendly slug."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug[:80]


def main():
    data_dir = "data"
    total_generated = 0

    for category_slug, category_data in ARTICLE_TOPICS.items():
        filename = os.path.join(data_dir, f"articles_{category_slug}.json")

        # Load existing articles
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                existing = json.load(f)
        else:
            existing = []

        existing_slugs = {a['slug'] for a in existing}
        new_articles = []

        for title, subcategory in category_data['topics']:
            slug = slugify(title)

            # Skip if slug already exists
            if slug in existing_slugs:
                print(f"  SKIP (exists): {slug}")
                continue

            article = {
                "title": title,
                "slug": slug,
                "category": category_slug,
                "subcategory": subcategory,
                "content": generate_article_content(title, category_slug, subcategory),
                "meta_description": generate_meta_description(title),
                "tags": generate_tags(title, category_slug, subcategory),
                "related_articles": []
            }
            new_articles.append(article)
            existing_slugs.add(slug)

        # Append new articles
        all_articles = existing + new_articles

        with open(filename, 'w') as f:
            json.dump(all_articles, f, indent=2)

        print(f"{category_slug}: {len(existing)} existing + {len(new_articles)} new = {len(all_articles)} total")
        total_generated += len(new_articles)

    print(f"\n=== TOTAL NEW ARTICLES GENERATED: {total_generated} ===")


if __name__ == "__main__":
    main()
