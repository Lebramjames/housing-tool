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

from src.utils import *
from src.utils.config import logging

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "huren")
BASE_URL = "https://vbtverhuurmakelaars.nl/woningen"
EDGE_DRIVER_PATH = os.getenv("EDGE_DRIVER_PATH", "msedgedriver")

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
            'iDeze woning is verhuurd. Je kunt niet meer reageren op deze woning.Verhuurd': 'Verhuurd',
            "Er zijn reeds meer dan 200 reacties op deze woning. Reageren is op dit moment niet mogelijk.": "Verhuurd"
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




def finalize_dataframe(df):

    df['address_full'] = df['address'] + ', ' + df['city']
    df['street'] = df['address'].apply(lambda x: re.match(r"^(.*?)(\d)", x).group(1).strip() if re.match(r"^(.*?)(\d)", x) else x)
    df['price'] = df['price_per_month']
    df['squared_m2'] = df['surface_area_m2'].astype(float)
    df['price_per_squared_m2'] = df['price'] / df['squared_m2']
    df['is_available'] = df['is_available']

    # is available from available_from (currently in Dutch convert to DD/MM/YYYY)
    df['available_from'] = pd.to_datetime(df['available_from'], errors='coerce', format='%d-%m-%Y').dt.strftime('%d/%m/%Y')

    df['note'] = df['note']

    df['link'] = 'https://vbtverhuurmakelaars.nl' + df['detail_url']
    df['rental_company'] = 'vbt_verhuurmakelaars'
    df['date_scraped'] = pd.Timestamp.now()

    required_columns = [
        'address_full',
        'street',
        'price',
        'squared_m2',
        'price_per_squared_m2',
        'is_available',
        'note',
        'date_scraped',
        'link',
        'available_from',
        'rental_company'
    ]

    df = df[required_columns]
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
        df = finalize_dataframe(df)

        append_row_to_sheet(df, RENTAL_DB)
        logging.info(f"[DONE] Scraped {len(df)} properties and saved to CSV.")
    finally:
        driver.quit()

    logging.info("[END] Scraping completed.")

if __name__ == "__main__":
    run_pipeline(local=True)
