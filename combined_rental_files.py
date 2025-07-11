# File: src/rental\bouwinvest.py
# %%
# wonenbijbouwinvest_pipeline.py
import os
import time
import re
import logging
import tempfile
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIG ---
BASE_URL = "https://www.wonenbijbouwinvest.nl/"
CITY = "Amsterdam"
MAX_PAGES = 10
GEOCODE_API = os.getenv("GEOCODE_API")  # Set your Maps.co key as env var
OUTPUT_DIR = os.path.join(os.getcwd(), "data", "huren")
USE_EDGE = True
HEADLESS = True

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- DRIVER SETUP ---
def get_driver(local=True):
    def common_options(opts):
        if HEADLESS:
            opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")
        return opts

    if local and USE_EDGE:
        options = common_options(EdgeOptions())
        options.use_chromium = True
        driver = webdriver.Edge(service=EdgeService(), options=options)
    else:
        options = common_options(ChromeOptions())
        service = ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    return driver

# --- ACCEPT COOKIES ---
def accept_cookies(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
        ).click()
        logging.info("Cookies accepted.")
    except TimeoutException:
        logging.warning("No cookie banner found.")

# --- SEARCH LOCATION ---
def search_location(driver, location):
    try:
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "query"))
        )
        search_input.clear()
        search_input.send_keys(location)
        search_input.send_keys(Keys.ENTER)
        logging.info(f"Search location entered: {location}")
    except TimeoutException:
        logging.warning("Search input not found.")

# --- PARSE LISTINGS ---
def extract_listings_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    listings = soup.find_all("div", class_="projectproperty-tile")
    data = []

    for listing in listings:
        try:
            data.append({
                "address": listing.find("span", class_="h2").get_text(strip=True),
                "location": listing.find("span", class_="paragraph fw-light").get_text(strip=True),
                "description": listing.find("span", class_="paragraph").get_text(strip=True),
                "availability": listing.find("span", class_=re.compile("bar__top")).get_text(strip=True),
                "surface_m2": listing.find("span", class_="facet icon-surface").get_text(strip=True).replace("M²", "").strip(),
                "bedrooms": listing.find("span", class_="facet icon-total_sleepingrooms").get_text(strip=True).replace("slaapkamers", "").strip(),
                "price": listing.find("span", class_="price-tag").get_text(strip=True),
                "url": "https://www.wonenbijbouwinvest.nl" + listing.find("a", href=True)['href']
            })
        except Exception as e:
            logging.warning(f"Failed to parse a listing: {e}")
    return data

# --- GEOCODING ---
def geocode_forward(df):
    if not GEOCODE_API:
        logging.warning("No GEOCODE_API key set — skipping geocoding.")
        df["lat"] = None
        df["lon"] = None
        return df

    lats, lons = [], []
    for _, row in df.iterrows():
        address = row['address']
        location = row.get('location', '')
        full_address = f"{address}, {location}" if location.lower() not in address.lower() else address
        url = f"https://geocode.maps.co/search?q={full_address}&api_key={GEOCODE_API}"

        try:
            response = requests.get(url)
            if response.ok and response.json():
                lats.append(response.json()[0].get("lat"))
                lons.append(response.json()[0].get("lon"))
            else:
                lats.append(None)
                lons.append(None)
        except Exception as e:
            logging.warning(f"Failed geocoding {full_address}: {e}")
            lats.append(None)
            lons.append(None)

    df["lat"] = lats
    df["lon"] = lons
    return df

# --- MAIN SCRAPER ---
def scrape_bouwinvest(city, local=False):
    driver = get_driver(local=local)
    driver.get(BASE_URL)
    accept_cookies(driver)
    search_location(driver, city)

    all_data = []

    for page in range(1, MAX_PAGES + 1):
        if page > 1:
            url = f"{BASE_URL}huuraanbod?query={city}&page={page}"
            driver.get(url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "projectproperty-tile"))
            )
            html = driver.page_source
            listings = extract_listings_from_html(html)

            if not listings:
                break

            all_data.extend(listings)
            logging.info(f"Page {page}: {len(listings)} listings.")
        except TimeoutException:
            logging.warning(f"Timeout on page {page}, stopping.")
            break

    driver.quit()

    # DataFrame cleanup
    df = pd.DataFrame(all_data)
    df['price'] = (
        df['price'].str.replace("€", "", regex=False)
        .str.replace(" per maand", "", regex=False)
        .str.replace(".", "", regex=False)
        .astype(float)
    )
    df['surface_m2'] = df['surface_m2'].astype(float)
    df['price_per_m2'] = df['price'] / df['surface_m2']
    df['date_scraped'] = pd.Timestamp.now()
    return df

def run_pipeline(local = False):
    logging.info('[START] Scraping Bouwinvest properties in Amsterdam...')
    df = scrape_bouwinvest(CITY, local=local)
    df = geocode_forward(df)

    # Add neighborhood & preference if available
    try:
        from vbt_huren import get_neighborhoods_from_coordinates, get_preference_from_coordinates
        df = get_neighborhoods_from_coordinates(df)
        df = get_preference_from_coordinates(df)
    except ImportError:
        logging.warning("Optional enrichment skipped: vbt_huren not installed")

    old_path = os.path.join(OUTPUT_DIR, f"bouwinvest_{CITY.lower()}.csv")
    df_old = pd.read_csv(old_path) if os.path.exists(old_path) else pd.DataFrame()
    if not df_old.empty:
        # Mark new listings
        df['is_new'] = ~df['url'].isin(df_old['url'])
        # Combine and deduplicate
        df = pd.concat([df_old, df]).drop_duplicates(subset=['url'], keep='last').reset_index(drop=True)
        # For all rows, set is_new to False except for those just scraped
        df['is_new'] = df['is_new'].fillna(False)
        logging.info(f"Combined with old data, total rows: {len(df)}")
    else:
        df['is_new'] = True
        logging.info(f"No old data found, total rows: {len(df)}")
    
    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"bouwinvest_{CITY.lower()}.csv")
    df.to_csv(out_path, index=False)
    logging.info(f"Saved {len(df)} rows to {out_path}")

    logging.info("[END] Scraping completed.")


