#!/usr/bin/env python3
"""Generate comprehensive synthetic dermatologist data for all 50 states."""

import json
import random
import hashlib

# Real US cities by state (major cities + suburbs)
CITIES_BY_STATE = {
    "AL": ["Birmingham", "Huntsville", "Montgomery", "Mobile", "Tuscaloosa", "Hoover", "Dothan", "Auburn"],
    "AK": ["Anchorage", "Fairbanks", "Juneau", "Wasilla"],
    "AZ": ["Phoenix", "Tucson", "Mesa", "Scottsdale", "Chandler", "Tempe", "Gilbert", "Glendale", "Peoria", "Surprise"],
    "AR": ["Little Rock", "Fort Smith", "Fayetteville", "Springdale", "Jonesboro", "Rogers"],
    "CA": ["Los Angeles", "San Francisco", "San Diego", "San Jose", "Sacramento", "Fresno", "Long Beach", "Oakland", "Bakersfield", "Anaheim", "Santa Ana", "Riverside", "Irvine", "Pasadena", "Beverly Hills", "Santa Monica", "Burbank", "Torrance", "Palo Alto", "Newport Beach", "Walnut Creek", "Encino", "Redondo Beach", "La Jolla", "Manhattan Beach", "Woodland Hills"],
    "CO": ["Denver", "Colorado Springs", "Aurora", "Fort Collins", "Lakewood", "Boulder", "Thornton", "Arvada"],
    "CT": ["Hartford", "New Haven", "Stamford", "Bridgeport", "Waterbury", "Norwalk", "Danbury", "Greenwich"],
    "DE": ["Wilmington", "Dover", "Newark", "Middletown"],
    "DC": ["Washington"],
    "FL": ["Miami", "Orlando", "Tampa", "Jacksonville", "Fort Lauderdale", "St. Petersburg", "Naples", "Sarasota", "Boca Raton", "West Palm Beach", "Coral Gables", "Gainesville", "Tallahassee", "Clearwater", "Palm Beach Gardens"],
    "GA": ["Atlanta", "Augusta", "Columbus", "Savannah", "Athens", "Macon", "Roswell", "Alpharetta", "Marietta", "Sandy Springs"],
    "HI": ["Honolulu", "Hilo", "Kailua", "Pearl City"],
    "ID": ["Boise", "Meridian", "Nampa", "Idaho Falls"],
    "IL": ["Chicago", "Aurora", "Naperville", "Joliet", "Rockford", "Springfield", "Evanston", "Oak Brook", "Schaumburg", "Highland Park"],
    "IN": ["Indianapolis", "Fort Wayne", "Evansville", "South Bend", "Carmel", "Fishers"],
    "IA": ["Des Moines", "Cedar Rapids", "Davenport", "Iowa City", "Ames"],
    "KS": ["Wichita", "Overland Park", "Kansas City", "Olathe", "Topeka", "Lawrence"],
    "KY": ["Louisville", "Lexington", "Bowling Green", "Owensboro", "Covington"],
    "LA": ["New Orleans", "Baton Rouge", "Shreveport", "Lafayette", "Lake Charles", "Metairie"],
    "ME": ["Portland", "Bangor", "Lewiston", "Augusta"],
    "MD": ["Baltimore", "Bethesda", "Rockville", "Silver Spring", "Columbia", "Annapolis", "Towson", "Frederick"],
    "MA": ["Boston", "Worcester", "Springfield", "Cambridge", "Newton", "Brookline", "Wellesley", "Burlington", "Lexington"],
    "MI": ["Detroit", "Grand Rapids", "Ann Arbor", "Troy", "Southfield", "Royal Oak", "Birmingham", "Farmington Hills"],
    "MN": ["Minneapolis", "St. Paul", "Rochester", "Duluth", "Bloomington", "Edina", "Plymouth", "Woodbury"],
    "MS": ["Jackson", "Gulfport", "Hattiesburg", "Southaven", "Biloxi"],
    "MO": ["St. Louis", "Kansas City", "Springfield", "Columbia", "Chesterfield", "Clayton", "Creve Coeur"],
    "MT": ["Billings", "Missoula", "Great Falls", "Bozeman"],
    "NE": ["Omaha", "Lincoln", "Bellevue", "Grand Island"],
    "NV": ["Las Vegas", "Henderson", "Reno", "North Las Vegas", "Sparks", "Summerlin"],
    "NH": ["Manchester", "Nashua", "Concord", "Portsmouth"],
    "NJ": ["Newark", "Jersey City", "Princeton", "Morristown", "Cherry Hill", "Hackensack", "Paramus", "Montclair", "Summit", "Ridgewood", "Englewood"],
    "NM": ["Albuquerque", "Santa Fe", "Las Cruces", "Rio Rancho"],
    "NY": ["New York", "Buffalo", "Rochester", "Albany", "White Plains", "Garden City", "Great Neck", "Manhasset", "Scarsdale", "Brooklyn", "Bronx", "Staten Island", "Long Island City"],
    "NC": ["Charlotte", "Raleigh", "Durham", "Winston-Salem", "Greensboro", "Chapel Hill", "Wilmington", "Asheville", "Cary"],
    "ND": ["Fargo", "Bismarck", "Grand Forks", "Minot"],
    "OH": ["Columbus", "Cleveland", "Cincinnati", "Toledo", "Akron", "Dayton", "Beachwood", "Westlake", "Dublin"],
    "OK": ["Oklahoma City", "Tulsa", "Norman", "Edmond", "Broken Arrow"],
    "OR": ["Portland", "Salem", "Eugene", "Bend", "Lake Oswego", "Beaverton"],
    "PA": ["Philadelphia", "Pittsburgh", "Allentown", "Erie", "Reading", "King of Prussia", "Bryn Mawr", "Wynnewood", "Doylestown", "Media"],
    "RI": ["Providence", "Warwick", "Cranston", "East Greenwich"],
    "SC": ["Charleston", "Columbia", "Greenville", "Myrtle Beach", "Mount Pleasant"],
    "SD": ["Sioux Falls", "Rapid City", "Aberdeen"],
    "TN": ["Nashville", "Memphis", "Knoxville", "Chattanooga", "Franklin", "Murfreesboro", "Brentwood"],
    "TX": ["Houston", "Dallas", "San Antonio", "Austin", "Fort Worth", "El Paso", "Plano", "Arlington", "Frisco", "The Woodlands", "Sugar Land", "Southlake", "Katy", "Round Rock", "McKinney"],
    "UT": ["Salt Lake City", "Provo", "Orem", "Sandy", "West Jordan", "Ogden", "Draper"],
    "VT": ["Burlington", "South Burlington", "Rutland"],
    "VA": ["Virginia Beach", "Richmond", "Arlington", "Norfolk", "Alexandria", "McLean", "Fairfax", "Reston", "Charlottesville", "Tysons Corner"],
    "WA": ["Seattle", "Tacoma", "Spokane", "Bellevue", "Kirkland", "Redmond", "Olympia", "Issaquah"],
    "WV": ["Charleston", "Huntington", "Morgantown", "Wheeling"],
    "WI": ["Milwaukee", "Madison", "Green Bay", "Kenosha", "Brookfield", "Wauwatosa"],
    "WY": ["Cheyenne", "Casper", "Jackson"]
}

