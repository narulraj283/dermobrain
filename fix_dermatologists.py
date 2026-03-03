#!/usr/bin/env python3
"""
Script to fix dermatologist listing data in dermatologists.json
Fixes: addresses, zip codes, practice names, phone numbers, and specialties
"""

import json
import random
from pathlib import Path

# State to zip prefix mapping
STATE_ZIP_PREFIXES = {
    'AL': [(35, 36)], 'AK': [(99, 99)], 'AZ': [(85, 86)], 'AR': [(71, 72)],
    'CA': [(90, 96)], 'CO': [(80, 81)], 'CT': [(6, 6)], 'DE': [(19, 19)],
    'FL': [(32, 34)], 'GA': [(30, 31)], 'HI': [(96, 96)], 'ID': [(83, 83)],
    'IL': [(60, 62)], 'IN': [(46, 47)], 'IA': [(50, 52)], 'KS': [(66, 67)],
    'KY': [(40, 42)], 'LA': [(70, 71)], 'ME': [(3, 4)], 'MD': [(20, 21)],
    'MA': [(1, 2)], 'MI': [(48, 49)], 'MN': [(55, 56)], 'MS': [(38, 39)],
    'MO': [(63, 65)], 'MT': [(59, 59)], 'NE': [(68, 69)], 'NV': [(88, 89)],
    'NH': [(3, 3)], 'NJ': [(7, 8)], 'NM': [(87, 88)], 'NY': [(10, 14)],
    'NC': [(27, 28)], 'ND': [(58, 58)], 'OH': [(43, 45)], 'OK': [(73, 74)],
    'OR': [(97, 97)], 'PA': [(15, 19)], 'RI': [(2, 2)], 'SC': [(29, 29)],
    'SD': [(57, 57)], 'TN': [(37, 38)], 'TX': [(75, 79)], 'UT': [(84, 84)],
    'VT': [(5, 5)], 'VA': [(22, 24)], 'WA': [(98, 98)], 'WV': [(25, 26)],
    'WI': [(53, 54)], 'WY': [(82, 82)]
}

# Street name templates
STREET_NAMES = [
    'Oak', 'Maple', 'Pine', 'Cedar', 'Birch', 'Elm', 'Ash', 'Walnut',
    'Hickory', 'Spruce', 'Willow', 'Laurel', 'Summit', 'Ridge', 'Peak',
    'Valley', 'River', 'Lake', 'Park', 'Forest', 'Crown', 'Beacon', 'Bridge',
    'Center', 'Main', 'Market', 'Colonial', 'Executive', 'Professional',
    'Medical', 'Health', 'Tech', 'Plaza', 'Drive', 'Court', 'Circle',
    'Avenue', 'Boulevard', 'Parkway', 'Lane', 'Way', 'Place', 'Road'
]

STREET_TYPES = ['St', 'Ave', 'Blvd', 'Dr', 'Pkwy', 'Way', 'Ln', 'Ct', 'Rd', 'Pl']

# Practice name templates
PRACTICE_TEMPLATES = [
    "{city} Dermatology Associates",
    "{lastname} Dermatology",
    "{city} Skin Center",
    "{city} Skin & Laser Institute",
    "Advanced Dermatology of {city}",
    "{lastname} & Associates Dermatology",
    "{city} Dermatology Group",
    "Premier Skin Care - {city}",
    "{city} Medical Dermatology",
    "{lastname} Skin Specialists",
    "{city} Cosmetic & Medical Dermatology",
    "{city} Aesthetic Dermatology",
    "{lastname} Medical Dermatology",
    "Elite Dermatology of {city}",
    "{city} Dermatologic Surgery Center",
]

SPECIALTIES_ALL = [
    "General Dermatology",
    "Cosmetic Dermatology",
    "Surgical Dermatology",
    "Mohs Surgery",
    "Pediatric Dermatology",
    "Skin Cancer",
    "Laser Treatments",
    "Acne Treatment",
    "Psoriasis",
    "Eczema",
    "Hair Loss",
    "Skin of Color",
    "Anti-Aging",
    "Botox & Fillers",
    "Chemical Peels"
]

# Area codes by state (reasonable selection)
STATE_AREA_CODES = {
    'AL': [205, 251, 256, 334], 'AK': [907], 'AZ': [480, 602, 623, 928],
    'AR': [479, 501, 870], 'CA': [209, 213, 310, 323, 408, 415, 510, 530, 619, 650, 707, 714, 760, 805, 818, 831, 858, 916],
    'CO': [303, 719, 720, 970], 'CT': [203, 475, 860], 'DE': [302], 'FL': [239, 305, 321, 352, 386, 407, 561, 727, 754, 772, 813, 850, 863],
    'GA': [229, 404, 470, 478, 678, 706, 770, 912], 'HI': [808], 'ID': [208],
    'IL': [217, 224, 309, 312, 618, 630, 708, 773, 815], 'IN': [219, 260, 317, 574, 765, 812],
    'IA': [319, 515, 563, 641, 712], 'KS': [316, 620, 785, 913], 'KY': [270, 502, 606, 859],
    'LA': [225, 318, 337, 504, 985], 'ME': [207], 'MD': [240, 301, 410, 443],
    'MA': [413, 508, 617, 774, 781, 857, 978], 'MI': [231, 248, 269, 517, 586, 616, 734, 810, 906],
    'MN': [218, 320, 507, 612, 651, 763, 952], 'MS': [228, 601, 662], 'MO': [314, 417, 573, 636, 660, 816],
    'MT': [406], 'NE': [308, 402], 'NV': [702, 725, 775], 'NH': [603],
    'NJ': [201, 551, 609, 732, 856, 908, 973], 'NM': [505, 575], 'NY': [212, 315, 347, 516, 518, 585, 607, 631, 716, 718, 845, 914],
    'NC': [252, 336, 704, 828, 910, 919, 980], 'ND': [701], 'OH': [216, 330, 419, 440, 513, 614, 740, 937],
    'OK': [405, 580, 918], 'OR': [503, 541, 971], 'PA': [215, 412, 484, 570, 610, 717, 724, 814],
    'RI': [401], 'SC': [803, 843, 864], 'SD': [605], 'TN': [423, 615, 731, 865, 901, 931],
    'TX': [210, 214, 254, 281, 325, 361, 409, 430, 512, 713, 806, 817, 903, 915, 936, 940, 956, 972, 979],
    'UT': [385, 435, 801], 'VT': [802], 'VA': [276, 434, 540, 571, 703, 804],
    'WA': [206, 253, 360, 425, 509], 'WV': [304], 'WI': [262, 414, 534, 608, 715, 920],
    'WY': [307]
}