if __name__ == "__main__":
    run_pipeline()
    logging.info("Bouwinvest scraper completed successfully.")


# File: src/rental\coordinate_finder.py
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

def run_pipeline(pipeline_name="rental"):
    input_type = INPUT[pipeline_name]
    # input_dir = INPUT[]
    # Step 1: Load all unique addresses from input files
    all_addresses = []

    for file in os.listdir(input_type):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(input_type, file))
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


# File: src/rental\ikwilhuren.py
# %%
# scraper.py
import os
import time
import re
import math
import tempfile
import logging
import pandas as pd
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

NAME = "ikwilhuren"
CITY = "amsterdam"

BASE_URL = "https://ikwilhuren.nu/"
EDGE_DRIVER_PATH = r"C:\Users\bgriffioen\OneDrive - STX Commodities B.V\Desktop\funda-project\funda-tool\src\utils\msedgedriver.exe"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "huren")


# --- Webdriver Setup ---
def get_driver(local=True):
    def add_common_options(opts):
        opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--window-size=1920,1080")
        temp_profile_dir = tempfile.mkdtemp()
        opts.add_argument(f"--user-data-dir={temp_profile_dir}")
        return opts

    if local:
        options = add_common_options(EdgeOptions())
        options.use_chromium = True
        service = EdgeService(executable_path=EDGE_DRIVER_PATH)
        return webdriver.Edge(service=service, options=options)
    else:
        options = add_common_options(ChromeOptions())
        service = ChromeService(executable_path=ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)


# --- Cookie Banner Acceptance ---
def accept_cookies(driver):
    try:
        time.sleep(10)  # Give time for JS to load
        script = """
        const shadowHost = document.querySelector('cookiecode-banner');
        const shadowRoot = shadowHost?.shadowRoot;
        const button = shadowRoot?.querySelector('.cc_button_allowall');
        if (button) button.click();
        """
        driver.execute_script(script)
        logging.info("Cookies accepted via JavaScript.")
    except Exception as e:
        logging.error(f"Failed to accept cookies: {e}")





# --- Get Total Pages ---
def get_total_pages(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        count_text = soup.find('span', class_='fs-4 ff-roboto-slab d-block fw-bold mb-0')
        if count_text:
            count_number = count_text.find('span', class_='text-blue-ncs').text.strip()
            total_listings = int(count_number)
            return math.ceil(total_listings / 10)
    except Exception as e:
        logging.error(f"Failed to get total page count: {e}")
    return 1


# --- Extract Listings from HTML ---
def extract_listing_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = []

    cards = soup.find_all('div', class_='card')
    for card in cards:
        try:
            body = card.find('div', class_='card-body')
            title_elem = body.find('span', class_='card-title').find('a')
            title = title_elem.get_text(strip=True)
            details_url = title_elem['href']
            address = body.find_all('span')[1].get_text(strip=True).split('-')[0].strip()

            # Availability
            available_from = None
            small_section = body.find('span', class_='small')
            if small_section:
                text = small_section.get_text()
                if 'Beschikbaar vanaf' in text:
                    available_from = text.split('Beschikbaar vanaf')[-1].strip()

            # Price and features
            bottom_div = body.find('div', class_='pt-4 dotted-spans mt-auto')
            spans = bottom_div.find_all('span')
            price = spans[0].get_text(strip=True)
            surface = spans[1].get_text(strip=True).replace(' m2', '').replace('m', '').strip()
            bedrooms = spans[2].get_text(strip=True).split()[0]

            # Status
            status = None
            badge = card.find('div', class_='badges')
            if badge:
                status_span = badge.find('span', class_='badge')
                status = status_span.get_text(strip=True) if status_span else None

            data.append({
                'address': title,
                'city': address,
                'available_from': available_from,
                'price_per_month': price,
                'surface_m2': surface,
                'bedrooms': bedrooms,
                'details_url': details_url,
                'status': status
            })
        except Exception as e:
            logging.warning(f"Skipping listing due to error: {e}")
    return data


# --- Clean Helpers ---
def split_available_from(val):
    if val is None:
        return None, None
    match = re.match(r'(\d{2}-\d{2}-\d{4})', val)
    date = match.group(1) if match else None
    note = val.replace(date, '', 1).strip() if date else val.strip()
    return date, note or None


def clean_dataframe(df):
    df[['available_from_date', 'available_from_note']] = df['available_from'].apply(
        lambda x: pd.Series(split_available_from(x))
    )

    df['price_per_month'] = (
        df['price_per_month']
        .str.replace('€', '', regex=False)
        .str.replace(',', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.replace('-', '', regex=False)
        .str.replace('/mnd', '', regex=False)
        .str.replace(' ', '', regex=False)
        .astype(float)
    )

    df['details_url'] = df['details_url'].apply(
        lambda x: f"https://ikwilhuren.nu{x}" if not x.startswith('http') else x
    )

    df['is_available'] = df['status'].apply(lambda x: x == 'Te huur')

    df['address'] = (
        df['address']
        .str.replace('Appartement ', '', regex=False)
        .str.replace('Woning ', '', regex=False)
        .str.strip()
    )

    return df

def select_gemeente(driver, gemeente_naam="Gemeente Amsterdam", retries=1):
    for attempt in range(retries):
        try:
            # Klik op het select2 veld om het te activeren
            select_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#select2-selAdres-container"))
            )
            select_field.click()

            # Zoek het input veld binnen de dropdown
            input_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.select2-search__field"))
            )

            input_field.clear()
            input_field.send_keys(gemeente_naam)
            time.sleep(1.5)  # even wachten op zoekresultaten
            input_field.send_keys(Keys.ENTER)
            time.sleep(1.5)  # vaak mislukt dit de eerste keer
            input_field.send_keys(Keys.ENTER)
            zoek_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//button[contains(@class, 'btn-orange') and contains(@class, 'position-relative') and contains(text(), 'Zoeken')]"
                    ))
                )
            zoek_button.click()
            
        except Exception as e:
            logging.warning(f"Poging {attempt + 1} om gemeente te selecteren mislukt: {e}")
        else:
            logging.info(f"Gemeente '{gemeente_naam}' geselecteerd bij poging {attempt + 1}")
            break