# Dermatologist name pools
FIRST_NAMES = [
    "James", "Robert", "John", "Michael", "David", "William", "Richard", "Joseph", "Thomas", "Charles",
    "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua",
    "Kenneth", "Kevin", "Brian", "George", "Timothy", "Ronald", "Edward", "Jason", "Jeffrey", "Ryan",
    "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan", "Jessica", "Sarah", "Karen",
    "Lisa", "Nancy", "Betty", "Margaret", "Sandra", "Ashley", "Dorothy", "Kimberly", "Emily", "Donna",
    "Michelle", "Carol", "Amanda", "Melissa", "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura", "Cynthia",
    "Amy", "Angela", "Helen", "Samantha", "Katherine", "Christine", "Debra", "Rachel", "Carolyn", "Janet",
    "Catherine", "Maria", "Heather", "Diane", "Ruth", "Julie", "Olivia", "Joyce", "Virginia", "Victoria",
    "Wei", "Ming", "Jing", "Lei", "Raj", "Priya", "Anil", "Sanjay", "Deepak", "Vikram",
    "Ahmed", "Mohamed", "Ali", "Hassan", "Omar", "Fatima", "Nadia", "Layla",
    "Carlos", "Maria", "Jose", "Luis", "Ana", "Sofia", "Diego", "Isabella",
    "Yuki", "Kenji", "Akira", "Sakura", "Hiro", "Jin", "Soo", "Min"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
    "Chen", "Kim", "Park", "Wang", "Li", "Zhang", "Liu", "Yang", "Huang", "Wu",
    "Patel", "Shah", "Gupta", "Singh", "Kumar", "Sharma", "Reddy", "Desai", "Mehta", "Joshi",
    "Cohen", "Goldberg", "Friedman", "Rosenberg", "Schwartz", "Katz", "Shapiro", "Stein", "Levy", "Weiss",
    "Murphy", "Sullivan", "Kennedy", "O'Brien", "O'Connor", "Ryan", "Kelly", "Burns",
    "Fischer", "Bauer", "Schneider", "Weber", "Wagner", "Muller",
    "Tanaka", "Suzuki", "Watanabe", "Takahashi", "Yamamoto",
    "Fernandez", "Morales", "Reyes", "Cruz", "Ortiz", "Diaz", "Vasquez"
]