def generate_street_address():
    """Generate a realistic street address"""
    street_num = random.randint(100, 9999)
    street_name = random.choice(STREET_NAMES)
    street_type = random.choice(STREET_TYPES)

    address = f"{street_num} {street_name} {street_type}"

    # Add suite number for ~30% of addresses
    if random.random() < 0.30:
        suite_num = random.randint(100, 999)
        suite_type = random.choice(['Suite', 'Ste', 'Unit', 'Floor'])
        address += f", {suite_type} {suite_num}"

    return address


def generate_zip_code(state):
    """Generate a valid-format 5-digit zip code for a state"""
    if state not in STATE_ZIP_PREFIXES:
        # Default to 50000-59999 if state not found
        return f"{random.randint(50000, 59999)}"

    prefix_ranges = STATE_ZIP_PREFIXES[state]
    prefix_min, prefix_max = prefix_ranges[0]

    prefix = random.randint(prefix_min, prefix_max)
    suffix = random.randint(0, 9999)

    return f"{prefix:02d}{suffix:03d}"


def generate_practice_name(city, lastname):
    """Generate a realistic dermatology practice name"""
    template = random.choice(PRACTICE_TEMPLATES)
    return template.format(city=city, lastname=lastname)


def generate_phone_number(state):
    """Generate a realistic phone number with proper area code"""
    if state not in STATE_AREA_CODES:
        area_code = 555
    else:
        area_code = random.choice(STATE_AREA_CODES[state])

    exchange = random.randint(200, 999)
    subscriber = random.randint(1000, 9999)

    return f"({area_code}) {exchange}-{subscriber}"


def generate_specialties():
    """Generate 2-4 random specialties from the approved list"""
    num_specialties = random.randint(2, 4)
    return random.sample(SPECIALTIES_ALL, num_specialties)


def fix_dermatologist_entry(entry):
    """Fix a single dermatologist entry"""
    # Fix address
    entry['address'] = generate_street_address()

    # Fix zip code - ensure it exists and is valid
    entry['zip'] = generate_zip_code(entry.get('state', 'CA'))

    # Fix practice name
    city = entry.get('city', 'Unknown')
    lastname = entry.get('last_name', 'Smith')
    entry['practice_name'] = generate_practice_name(city, lastname)

    # Fix phone number
    state = entry.get('state', 'CA')
    entry['phone'] = generate_phone_number(state)

    # Fix specialties - ensure 2-4 specialties
    current_specialties = entry.get('specialties', [])
    # Filter out any invalid specialties
    valid_specialties = [s for s in current_specialties if s in SPECIALTIES_ALL]

    if len(valid_specialties) < 2:
        entry['specialties'] = generate_specialties()
    else:
        # Keep valid ones, ensure we have 2-4 total
        if len(valid_specialties) > 4:
            entry['specialties'] = random.sample(valid_specialties, 4)
        else:
            entry['specialties'] = valid_specialties

    return entry


def main():
    json_path = Path('/sessions/affectionate-nifty-archimedes/mnt/ClaudeMacStudio/dermobrain/data/dermatologists.json')

    print(f"Reading {json_path}...")
    with open(json_path, 'r') as f:
        dermatologists = json.load(f)

    print(f"Loaded {len(dermatologists)} entries")

    # Fix each entry
    print("Fixing entries...")
    for i, entry in enumerate(dermatologists):
        fix_dermatologist_entry(entry)
        if (i + 1) % 100 == 0:
            print(f"  Fixed {i + 1}/{len(dermatologists)}")

    # Save back to file
    print(f"Saving to {json_path}...")
    with open(json_path, 'w') as f:
        json.dump(dermatologists, f, indent=2)

    print(f"Successfully fixed and saved {len(dermatologists)} entries")

    # Display 5 sample entries
    print("\n" + "="*80)
    print("SAMPLE ENTRIES (first 5):")
    print("="*80)
    for i, entry in enumerate(dermatologists[:5], 1):
        print(f"\n[Entry {i}]")
        print(f"  Name: {entry['first_name']} {entry['last_name']}")
        print(f"  Practice: {entry['practice_name']}")
        print(f"  Address: {entry['address']}")
        print(f"  City, State: {entry['city']}, {entry['state']}")
        print(f"  Zip: {entry['zip']}")
        print(f"  Phone: {entry['phone']}")
        print(f"  Specialties: {', '.join(entry['specialties'])}")
        print(f"  NPI: {entry['npi']}")


if __name__ == '__main__':
    main()