# --- Main Scraping Flow ---
def run_pipeline(local = False):
    driver = get_driver(local=local)
    driver.get(BASE_URL)
    accept_cookies(driver)

    from selenium.webdriver.common.keys import Keys

    driver.get("https://ikwilhuren.nu/aanbod/")
    select_gemeente(driver)

    time.sleep(2)
    total_pages = get_total_pages(driver)
    logging.info(f"Totaal aantal pagina's: {total_pages}")

    all_listings = []
    for page_num in range(1, total_pages + 1):
        url = f"{BASE_URL}aanbod/?page={page_num}" if page_num > 1 else f"{BASE_URL}aanbod/"
        driver.get(url)
        time.sleep(3)
        html = driver.page_source
        listings = extract_listing_data(html)
        all_listings.extend(listings)
        logging.info(f"Pagina {page_num} verwerkt ({len(listings)} woningen).")

    driver.quit()

    df = pd.DataFrame(all_listings)
    df = clean_dataframe(df)


    name = f"{NAME}_{CITY}"
    output_path = os.path.join(OUTPUT_DIR, f"{name}.csv")
    logging.info(f"Saving data to {output_path}")

    # Use 'details_url' as the unique link identifier
    df = df.rename(columns={'details_url': 'link'})


    # Add date_scraped column
    df['date_scraped'] = pd.Timestamp.now()

    if os.path.exists(output_path):
        df_old = pd.read_csv(output_path)
        # Mark all as inactive by default
        df_old['is_active'] = False
        # Mark new scrape as active
        df['is_active'] = True

        # Mark is_new: True if link not in previous scrape
        df['is_new'] = ~df['link'].isin(df_old['link'])
        if 'is_new' not in df_old.columns:
            df_old['is_new'] = False

        # Combine, keeping all rows, updating 'is_active' and 'is_new' for current scrape
        df_combined = pd.concat([df_old, df], ignore_index=True)
        # Ensure 'date_scraped' is datetime for proper sorting
        df_combined['date_scraped'] = pd.to_datetime(df_combined['date_scraped'], errors='coerce')
        # For each link, keep the most recent row (by date_scraped)
        df_combined = df_combined.sort_values('date_scraped').drop_duplicates(subset=['link'], keep='last')
    else:
        df['is_active'] = True
        df['is_new'] = True
        df_combined = df

    # address must contain Amsterdam eg: "1014BG Amsterdam" is kept 2671HZ Naaldwijk is removed
    df_combined = df_combined[df_combined['city'].str.contains(CITY, case=False, na=False)]
    df_combined.to_csv(output_path, index=False)
    logging.info(f"Data saved to {output_path}")

if __name__ == "__main__":
    run_pipeline(local=True)
    logging.info(f"[END] Scraping completed for {NAME} in {CITY}.")

# File: src/rental\neighborhood_processor.py
# %%
# %%
# %%
import os
import re
import pandas as pd
from rapidfuzz import process, fuzz
from tqdm import tqdm

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INPUT_DIR = os.path.join(BASE_DIR, "data", "huren")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "geocoded_streets")
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

if __name__ == "__main__":
    run_pipeline()

# File: src/rental\process_rental.py
# %%

import logging


from src.rental import vbt_huren
from src.rental import bouwinvest
from src.rental import vesteda
from rental.notifications import send_email
from src.rental import ikwilhuren

from src.rental import coordinate_finder
from src.rental import neighborhood_processor

# import send_email
# import vbt_huren
# import bouwinvest
# import vesteda
# import ikwilhuren
# import coordinate_finder

def process_rental_main():

    vbt_huren.run_pipeline(local=False)
    vesteda.run_pipeline(local=False)
    ikwilhuren.run_pipeline(local=False)
    bouwinvest.run_pipeline(local=False)


    coordinate_finder.run_pipeline()
    neighborhood_processor.run_pipeline()

    send_email.run_pipeline(rental_company='vbt_huren')


    send_email.run_pipeline(rental_company='bouwinvest')
    send_email.run_pipeline(rental_company='vesteda')

    send_email.run_pipeline(rental_company='ikwilhuren')

