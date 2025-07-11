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

from src.utils import *
from src.utils.config import logging

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

NAME = "ikwilhuren"
CITY = "amsterdam"

BASE_URL = "https://ikwilhuren.nu/"
EDGE_DRIVER_PATH = os.getenv("EDGE_DRIVER_PATH", "msedgedriver")
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
            logging.warning(f"Poging {attempt + 1} om gemeente te selecteren mislukt")
        else:
            logging.info(f"Gemeente '{gemeente_naam}' geselecteerd bij poging {attempt + 1}")
            break


def finalize_dataframe(df):
    # columns to be filled in 
    # address_full	street	price	squared_m2	price_per_squared_m2	is_available	note	date_scraped	link	available_from	rental_company	is_new

    df['address_full'] = df['address'] + ', ' + df['city']
    df['price'] = df['price_per_month']
    df['surface_m2'] = df['surface_m2'].astype(float)
    df['price_per_m2'] = df['price'] / df['surface_m2']
    df['street'] = df['address'].apply(lambda x: re.match(r"^(.*?)(\d)", x).group(1).strip() if re.match(r"^(.*?)(\d)", x) else x)
    df['is_available'] = df['status'].apply(lambda x: True if x and 'Te huur' in x else False)
    df['note'] = df['available_from_note']
    df['link'] = df['details_url']
    df['date_scraped'] = pd.Timestamp.now()

    df['rental_company'] = NAME
    # retrieve available_from string in DD/MM/YYYY format using regex
    df['available_from_date'] = df['available_from_date'].str.extract(r'(\d{1,2}-\d{1,2}-\d{4})')[0]
    # Add date_scraped column
    df['date_scraped'] = pd.Timestamp.now()
    # drop the rest of the columsn  
    df = df[['address_full', 'street', 'price', 'surface_m2', 'price_per_m2', 'is_available', 'note', 'date_scraped', 'link', 'available_from_date', 'rental_company']]
    return df

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

    df = finalize_dataframe(df)

    append_row_to_sheet(df, RENTAL_DB)
    return df


    

if __name__ == "__main__":
    df = run_pipeline(local=True)
    logging.info(f"[END] Scraping completed for {NAME} in {CITY}.")