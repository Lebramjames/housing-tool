# %%
# %%
import os
import re
import time
import pandas as pd
import requests
import urllib3
from tqdm import tqdm

from datetime import datetime


from src.utils.google_sheets import read_sheet_to_df
from src.utils.config import logging, GEOCODED_STREETS, RENTAL_DB
from src.utils.google_sheets import append_row_to_sheet


# Disable SSL warnings (for VPN / MITM environments)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load API key
GEOCODE_API = os.getenv("GEOCODE_API")

# Constants
CITY_FALLBACK = "Amsterdam"
COUNTRY = "NL"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "geocoded_streets")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "geocoded_streets.csv")

INPUT = { 
    'rental' : os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "huren"), 
    'buying' : None
}

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_street(address):
    if isinstance(address, str):
        match = re.match(r"^(.*?)(?=\d)", address.strip())
        return match.group(0).strip() if match else address.strip()
    return None


def finalize_dataframe(df):

    df['street'] = df['street']
    df['latitude'] = df['latitude'].astype(float)
    df['longitude'] = df['longitude'].astype(float)

    df['info1'] = df['neighborhood']
    df['info2'] = df['district']
    df['info3'] = df['city']
    df['postcode'] = df['postcode']

    df['location'] = df.apply(lambda x: f"{x['latitude']}, {x['longitude']}" if pd.notna(x['latitude']) and pd.notna(x['longitude']) else None, axis=1)
    df['display_name'] = df['display_name']
    df['date_updated'] = pd.to_datetime(df['date_updated']).dt.strftime('%Y-%m-%d')


    columns = [
        "street", "latitude", "longitude", "location", "info1", 
        "info2", "info3", "postcode", "display_name", "date_updated"
    ]
    # Ensure all columns exist, fill missing ones with None
    for col in columns:
        if col not in df.columns:
            df[col] = None
    return df[columns].values.tolist()

def run_pipeline(pipeline_name="rental"):
    # Step 1: Load data
    geocoded_streets_df = read_sheet_to_df(GEOCODED_STREETS, 0)
    streets_df = read_sheet_to_df(RENTAL_DB, 0)

    streets = set(streets_df['street'].dropna().unique())
    geocoded_streets = set(geocoded_streets_df['street'].dropna().unique())

    # Step 2: Find streets that still need to be geocoded
    missing_streets = streets - geocoded_streets
    print(f"Missing streets to geocode: {len(missing_streets)}")

    already_done = set(geocoded_streets_df['street'].str.lower().str.strip().dropna().unique())
    new_rows = []

    for street in tqdm(missing_streets, desc="Geocoding streets"):
        normalized_street = street.lower().strip()
        if normalized_street in already_done:
            continue

        try:
            # Format query
            street_param = f"2 {street}".lower().replace(" ", "+")
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

                # Parse parts from display_name
                parts = display_name.split(", ")
                neighborhood = parts[2] if len(parts) > 2 else None
                district = parts[3] if len(parts) > 3 else None
                city = parts[4] if len(parts) > 4 else None
                postcode = parts[-2] if re.match(r'^\d{4}\s?[A-Z]{2}$', parts[-2]) else None

                row = {
                    "street": street,
                    "latitude": lat,
                    "longitude": lon,
                    "neighborhood": neighborhood,
                    "location": f"{lat}, {lon}" if lat and lon else None,
                    "district": district,
                    "city": city,
                    "postcode": postcode,
                    "display_name": display_name,
                    "date_updated": datetime.now().strftime("%Y-%m-%d")
                }
            else:
                row = {
                    "street": street,
                    "latitude": None,
                    "longitude": None,
                    "neighborhood": None,
                    "location": None,
                    "district": None,
                    "city": None,
                    "postcode": None,
                    "display_name": None,
                    "date_updated": datetime.now().strftime("%Y-%m-%d")
                }

            new_rows.append(row)
            already_done.add(normalized_street)
            time.sleep(1)  # Respect API rate limits

        except Exception as e:
            print(f"❌ Error geocoding {street}: {e}")

    if new_rows:
        df_new = pd.DataFrame(new_rows)
        append_row_to_sheet(df_new, GEOCODED_STREETS)
        print(f"\n✅ Geocoding complete. {len(new_rows)} new streets added to Google Sheet.")
    else:
        print("✅ No new streets to geocode.")

if __name__ == "__main__":
    run_pipeline()

# %%


df = read_sheet_to_df(GEOCODED_STREETS, 0)

df