if __name__ == "__main__":
    process_rental_main()




# File: src/rental\send_email.py
# %%
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

GOOGLE_KEY = os.getenv("GOOGLE_KEY")

import pandas as pd
import os
from pathlib import Path

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Load preference geojson
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent.parent

def create_vbt_body():
    data_path = os.path.join(parent_dir, 'data', 'huren', 'enriched_properties_amsterdam.csv')  # ✅ enriched version
    df = pd.read_csv(data_path, sep=',')

    df = df[df['is_available'] == True]

    if 'preference' in df.columns:
        df = df[df['preference'] == True]

    df = df.sort_values(by='number_of_responses', ascending=True)

    base_url = 'https://vbtverhuurmakelaars.nl'
    df['link'] = base_url + df['detail_url']
    df['price_per_m2'] = df['price_per_month'] / df['surface_area_m2']
    df = df.dropna(subset=['address', 'price_per_month', 'surface_area_m2', 'price_per_m2', 'number_of_responses', 'link'])

    def create_email_body(df, max_rows=10):
        df = df.head(max_rows).copy()
        df['price_per_m2'] = df['price_per_m2'].round(2)

        body = "VBT Rentals (available):\n\n"
        body += f"{'Address':<35} {'€ Rent':>8} {'m²':>5} {'€/m²':>6} {'Resp.':>6} {'Neighborhood':>15}\n"
        body += "-" * 50 + "\n"

        for _, row in df.iterrows():
            address = row['address'][:32] + "..." if len(row['address']) > 35 else row['address']
            neighborhood = row.get('neighborhood', 'N/A')
            body += f"{address:<35} {int(row['price_per_month']):>8} {int(row['surface_area_m2']):>5} {row['price_per_m2']:>6.2f} {int(row['number_of_responses']):>6} {neighborhood:>15}\n"
            body += f"🔗 {row['link']}\n\n"
        return body

    return create_email_body(df)


def create_bouwinvest_body():
    data_path = os.path.join(parent_dir, 'data', 'huren', 'enriched_bouwinvest_amsterdam.csv')
    df = pd.read_csv(data_path, sep=',')

    # Sort: new listings first, then by price
    df = df.sort_values(by=['is_new', 'price'], ascending=[False, True])

    def create_email_body(df, max_rows=10):
        df = df.head(max_rows).copy()
        df['price_per_m2'] = df['price'] / df['surface_m2']
        df['price_per_m2'] = df['price_per_m2'].round(2)

        body = "🏢 Bouwinvest Rentals (available):\n\n"
        body += f"{'Address':<35} {'€ Rent':>8} {'m²':>5} {'€/m²':>6} {'New':>4} {'Neighborhood':>15}\n"
        body += "-" * 70 + "\n"

        for _, row in df.iterrows():
            address = row['address'][:32] + "..." if len(row['address']) > 35 else row['address']
            is_new = 'Yes' if row.get('is_new', False) else 'No'
            neighborhood = row.get('neighborhood', 'N/A')

            body += f"{address:<35} {int(row['price']):>8} {int(row['surface_m2']):>5} {row['price_per_m2']:>6.2f} {is_new:>4} {neighborhood:>15}\n"
            body += f"🔗 {row['url']}\n\n"

        return body

    return create_email_body(df)


def send_gmail(to_email, subject, body, gmail_user, app_password = GOOGLE_KEY):
    msg = MIMEMultipart()
# def send_gmail(to_email, subject, body, gmail_user, app_password = GOOGLE_KEY):
    if not app_password:
        print("❌ Error: GOOGLE_KEY environment variable is not set.")
        return

    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, app_password)
        server.send_message(msg)
        server.quit()
        print("✅ Email sent successfully")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

def create_vesteda_body():
    data_path = os.path.join(parent_dir, 'data', 'huren', 'enriched_vesteda_amsterdam.csv')
    df = pd.read_csv(data_path, sep=',')

    df = df[df['is_available'] == True]

    # Ensure we're only working with listings in Amsterdam
    df = df[df['address'].str.contains('Amsterdam', case=False, na=False)]

    # Rename columns
    df.rename(columns={'area': 'surface_m2'}, inplace=True)

    # Sort: new listings first, then by price
    df = df.sort_values(by=['is_new', 'price'], ascending=[False, True])

    def create_email_body(df, max_rows=20):
        if df.empty:
            return "Vesteda Rentals (available):\n\nGeen beschikbare woningen gevonden."
        
        df = df.head(max_rows).copy()
        df['price_per_m2'] = df['price'] / df['surface_m2']
        df['price_per_m2'] = df['price_per_m2'].round(2)

        body = "🏢 Top Vesteda Rentals (available):\n\n"
        body += f"{'Address':<35} {'€ Rent':>8} {'m²':>5} {'€/m²':>6} {'New':>4} {'Neighborhood':>15}\n"
        body += "-" * 70 + "\n"

        for _, row in df.iterrows():
            address = row['address'][:32] + "..." if len(row['address']) > 35 else row['address']
            neighborhood = row.get('neighborhood', 'N/A')
            is_new = 'Yes' if row.get('is_new', False) else 'No'

            body += f"{address:<35} {int(row['price']):>8} {int(row['surface_m2']):>5} {row['price_per_m2']:>6.2f} {is_new:>4} {neighborhood:>15}\n"
            body += f"🔗 {row['url']}\n\n"
        
        return body

    body = create_email_body(df)
    return body

