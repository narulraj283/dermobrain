#!/usr/bin/env python3
"""
Fetch real dermatologist data from the NPPES NPI Registry API.
Taxonomy code 207N00000X = Dermatology
"""

import json
import time
import urllib.request
import urllib.parse
import os

API_URL = "https://npiregistry.cms.hhs.gov/api/"
TAXONOMY = "207N00000X"  # Dermatology

# All US states
STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC"
]

STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia"
}


def fetch_dermatologists_for_state(state_code, skip=0, limit=200):
    """Fetch dermatologists from NPPES API for a given state."""
    params = {
        "version": "2.1",
        "taxonomy_description": "Dermatology",
        "state": state_code,
        "limit": limit,
        "skip": skip,
        "pretty": "false"
    }
    url = API_URL + "?" + urllib.parse.urlencode(params)

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DermoBrain/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        print(f"  Error fetching {state_code} (skip={skip}): {e}")
        return None


def parse_result(result):
    """Parse a single NPI registry result into our format."""
    basic = result.get("basic", {})
    addresses = result.get("addresses", [])
    taxonomies = result.get("taxonomies", [])

    # Get practice location address (location_type = 2 is practice, 1 is mailing)
    practice_addr = None
    for addr in addresses:
        if addr.get("address_purpose") == "LOCATION":
            practice_addr = addr
            break
    if not practice_addr and addresses:
        practice_addr = addresses[0]

    if not practice_addr:
        return None

    # Get specialties from taxonomies
    specialties = []
    for tax in taxonomies:
        desc = tax.get("desc", "")
        if desc and desc != "Dermatology":
            specialties.append(desc)
    if not specialties:
        specialties = ["General Dermatology"]

    # Build the record
    first_name = basic.get("first_name", "").title()
    last_name = basic.get("last_name", "").title()
    credential = basic.get("credential", "MD")

    # Clean credential
    if credential:
        credential = credential.replace(".", "").strip()
        if not credential:
            credential = "MD"
    else:
        credential = "MD"

    city = practice_addr.get("city", "").title()
    state = practice_addr.get("state", "")
    zip_code = practice_addr.get("postal_code", "")[:5]

    # Build practice name
    org_name = basic.get("organization_name", "")
    if org_name:
        practice_name = org_name.title()
    else:
        practice_name = f"Dr. {first_name} {last_name} Dermatology"

    # Phone
    phone = practice_addr.get("telephone_number", "")
    if phone and len(phone) == 10:
        phone = f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"

    address_line = practice_addr.get("address_1", "").title()
    address_2 = practice_addr.get("address_2", "")
    if address_2:
        address_line += f", {address_2.title()}"

    return {
        "npi": str(result.get("number", "")),
        "first_name": first_name,
        "last_name": last_name,
        "credential": credential,
        "practice_name": practice_name,
        "address": address_line,
        "city": city,
        "state": state,
        "zip": zip_code,
        "phone": phone,
        "specialties": specialties[:3],
        "is_premium": False
    }


def main():
    all_dermatologists = []
    seen_npis = set()

    for state in STATES:
        print(f"Fetching {state}...", end=" ", flush=True)
        skip = 0
        state_count = 0

        while True:
            data = fetch_dermatologists_for_state(state, skip=skip)
            if not data:
                break

            results = data.get("results", [])
            if not results:
                break

            for result in results:
                npi = str(result.get("number", ""))
                if npi in seen_npis:
                    continue
                seen_npis.add(npi)

                parsed = parse_result(result)
                if parsed and parsed["city"] and parsed["state"]:
                    all_dermatologists.append(parsed)
                    state_count += 1

            # Check if there are more results
            result_count = data.get("result_count", 0)
            if skip + len(results) >= result_count or len(results) < 200:
                break

            skip += 200
            time.sleep(0.5)  # Be nice to the API

        print(f"{state_count} found")
        time.sleep(0.3)

    # Sort by state, then city, then last name
    all_dermatologists.sort(key=lambda x: (x["state"], x["city"], x["last_name"]))

    # Save to file
    output_file = os.path.join("data", "dermatologists.json")
    with open(output_file, 'w') as f:
        json.dump(all_dermatologists, f, indent=2)

    print(f"\n{'='*50}")
    print(f"Total dermatologists fetched: {len(all_dermatologists)}")
    print(f"Saved to: {output_file}")

    # Stats
    states_found = set(d["state"] for d in all_dermatologists)
    cities_found = set(f"{d['city']}, {d['state']}" for d in all_dermatologists)
    print(f"States covered: {len(states_found)}")
    print(f"Cities covered: {len(cities_found)}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
