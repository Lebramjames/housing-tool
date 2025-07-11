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