def create_ikwilhuren():
    data_path = os.path.join(parent_dir, 'data', 'huren', 'enriched_ikwilhuren_amsterdam.csv')
    df = pd.read_csv(data_path, sep=',')

    # df = df[df['address'].str.contains('Amsterdam', case=False, na=False)]
    # Parse dates
    df['date_scraped'] = pd.to_datetime(df['date_scraped'], errors='coerce')
    # --- Get first scraped date for each listing (using ALL rows, not just active) ---
    first_seen = df.groupby('link')['date_scraped'].min().reset_index().rename(columns={'date_scraped': 'first_scraped'})
    # --- Get latest version of each listing ---
    df = df.sort_values('date_scraped', ascending=False).drop_duplicates('link')

    # --- Now filter only the ones that are currently active ---
    df = df[(df['is_active'] == True) & (df['is_available'] == True)]

    # Merge in the first_seen date (from full dataset)
    df = df.merge(first_seen, on='link', how='left')

    # Create combined address
    df['address'] = df['address'] + ' ' + df['city']

    # Rename columns
    df.rename(columns={'surface_m2': 'surface_area_m2', 'price_per_month': 'price_per_month'}, inplace=True)

    # Clean and compute derived columns
    df = df.sort_values(by='price_per_month', ascending=True)
    df['price_per_m2'] = df['price_per_month'] / df['surface_area_m2']

    df = df.dropna(subset=['address', 'price_per_month', 'surface_area_m2', 'price_per_m2', 'link'])

    def create_email_body(df, max_rows=10):
        df = df.head(max_rows).copy()
        df['price_per_m2'] = df['price_per_m2'].round(2)

        # Clean up notes
        df['available_from_note'] = df['available_from_note'].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()

        body = "🏢 Ik wil huren (MVGM - Top Rentals - available):\n\n"
        body += f"{'Address':<35} {'€ Rent':>8} {'m²':>5} {'€/m²':>6} {'Neighborhood':>15}\n"
        body += "-" * 70 + "\n"

        for _, row in df.iterrows():
            address = row['address'][:32] + "..." if len(row['address']) > 35 else row['address']
            first_scraped = row['first_scraped'].date() if pd.notnull(row['first_scraped']) else 'N/A'
            available_note = row['available_from_note'] if pd.notnull(row['available_from_note']) else 'N/A'
            is_new = str(row['is_new']) if 'is_new' in row and pd.notnull(row['is_new']) else 'N/A'
            neighborhood = row.get('neighborhood', 'N/A')

            body += f"{address:<35} {int(row['price_per_month']):>8} {int(row['surface_area_m2']):>5} {row['price_per_m2']:>6.2f} {neighborhood:>15}\n"
            body += f"🔗 {row['link']}\n"
            body += f"📅 First scraped: {first_scraped} | 🆕 New: {is_new}\n"
            body += f"📌 Beschikbaar: {available_note}\n\n"

        return body
    body = create_email_body(df)
    return body

def run_pipeline(rental_company='vbt_huren'):
    logging.info(f"[START] Sending email for {rental_company}...")  

    body_dict = {
        'vbt_huren': create_vbt_body,
        'bouwinvest': create_bouwinvest_body,
        'vesteda': create_vesteda_body,
        "ikwilhuren": create_ikwilhuren,  # Assuming ikwilhuren uses the same body as vbt_huren
        # 'funda': create_body
    }

    body = body_dict.get(rental_company, create_vbt_body)()

    # to_email = 'bramgriffioen98@gmail.com, rianne.boon@hotmail.com'
    to_email = 'bramgriffioen98@gmail.com'

    today = pd.Timestamp.now().strftime('%Y-%m-%d')
    subject = f"{rental_company} - Dagelijkse huurwoningen in Amsterdam - {today}"
    # body = 'This is a test email sent from Python using Gmail.'
    gmail_user = 'bramgriffioen98@gmail.com'
    send_gmail(to_email, subject, body, gmail_user) 
    
    logging.info(f"[END] Email sent for {rental_company}.") 
    return body

if __name__ == "__main__":
    body = run_pipeline(rental_company='ikwilhuren')
    print(body)


# File: src/rental\vbt_huren.py
# %%
# scraper.py
import os
import time
import re
import tempfile
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "huren")
BASE_URL = "https://vbtverhuurmakelaars.nl/woningen"
EDGE_DRIVER_PATH = r"C:\Users\bgriffioen\OneDrive - STX Commodities B.V\Desktop\funda-project\funda-tool\src\utils\msedgedriver.exe"

def get_driver(local=False):
    # Common browser arguments
    def add_common_options(opts):
        opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--window-size=1920,1080")
        temp_profile_dir = tempfile.mkdtemp()
        opts.add_argument(f"--user-data-dir={temp_profile_dir}")
        return opts

    if local:
        options = add_common_options(EdgeOptions())
        options.use_chromium = True
        service = EdgeService(executable_path=EDGE_DRIVER_PATH)
        driver = webdriver.Edge(service=service, options=options)
    else:
        options = add_common_options(ChromeOptions())
        service = ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    return driver


