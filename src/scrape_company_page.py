# %%
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import warnings
import re
from bs4 import BeautifulSoup
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve page with status code: {response.status_code}")
        return None
    

def extract_indeling_info(html):
    soup = BeautifulSoup(html, "html.parser")
    indeling_data = {
        "kamers": None,
        "badkamers": None,
        "voorzieningen": None,
        "woonlagen": None,
        "verdieping": None,
        "energielabel": None,
        "isolatie": None,
        "verwarming": None,
        "warm_water": None,
    }

    rows = soup.select('div[data-testid="category-indeling"] dt')
    for dt in rows:
        label = dt.get_text(strip=True).lower()
        dd = dt.find_next_sibling("dd")
        value = dd.get_text(strip=True) if dd else None

        if "kamers" in label:
            indeling_data["kamers"] = value
        elif "badkamers" in label:
            indeling_data["badkamers"] = value
        elif "voorzieningen" in label:
            indeling_data["voorzieningen"] = value
        elif "woonlagen" in label:
            indeling_data["woonlagen"] = value
        elif "gelegen op" in label:
            indeling_data["verdieping"] = value

    energie_rows = soup.select('div[data-testid="category-energie"] dt')
    for dt in energie_rows:
        label = dt.get_text(strip=True).lower()
        dd = dt.find_next_sibling("dd")
        value = dd.get_text(strip=True) if dd else None

        if "energielabel" in label:
            indeling_data["energielabel"] = value
        elif "isolatie" in label:
            indeling_data["isolatie"] = value
        elif "verwarming" in label:
            indeling_data["verwarming"] = value
        elif "warm water" in label:
            indeling_data["warm_water"] = value

    return indeling_data