CREDENTIALS = ["MD", "DO", "MD, FAAD", "DO, FAAD", "MD, PhD", "MD, MBA", "MD, MS"]

SPECIALTIES = [
    "General Dermatology", "Medical Dermatology", "Surgical Dermatology", "Cosmetic Dermatology",
    "Mohs Surgery", "Pediatric Dermatology", "Dermatopathology", "Laser Surgery",
    "Skin Cancer", "Acne Treatment", "Eczema & Psoriasis", "Hair Loss",
    "Anti-Aging", "Injectables & Fillers", "Laser Treatments", "Body Contouring",
    "Skin of Color", "Nail Disorders", "Contact Dermatitis", "Immunodermatology",
    "Teledermatology", "Phototherapy", "Wound Care", "Vein Treatment"
]

PRACTICE_SUFFIXES = [
    "Dermatology", "Dermatology Associates", "Skin Care Center", "Dermatology & Skin Cancer Center",
    "Dermatology Clinic", "Skin Institute", "Dermatology Group", "Advanced Dermatology",
    "Dermatology & Aesthetics", "Cosmetic & Medical Dermatology", "Skin Health Center",
    "Dermatology Specialists", "Comprehensive Dermatology", "Premier Dermatology",
    "Skin & Laser Center", "Dermatology & Laser Surgery", "Family Dermatology",
    "Regional Dermatology", "Center for Dermatology", "Skin Wellness Center"
]

STREET_NAMES = [
    "Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Park Blvd", "Broadway", "Elm St",
    "Washington Blvd", "Medical Center Dr", "Healthcare Pkwy", "Professional Plaza",
    "University Ave", "Hospital Dr", "Lake View Dr", "Sunrise Blvd", "Highland Ave",
    "Pine St", "Spring St", "Academy Rd", "Commerce Dr", "Executive Dr",
    "Town Center Dr", "Market St", "Valley Rd", "Ridge Rd", "Summit Ave",
    "Peachtree Rd", "Wilshire Blvd", "Michigan Ave", "Newbury St", "Madison Ave"
]

# Dermatologists per state (roughly proportional to population)
DERMS_PER_STATE = {
    "CA": 900, "TX": 600, "FL": 550, "NY": 700, "PA": 350, "IL": 350,
    "OH": 300, "GA": 250, "NC": 250, "MI": 250, "NJ": 300, "VA": 250,
    "WA": 200, "AZ": 200, "MA": 300, "TN": 200, "IN": 150, "MO": 150,
    "MD": 250, "WI": 150, "CO": 200, "MN": 200, "SC": 150, "AL": 120,
    "LA": 120, "KY": 100, "OR": 150, "OK": 100, "CT": 200, "UT": 100,
    "IA": 80, "NV": 100, "AR": 70, "MS": 60, "KS": 80, "NM": 60,
    "NE": 60, "ID": 50, "WV": 40, "HI": 40, "NH": 50, "ME": 40,
    "RI": 40, "MT": 30, "DE": 40, "SD": 25, "ND": 25, "AK": 20,
    "VT": 20, "WY": 15, "DC": 100
}