def accept_cookies(driver):
    driver.execute_script("""
        const iframe = document.querySelector('iframe.trengo-vue-iframe');
        if (iframe) iframe.style.display = 'none';
    """)
    try:
        button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.button.accept.show-nadvanced.svelte-19xnkg3"))
        )
        driver.execute_script("arguments[0].click();", button)
    except TimeoutException:
        logging.warning("Accept cookies button not found or not clickable. Continuing without accepting cookies.")

def page_settings(driver):
    for attempt in range(3):
        try:
            city_input = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="city"]'))
            )
            city_input.clear()
            city_input.send_keys("Amsterdam")

            price_dropdown = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "priceRental-max"))
            )
            Select(price_dropdown).select_by_value("2000")
            break
        except StaleElementReferenceException:
            logging.info(f"[INFO] Stale element on attempt {attempt+1}, retrying...")
            time.sleep(1)

def parse_property_cards(html):
    soup = BeautifulSoup(html, 'html.parser')
    properties = []

    for listing in soup.select('a.property'):
        prop = {
            'status': listing.select_one('div').get_text(strip=True),
            'city': "Amsterdam",
            'address': listing.select_one('span.normal').get_text(strip=True),
            'price_per_month': int(
                listing.select_one('div.price').get_text(strip=True)
                .replace('€', '').replace(',-', '').replace('.', '').strip()
            )
        }

        rows = listing.select('table tr')
        for row in rows:
            cells = row.select('td')
            if len(cells) < 2:
                continue
            key, value = cells[0].get_text(strip=True), cells[1].get_text(strip=True)
            if key == "Soort object":
                prop['type'] = value
            elif key == "Woonoppervlakte":
                prop['surface_area_m2'] = int(value.replace("m²", "").strip())
            elif key == "Kamers":
                prop['rooms'] = int(value.split()[0])
            elif key == "Servicekosten":
                prop['service_costs_per_month'] = int(value.replace('€', '').replace(',-', '').replace('per maand', '').strip())
            elif key == "Huurtermijn (min.)":
                prop['minimum_lease_term_months'] = int(value.replace("Maanden", "").strip())
            elif key == "Beschikbaar":
                prop['available_from'] = value
            elif key == "Aantal reacties":
                prop['number_of_responses'] = int(value)

        note = listing.select_one('p.nomore')
        prop['note'] = note.get_text(strip=True) if note else ''
        prop['is_available'] = False if note else True

        style = listing.select_one('.visimage')['style']
        prop['image_url'] = style.split('url(')[1].split(')')[0]
        prop['detail_url'] = listing['href']

        status_map = {
            'Beschikbaar': 'Beschikbaar',
            'iDeze woning is momenteel aangeboden aan een kandidaat. Je kunt nog reageren op deze woning, je komt dan op de wachtlijst.Aangeboden': 'Aangeboden',
            'iDeze woning is verhuurd. Je kunt niet meer reageren op deze woning.Verhuurd': 'Verhuurd'
        }
        prop['status'] = status_map.get(prop['status'], prop['status'])
        # change beschikbaar to True 
        beschikbaar_map = {
            'Beschikbaar': True,
            'Aangeboden': False,
            'Verhuurd': False
        }
        prop['is_available'] = beschikbaar_map.get(prop['status'], False)
        
        properties.append(prop)

    return properties

def extract_coordinates(html):
    cleaned = html.replace('\\u002F', '/')
    matches = re.findall(r'coordinate\s*:\s*\[\s*(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)\s*\]', cleaned)
    return [{'longitude': float(lon), 'latitude': float(lat)} for lon, lat in matches]


# def get_neighborhoods_from_coordinates(df):
#     from geopy.geocoders import Nominatim
#     from geopy.extra.rate_limiter import RateLimiter

#     df['lat_lon'] = list(zip(df['latitude'].round(5), df['longitude'].round(5)))
#     unique_coords = df['lat_lon'].dropna().unique()

#     geolocator = Nominatim(user_agent="amsterdam-housing-scraper")
#     geocode = RateLimiter(geolocator.reverse, min_delay_seconds=1, error_wait_seconds=2, swallow_exceptions=True)

#     coord_to_neighborhood = {}
#     for coord in unique_coords:
#         try:
#             location = geocode(coord, exactly_one=True, language="nl")
#             if location and hasattr(location, "raw"):
#                 suburb = location.raw.get("address", {}).get("suburb", "")
#                 wijk = location.raw.get("address", {}).get("neighbourhood", "")
#                 buurt = location.raw.get("address", {}).get("quarter", "")
#                 coord_to_neighborhood[coord] = suburb or wijk or buurt or ""
#             else:
#                 coord_to_neighborhood[coord] = ""
#         except Exception:
#             coord_to_neighborhood[coord] = ""

#     df['neighborhood'] = df['lat_lon'].map(coord_to_neighborhood)
#     df.drop(columns=['lat_lon'], inplace=True)
#     return df