def extract_listing_data(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Step 1: Find the script tag with __NUXT__ or JSON-like data
    script = soup.find('script', text=re.compile(r'window\.__NUXT__'))
    if not script:
        return {}

    # Step 2: Extract JSON from script contents
    match = re.search(r'window\.__NUXT__\s*=\s*({.*});', script.string, re.DOTALL)
    if not match:
        return {}

    nuxt_json_str = match.group(1)

    try:
        # Evaluate or parse the JS object
        data = json.loads(nuxt_json_str)
    except json.JSONDecodeError:
        return {}

    # Step 3: Traverse through the nested JSON to pull relevant fields
    # This step depends on actual JSON structure; example below is flexible

    listing_data = {}

    # Example regex-based fallback if JSON structure varies:
    pattern_pairs = {
        'soort_appartement': r'"Soort appartement"\s*,\s*"([^"]+)"',
        'soort_bouw': r'"Soort bouw"\s*,\s*"([^"]+)"',
        'bouwjaar': r'"Bouwjaar"\s*,\s*"([^"]+)"',
        'soort_dak': r'"Soort dak"\s*,\s*"([^"]+)"',
        'woonoppervlakte_m2': r'"Wonen"\s*,\s*"(\d+)\s*m²"',
        'gebouwgebonden_buitenruimte_m2': r'"Gebouwgebonden buitenruimte"\s*,\s*"(\d+)\s*m²"',
        'externe_bergruimte_m2': r'"Externe bergruimte"\s*,\s*"(\d+)\s*m²"',
        'inhoud_m3': r'"Inhoud"\s*,\s*"(\d+)\s*m³"'
    }

    for key, regex in pattern_pairs.items():
        match = re.search(regex, html)
        if match:
            value = match.group(1).strip()
            # Only convert to int if value is numeric
            if ('m2' in key or 'm3' in key or key == 'bouwjaar') and value.isdigit():
                listing_data[key] = int(value)
            else:
                listing_data[key] = value

    return listing_data

import re

def extract_surface_areas(text):
    """
    Extracts surface area values in m² from structured Funda HTML/JS blocks.
    Returns a dictionary with values as integers (in m²), if present.
    """
    fields = {
        "woonoppervlakte_m2": r'"Wonen"\s*,\s*"(\d+)\s*m²"',
        "gebouwgebonden_buitenruimte_m2": r'"Gebouwgebonden buitenruimte"\s*,\s*"(\d+)\s*m²"',
        "externe_bergruimte_m2": r'"Externe bergruimte"\s*,\s*"(\d+)\s*m²"',
        "inhoud_m3": r'"Inhoud"\s*,\s*"(\d+)\s*m³"'
    }

    data = {}
    for key, pattern in fields.items():
        match = re.search(pattern, text)
        if match:
            data[key] = int(match.group(1).strip())

    return data

def extract_energy_label(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find the dt with "Energielabel"
    label_dt = soup.find('dt', string="Energielabel")
    if label_dt:
        # The <dd> element is typically the next sibling of the <dt>
        dd = label_dt.find_next_sibling('dd')
        if dd:
            span = dd.find('span')
            if span:
                return span.get_text(strip=True)
    return None

def extract_overdracht_from_json_block(raw_text):
    data = {}

    fields = {
        "vraagprijs": r'"Vraagprijs"\s*,\s*"([^"]+)"',
        "prijs_per_m2": r'"Vraagprijs per m²"\s*,\s*"([^"]+)"',
        "aangeboden_sinds": r'"Aangeboden sinds"\s*,\s*"([^"]+)"',
        "status": r'"Status"\s*,\s*"([^"]+)"',
        "aanvaarding": r'"Aanvaarding"\s*,\s*"([^"]+)"',
        "servicekosten": r'"Bijdrage VvE"\s*,\s*"([^"]+)"',
    }

    for key, pattern in fields.items():
        match = re.search(pattern, raw_text)
        data[key] = match.group(1) if match else None

    return data

def extract_kadastrale_info_from_flat_html(raw_text):
    def extract_value(label_key):
        # Match the pattern: "label_key","Label","Actual value"
        pattern = rf'"{re.escape(label_key)}"\s*,\s*"[^"]+"\s*,\s*"([^"]+)"'
        match = re.search(pattern, raw_text)
        return match.group(1).strip() if match else None

    return {
        "eigendomssituatie": extract_value("cadastral-ownershipsituation"),
        "lasten": extract_value("cadastral-fees")
    }


def scrape_company_information():
    today = pd.Timestamp.now().strftime('%Y-%m-%d')
    input_path = os.path.join(os.getcwd(), 'data', f'funda_data_{today}.csv')
    df = pd.read_csv(input_path)

    # df price/m2 sort from low to high
    df.sort_values(by='price/m2', inplace=True)
    df_working = df.copy()

    for idx, row in df_working.iterrows():
        if idx % 10 == 0:
            logging.info(f"Processing row {idx}/{len(df_working)}")
        url = row['url']

        # Skip if already processed
        if pd.notna(row['indeling_kamers']):
            continue

        counter += 1
        print(f"Processing {counter}/{len(df_working)}: {url}")

        html = get_html(url)
        if not html:
            continue

        # Extract structured content
        indeling_info = extract_indeling_info(html)
        kadaster_info = extract_kadastrale_info_from_flat_html(html)
        listing_data = extract_listing_data(html)
        energy_label = extract_energy_label(html)
        overdracht_info = extract_overdracht_from_json_block(html)
        surface_info = extract_surface_areas(html)

        # Combine all extracted data
        flat_data = {}
        for key, value in {
            "indeling": indeling_info,
            "kadaster": kadaster_info,
            "listing_data": listing_data,
            "overdracht": overdracht_info,
            "surface": surface_info  # <--- NEW
        }.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flat_data[f"{key}_{sub_key}"] = sub_value
            else:
                flat_data[key] = value
        flat_data["energy_label"] = energy_label


        # Update DataFrame row
        for col, val in flat_data.items():
            df_working.at[idx, col] = val

        # Save progress
        output_path = os.path.join(os.getcwd(), 'data', f'funda_data_{today}.csv')
        df_working.to_csv(output_path, index=False)
