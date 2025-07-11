# %% neighborhood_processor.py
import os
import re
import pandas as pd
from rapidfuzz import process, fuzz
from tqdm import tqdm
from pathlib import Path

from src.utils import *

INPUT_DIR = os.path.join(DATA_DIR ,  "huren")
OUTPUT_DIR = os.path.join(DATA_DIR, "geocoded_streets")
GEOCODED_PATH = os.path.join(OUTPUT_DIR, "geocoded_streets.csv")

# Load geocoded streets
geocoded_df = pd.read_csv(GEOCODED_PATH)
geocoded_df["street_clean"] = geocoded_df["street"].str.lower().str.strip()

# Function to extract street part from address
def extract_street(address):
    if isinstance(address, str):
        match = re.match(r"^(.*?)(?=\d)", address.strip())
        return match.group(0).strip().lower() if match else address.strip().lower()
    return None

def run_pipeline():
    # Match and enrich each input file
    for file in os.listdir(INPUT_DIR):
        if not file.endswith(".csv"):
            continue
        if file.startswith("enriched_"):
            continue  # Skip already enriched files

        input_path = os.path.join(INPUT_DIR, file)
        df = pd.read_csv(input_path)

        # Extract street
        df["street_extracted"] = df["address"].map(extract_street)

        # Create output columns if missing
        if "lat" not in df.columns:
            df["lat"] = None
        if "lon" not in df.columns:
            df["lon"] = None
        if "neighborhood" not in df.columns:
            df["neighborhood"] = None

        # Fuzzy match and fill only missing values
        for idx, row in tqdm(df.iterrows(), total=len(df), desc=f"Processing {file}"):
            if pd.notna(row["lat"]) and pd.notna(row["lon"]) and pd.notna(row["neighborhood"]):
                continue  # Already enriched

            street = row["street_extracted"]
            if not isinstance(street, str):
                continue

            match = process.extractOne(
                street,
                geocoded_df["street_clean"],
                scorer=fuzz.token_sort_ratio
            )

            if match and match[1] >= 85:
                matched_row = geocoded_df[geocoded_df["street_clean"] == match[0]].iloc[0]
                df.at[idx, "lat"] = matched_row["lat"]
                df.at[idx, "lon"] = matched_row["lon"]
                df.at[idx, "neighborhood"] = matched_row.get("neighborhood")

        # Save enriched version
        output_path = os.path.join(INPUT_DIR, f"enriched_{file}")
        df.drop(columns=["street_extracted"], inplace=True)
        df.to_csv(output_path, index=False)
        print(f"✅ Enriched and saved to {output_path}")

# %%
# %
if __name__ == "__main__":
    run_pipeline()

