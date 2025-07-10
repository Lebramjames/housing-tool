# %%
# %%
import os
import re
import time
import pandas as pd
import requests
import urllib3
from tqdm import tqdm

# Disable SSL warnings (for VPN / MITM environments)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load API key
GEOCODE_API = os.getenv("GEOCODE_API")

# Constants
CITY_FALLBACK = "Amsterdam"
COUNTRY = "NL"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "geocoded_streets")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "geocoded_streets.csv")
INPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "huren")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_street(address):
    if isinstance(address, str):
        match = re.match(r"^(.*?)(?=\d)", address.strip())
        return match.group(0).strip() if match else address.strip()
    return None

def run_pipeline():
    # Step 1: Load all unique addresses from input files
    all_addresses = []

    for file in os.listdir(INPUT_DIR):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(INPUT_DIR, file))
            if 'address' in df.columns:
                all_addresses.extend(df['address'].dropna().unique())

    streets = sorted(set(filter(None, [extract_street(a) for a in all_addresses])))
    print(streets)
    # Step 2: Load already geocoded streets
    if os.path.exists(OUTPUT_FILE):
        existing_df = pd.read_csv(OUTPUT_FILE)
        already_done = set(existing_df['street'].str.lower().str.strip())
    else:
        existing_df = pd.DataFrame(columns=["street", "lat", "lon", "neighborhood", "district", "city", "postcode", "display_name"])
        already_done = set()

    # Step 3: Geocode missing streets
    new_rows = []

    for street in tqdm(streets, desc="Geocoding streets"):
        normalized_street = street.lower().strip()

        if normalized_street in already_done:
            continue

        try:
            # Format query
            street_param = f"1 {street}".lower().replace(" ", "+")
            city_param = CITY_FALLBACK.lower().replace(" ", "+")
            url = (
                f"https://geocode.maps.co/search?"
                f"street={street_param}&"
                f"city={city_param}&"
                f"country={COUNTRY}&"
                f"api_key={GEOCODE_API}"
            )

            response = requests.get(url, verify=False, timeout=10)
            data = response.json() if response.status_code == 200 else []

            if data:
                entry = data[0]
                lat = entry.get("lat")
                lon = entry.get("lon")
                display_name = entry.get("display_name", "")

                # Parse components from display_name
                parts = display_name.split(", ")
                neighborhood = parts[2] if len(parts) > 2 else None
                district = parts[3] if len(parts) > 3 else None
                city = parts[4] if len(parts) > 4 else None
                postcode = parts[-2] if re.match(r'^\d{4}\s?[A-Z]{2}$', parts[-2]) else None

                row = {
                    "street": street,
                    "lat": lat,
                    "lon": lon,
                    "neighborhood": neighborhood,
                    "district": district,
                    "city": city,
                    "postcode": postcode,
                    "display_name": display_name
                }
            else:
                row = {
                    "street": street,
                    "lat": None,
                    "lon": None,
                    "neighborhood": None,
                    "district": None,
                    "city": None,
                    "postcode": None,
                    "display_name": None
                }

            # Save row immediately
            pd.DataFrame([row]).to_csv(OUTPUT_FILE, mode='a', header=not os.path.exists(OUTPUT_FILE), index=False)
            already_done.add(normalized_street)
            new_rows.append(row)

            # Respect API rate limits
            time.sleep(1)

        except Exception as e:
            print(f"❌ Error geocoding {street}: {e}")

    print(f"\n✅ Geocoding complete. {len(new_rows)} new streets added to {OUTPUT_FILE}.")


if __name__ == "__main__":
    run_pipeline()

# %%