def generate_npi(seed_str):
    """Generate a deterministic 10-digit NPI-like number from a seed."""
    h = hashlib.md5(seed_str.encode()).hexdigest()
    return "1" + h[:9].replace('a', '1').replace('b', '2').replace('c', '3').replace('d', '4').replace('e', '5').replace('f', '6')


def generate_phone(state, city, index):
    """Generate a realistic phone number."""
    area_codes = {
        "CA": [213, 310, 323, 415, 424, 510, 619, 650, 714, 818, 858, 909, 949],
        "NY": [212, 347, 516, 518, 631, 646, 718, 914, 917],
        "TX": [210, 214, 281, 346, 469, 512, 713, 817, 832, 972],
        "FL": [305, 321, 386, 407, 561, 727, 786, 813, 850, 904, 941, 954],
        "IL": [312, 630, 708, 773, 847],
        "PA": [215, 267, 412, 484, 610, 717],
        "OH": [216, 330, 440, 513, 614, 937],
        "GA": [404, 470, 678, 706, 770, 912],
        "NJ": [201, 551, 609, 732, 856, 908, 973],
        "MA": [339, 508, 617, 781, 857],
    }
    ac = random.choice(area_codes.get(state, [random.randint(200, 999)]))
    return f"({ac}) {random.randint(200,999)}-{random.randint(1000,9999)}"


def main():
    random.seed(42)  # Reproducible
    all_derms = []
    seen_names = set()

    for state, count in DERMS_PER_STATE.items():
        cities = CITIES_BY_STATE.get(state, ["Unknown"])

        for i in range(count):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)

            # Avoid exact duplicates
            name_key = f"{first} {last} {state}"
            attempts = 0
            while name_key in seen_names and attempts < 10:
                first = random.choice(FIRST_NAMES)
                last = random.choice(LAST_NAMES)
                name_key = f"{first} {last} {state}"
                attempts += 1
            seen_names.add(name_key)

            city = cities[i % len(cities)]
            credential = random.choice(CREDENTIALS)
            npi = generate_npi(f"{first}{last}{state}{city}{i}")

            # Practice name
            if random.random() < 0.4:
                practice_name = f"{last} {random.choice(PRACTICE_SUFFIXES)}"
            elif random.random() < 0.6:
                practice_name = f"{city} {random.choice(PRACTICE_SUFFIXES)}"
            else:
                practice_name = f"Dr. {first} {last} {random.choice(PRACTICE_SUFFIXES)}"

            # Address
            address = f"{random.randint(100, 9999)} {random.choice(STREET_NAMES)}"
            if random.random() < 0.3:
                address += f", Suite {random.randint(100, 999)}"

            # Specialties (1-3)
            num_specs = random.randint(1, 3)
            specs = random.sample(SPECIALTIES, num_specs)

            # Phone
            phone = generate_phone(state, city, i)

            # Zip
            zip_code = str(random.randint(10000, 99999))

            # Premium (5% chance)
            is_premium = random.random() < 0.05

            all_derms.append({
                "npi": npi,
                "first_name": first,
                "last_name": last,
                "credential": credential,
                "practice_name": practice_name,
                "address": address,
                "city": city,
                "state": state,
                "zip": zip_code,
                "phone": phone,
                "specialties": specs,
                "is_premium": is_premium
            })

    # Sort
    all_derms.sort(key=lambda x: (x["state"], x["city"], x["last_name"]))

    with open("data/dermatologists.json", 'w') as f:
        json.dump(all_derms, f, indent=2)

    states = set(d["state"] for d in all_derms)
    cities = set(f"{d['city']}, {d['state']}" for d in all_derms)
    print(f"Generated {len(all_derms)} dermatologists")
    print(f"States: {len(states)}, Cities: {len(cities)}")


if __name__ == "__main__":
    main()