def get_neighborhoods_from_coordinates(df):
    import os
    import json
    from pathlib import Path
    from shapely.geometry import Point, Polygon

    # Load neighborhoods geojson
    current_dir = Path(__file__).resolve().parent
    parent_dir = current_dir.parent.parent
    json_path = os.path.join(parent_dir, 'data', 'neighborhoods_amsterdam.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        geojson = json.load(f)

    # Prepare polygons
    neighborhoods = []
    for feature in geojson['features']:
        name = feature['properties'].get('neighborhood', '')
        coords = feature['geometry']['coordinates']
        # Handle both Polygon and MultiPolygon
        if feature['geometry']['type'] == 'Polygon':
            polygons = [Polygon(coords[0])]
        elif feature['geometry']['type'] == 'MultiPolygon':
            polygons = [Polygon(poly[0]) for poly in coords]
        else:
            continue
        neighborhoods.append((name, polygons))

    def find_neighborhood(lat, lon):
        point = Point(lon, lat)
        for name, polygons in neighborhoods:
            for poly in polygons:
                if poly.contains(point):
                    return name
        return ""

    df['neighborhood'] = df.apply(
        lambda row: find_neighborhood(row['latitude'], row['longitude'])
        if pd.notnull(row.get('latitude')) and pd.notnull(row.get('longitude')) else "",
        axis=1
    )
    return df


def get_preference_from_coordinates(df):
    import os
    import json
    from pathlib import Path
    from shapely.geometry import Point, Polygon

    # Load preference geojson
    current_dir = Path(__file__).resolve().parent
    parent_dir = current_dir.parent.parent
    json_path = os.path.join(parent_dir, 'data', 'preference.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        geojson = json.load(f)

    # Prepare polygons
    preferences = []
    for feature in geojson['features']:
        name = feature['properties'].get('preference', '')
        coords = feature['geometry']['coordinates']
        # Handle both Polygon and MultiPolygon
        if feature['geometry']['type'] == 'Polygon':
            polygons = [Polygon(coords[0])]
        elif feature['geometry']['type'] == 'MultiPolygon':
            polygons = [Polygon(poly[0]) for poly in coords]
        else:
            continue
        preferences.append((name, polygons))

    def is_in_preference(lat, lon):
        point = Point(lon, lat)
        for name, polygons in preferences:
            for poly in polygons:
                if poly.contains(point):
                    return True
        return False

    df['preference'] = df.apply(
        lambda row: is_in_preference(row['latitude'], row['longitude'])
        if pd.notnull(row.get('latitude')) and pd.notnull(row.get('longitude')) else False,
        axis=1
    )
    return df


def scrape_all_pages(driver, max_pages=100):
    df = pd.DataFrame()
    for page_num in range(1, max_pages + 1):
        page_url = f"{BASE_URL}/{page_num}" if page_num > 1 else BASE_URL
        driver.get(page_url)
        time.sleep(1)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        if soup.select_one("div.wrapped > h1") and "Helaas, deze pagina is niet" in soup.text:
            logging.info(f"Page {page_num} not available, stopping.")
            break

        properties = parse_property_cards(html)
        if not properties:
            logging.info(f"[INFO] No properties on page {page_num}, stopping.")
            break

        coordinates = extract_coordinates(html)
        if len(coordinates) == len(properties):
            for i, prop in enumerate(properties):
                prop.update(coordinates[i])

        df = pd.concat([df, pd.DataFrame(properties)], ignore_index=True)
        df['date_time_scraped'] = pd.Timestamp.now()
    return df

def run_pipeline(local  = False):
    logging.info("[START] Scraping VBT Verhuur Makelaars properties in Amsterdam...")
    driver = get_driver(local=local)
    try:
        driver.get(BASE_URL)
        accept_cookies(driver)
        page_settings(driver)
        df = scrape_all_pages(driver)
        df = get_neighborhoods_from_coordinates(df)
        df = get_preference_from_coordinates(df)

        df['price_per_m2'] = df['price_per_month'] / df['surface_area_m2']

        df_old = pd.read_csv(f"{OUTPUT_DIR}/properties_amsterdam.csv") if os.path.exists(f"{OUTPUT_DIR}/properties_amsterdam.csv") else pd.DataFrame()
        if not df_old.empty:
            df = pd.concat([df_old, df]).drop_duplicates(subset=['detail_url'], keep='last').reset_index(drop=True)
        df.to_csv(f"{OUTPUT_DIR}/properties_amsterdam.csv", index=False)
        logging.info(f"[DONE] Scraped {len(df)} properties and saved to CSV.")
    finally:
        driver.quit()

    logging.info("[END] Scraping completed.")

if __name__ == "__main__":
    run_pipeline(local=True)


# File: src/rental\vesteda.py
# %%
# scraper.py
import os
import time
import re
import tempfile
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

NAME = "vesteda"
CITY = "amsterdam"

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "huren")
BASE_URL = "https://hurenbij.vesteda.com/login"

EDGE_DRIVER_PATH = r"C:\Users\bgriffioen\OneDrive - STX Commodities B.V\Desktop\funda-project\funda-tool\src\utils\msedgedriver.exe"

def get_driver(local=False):
    # Common browser arguments
    def add_common_options(opts):
        opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--window-size=1920,1080")
        temp_profile_dir = tempfile.mkdtemp()
        opts.add_argument(f"--user-data-dir={temp_profile_dir}")
        return opts

    if local:
        options = add_common_options(EdgeOptions())
        options.use_chromium = True
        service = EdgeService(executable_path=EDGE_DRIVER_PATH)
        driver = webdriver.Edge(service=service, options=options)
    else:
        options = add_common_options(ChromeOptions())
        service = ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    return driver

def extract_listings(html):
    soup = BeautifulSoup(html, 'html.parser')
    listings = []

    cards = soup.select('div.card.card-result-list')

    for card in cards:
        # Address
        address_tag = card.select_one('h5.card-title a')
        address = address_tag.text.strip() if address_tag else None

        # Location
        location_tag = card.select_one('div.card-text')
        location = location_tag.text.strip() if location_tag else None

        # Price
        price_tag = card.select_one('div.object-price .value')
        price = price_tag.text.strip() if price_tag else None

        # Rooms
        rooms_tag = card.select_one('div.object-rooms .value')
        rooms = rooms_tag.text.strip() if rooms_tag else None

        # Area
        area_tag = card.select_one('div.object-area .value')
        area = area_tag.text.strip() if area_tag else None

        # Link (relative)
        link = address_tag['href'] if address_tag and address_tag.has_attr('href') else None

        # Status note
        note_tag = card.select_one('div.card-body.pt-0 p.text-muted')
        status_note = note_tag.text.strip() if note_tag else None

        # Build dictionary
        listings.append({
            'address': address,
            'location': location,
            'price': price,
            'rooms': rooms,
            'area': area,
            'link': link,
            'status_note': status_note
        })

    return listings

def login_vesteda(driver, user_name, password):
    wait = WebDriverWait(driver, 5)

    # Step 1: Reject cookies if shown
    try:
        reject_button = wait.until(EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyButtonDecline")))
        reject_button.click()
    except:
        pass

    attempt = 0
    max_attempts = 3

    while attempt < max_attempts:
        attempt += 1

        try:
            # Fill email twice for safety
            for _ in range(2):
                email_input = wait.until(EC.element_to_be_clickable((By.NAME, "txtEmail")))
                email_input.clear()
                email_input.send_keys(user_name)
                ActionChains(driver).move_to_element(email_input).send_keys(Keys.TAB).perform()

            # Fill password
            password_input = wait.until(EC.element_to_be_clickable((By.NAME, "txtWachtwoord")))
            password_input.clear()
            password_input.send_keys(password)

            # Submit using RETURN key
            login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            login_button.send_keys(Keys.RETURN)

            # Wait briefly for login result to render
            time.sleep(2)

            alerts = driver.find_elements(By.CSS_SELECTOR, "div.alert.alert-info.alert-dismissible")
            for alert in alerts:
                if "welkom" in alert.text.lower():
                    print(f"✅ Login successful on attempt {attempt}")
                    break  # ← this breaks the for-loop
            else:
                print(f"⚠️ Login attempt {attempt} failed. Retrying...")
                continue  # Only runs if no alert matched

            break  # ← this breaks the while-loop if "Welkom" was found

        except (TimeoutException, NoSuchElementException):
            pass  # Try again if something went wrong

        print(f"⚠️ Login attempt {attempt} failed. Retrying...")


def process_data(dict):
    df = pd.DataFrame(dict)

    # Convert 'price' to integer
    df['price'] = df['price'].str.replace(',-', '').str.replace('.', '',
                                                regex=False).astype(int)

    # /object/8aa1d02b7b8115234913b26207d6120b/ to https://hurenbij.vesteda.com/object/8aa1d02b7b8115234913b26207d6120b/
    df['link'] = df['link'].apply(lambda x: f"https://hurenbij.vesteda.com{x}" if x else None)

    # area 93 m2 to 93
    df['area'] = df['area'].str.replace(' m2', '').astype(int)
    df['status_note'].unique()

    # array(['Voor deze woning zijn al veel bezichtigingsaanvragen binnen. Vergroot uw kans door een andere woning te selecteren.'],
        #   dtype=object) if this is the case make is_available False else True
    df['is_available'] = df['status_note'].apply(
        lambda x: False if "al veel bezichtigingsaanvragen" in x else True)
    # drop status_note
    df = df.drop(columns=['status_note'])

    df['price'] = df['price'].astype(int)

    # Convert 'area' to integer
    df['area'] = df['area'].astype(int)

    # Ensure 'is_available' is boolean
    df['is_available'] = df['is_available'].astype(bool)
    df['date_scraped'] = pd.to_datetime('now')

    return df

def run_pipeline(local=False):
    logging.info(f"[START] Scraping {NAME} properties in {CITY}...")
    load_dotenv()

    driver = get_driver(local=local)
    driver.get(BASE_URL)

    # reject_cookies(driver)
    user_name = os.getenv("VESTEDA_USER")
    password = os.getenv("VESTEDA_PASSWORD")

    wait = WebDriverWait(driver, 10)

    # Perform login
    login_vesteda(driver, user_name, password)

    driver.get("https://hurenbij.vesteda.com/zoekopdracht/")
    # Wait for the page to load
    html = driver.page_source
    dict = extract_listings(html)


    df = process_data(dict)
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "huren")
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    name = f"{NAME}_{CITY}"

    output_path = os.path.join(OUTPUT_DIR, f"{name}.csv")
    logging.info(f"Saving data to {output_path}")

    if os.path.exists(output_path):
        df_old = pd.read_csv(output_path)
        # Mark all old entries as is_new = False
        df_old['is_new'] = False
        # Mark new entries as is_new = True if their link is not in old data
        df['is_new'] = ~df['link'].isin(df_old['link'])
        # Combine old and new, keeping all unique links, with new entries marked correctly
        df_combined = pd.concat([df_old, df[df['is_new']]], ignore_index=True).drop_duplicates(subset=['link'], keep='last')
    else:
        df['is_new'] = True
        df_combined = df

    df_combined.to_csv(output_path, index=False)
    logging.info(f"Data saved to {output_path}")

    driver.quit()
    logging.info(f"[END] Scraping completed for {NAME} in {CITY}.") 
    
if __name__ == "__main__":
    run_pipeline()

