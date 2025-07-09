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
BASE_URL = "https://www.wonenbijbouwinvest.nl/"
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

def accept_cookies():
    from selenium.webdriver.common.keys import Keys
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
        ).click()
        logging.info("Cookies accepted.")
    except TimeoutException:
        logging.warning("Cookie button not found or already accepted.")

accept_cookies()

from selenium.webdriver.common.keys import Keys

def search_location(location):
    try:
        # Wait for and enter the location
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "query"))
        )
        search_input.clear()
        search_input.send_keys(location)
        search_input.send_keys(Keys.ENTER)  # <-- Press Enter here
        logging.info(f"Location entered and Enter pressed: {location}")

    except TimeoutException as e:
        logging.warning(f"Search input failed: {e}")




driver = get_driver(local=True)
driver.get(BASE_URL)
search_location("Amsterdam")

def extract_listings_from_html(html):
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    listings = soup.find_all("div", class_="projectproperty-tile")
    data = []

    for listing in listings:
        try:
            # Title
            title_tag = listing.find("span", class_="h2")
            title = title_tag.get_text(strip=True) if title_tag else None

            # Location
            location_tag = listing.find("span", class_="paragraph fw-light")
            location = location_tag.get_text(strip=True) if location_tag else None

            # Description
            desc_tag = listing.find("span", class_="paragraph")
            description = desc_tag.get_text(strip=True) if desc_tag else None

            # Availability
            availability_tag = listing.find("span", class_=re.compile("bar__top"))
            availability = availability_tag.get_text(strip=True) if availability_tag else None

            # Surface area
            surface_tag = listing.find("span", class_="facet icon-surface")
            surface = surface_tag.get_text(strip=True).replace("M²", "").strip() if surface_tag else None

            # Bedrooms
            beds_tag = listing.find("span", class_="facet icon-total_sleepingrooms")
            bedrooms = beds_tag.get_text(strip=True).replace("slaapkamers", "").strip() if beds_tag else None

            # Price
            price_tag = listing.find("span", class_="price-tag")
            price = price_tag.get_text(strip=True) if price_tag else None

            # Link
            link_tag = listing.find("a", href=True)
            url = "https://www.wonenbijbouwinvest.nl" + link_tag['href'] if link_tag else None

            data.append({
                "title": title,
                "location": location,
                "description": description,
                "availability": availability,
                "surface_m2": surface,
                "bedrooms": bedrooms,
                "price": price,
                "url": url
            })

        except Exception as e:
            print(f"Error parsing listing: {e}")
            continue

    return data


from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

all_data = []

while True:
    # Wait for listings to load (adjust selector if needed)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "projectproperty-tile"))
        )
    except TimeoutException:
        print("Timed out waiting for listings to load.")
        break

    # Parse and extract listings
    html = driver.page_source
    listings = extract_listings_from_html(html)
    all_data.extend(listings)
    print(f"Extracted {len(listings)} listings from current page.")

    # Try clicking the 'Volgende' button
    try:
        next_button = driver.find_element(By.LINK_TEXT, "Volgende")
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        time.sleep(1)
        next_button.click()
        time.sleep(3)  # let next page load
    except NoSuchElementException:
        print("No more pages.")
        break

# %%
BASE_URL = "https://www.wonenbijbouwinvest.nl/huuraanbod?query=Amsterdam&page={}"
MAX_PAGES = 10  # You can increase or stop dynamically if needed

all_data = []

# Step 1: Extract listings from the current (first) page
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "projectproperty-tile"))
    )
    html = driver.page_source
    listings = extract_listings_from_html(html)
    all_data.extend(listings)
    print(f"Page 1: extracted {len(listings)} listings.")
except TimeoutException:
    print("Failed to load first page.")

# Step 2: Loop through pages 2 to N
for page in range(2, MAX_PAGES + 1):
    url = BASE_URL.format(page)
    print(f"Scraping page {page}: {url}")
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "projectproperty-tile"))
        )
    except TimeoutException:
        print(f"No listings found on page {page}, stopping.")
        break

    html = driver.page_source
    listings = extract_listings_from_html(html)

    if not listings:
        print(f"No listings found on page {page}, stopping.")
        break

    all_data.extend(listings)
    print(f"Page {page}: extracted {len(listings)} listings.")
df = pd.DataFrame(all_data)
df['price'] = df['price'].str.replace('€', '').str.replace(' per maand', '').str.replace('.', '').astype(int)
df['price_per_m2'] = df['price'] / df['surface_m2'].astype(float)
df.rename(columns={
    'title': 'adress'}, inplace=True)


def geocode_forward(df):
    import requests

    GEOCODE_API = os.getenv('GEOCODE_API')

    lats = []
    lons = []

    for idx, row in df.iterrows():
        # Combine address and location for better geocoding
        address = row['adress']
        location = row.get('location', '')
        # If location is not empty and not already in address, append it
        if location and location.lower() not in address.lower():
            full_address = f"{address}, {location}"
        else:
            full_address = address

        url = f"https://geocode.maps.co/search?q={full_address}&api_key={GEOCODE_API}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                lats.append(data[0].get('lat'))
                lons.append(data[0].get('lon'))
            else:
                lats.append(None)
                lons.append(None)
        else:
            lats.append(None)
            lons.append(None)

    df['lat'] = lats
    df['lon'] = lons
    return df

try:
    df = geocode_forward(df)
except Exception as e:
    print(f"Geocoding failed: {e}")
    df['lat'] = None
    df['lon'] = None


from vbt_huren import get_neighborhoods_from_coordinates, get_preference_from_coordinates

df = get_neighborhoods_from_coordinates(df)
df = get_preference_from_coordinates(df)
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
                "adress": listing.find("span", class_="h2").get_text(strip=True),
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
        address = row['adress']
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
def scrape_bouwinvest(city):
    driver = get_driver(local=True)
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

def run_pipeline():
    df = scrape_bouwinvest(CITY)
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

    print(df.head())

if __name__ == "__main__":
    run_pipeline()
    logging.info("Bouwinvest scraper completed successfully.")
