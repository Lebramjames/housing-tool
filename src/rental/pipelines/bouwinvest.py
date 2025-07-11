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

from src.utils import *
from src.utils.config import logging

# --- CONFIG ---
BASE_URL = "https://www.wonenbijbouwinvest.nl/"
CITY = "Amsterdam"
MAX_PAGES = 10
GEOCODE_API = os.getenv("GEOCODE_API")  # Set your Maps.co key as env var
OUTPUT_DIR = os.path.join(os.getcwd(), "data", "huren")
USE_EDGE = True
HEADLESS = True

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
                "url": listing.find("a", href=True)['href']
            })
        except Exception as e:
            logging.warning(f"Failed to parse a listing: {e}")
    return data


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


def finalize_dataframe(df):
    # columns to be filled in 
    # address_full	street	price	squared_m2	price_per_squared_m2	is_available	note	date_scraped	link	available_from	rental_company	is_new

    df['address_full'] = df['address'] + ', ' + df['location']
    # df['street'] = df['address'] (only retrieve the part up to the first number value)

    def extract_street(address):
        match = re.match(r"^(.*?)(\d)", address)
        return match.group(1).strip() if match else address
    df['street'] = df['address'].apply(extract_street)

    df['is_available'] = df['availability'].apply(lambda x: 'Beschikbaar' in x)
    df['note'] = None
    df['date_scraped'] = pd.Timestamp.now()
    df['link'] = df['url']
    # df['available_from'] = df['availability'].apply(retreive DD/MM/YYYY from the availability string)
    df['available_from'] = df['availability'].str.extract(r'(\d{1,2}/\d{1,2}/\d{4})')[0]
    df['rental_company'] = 'bouwinvest'

    # keep the order of the columns
    df = df[['address_full', 'street', 'price', 'surface_m2', 'price_per_m2', 'is_available', 'note', 'date_scraped', 'link', 'available_from', 'rental_company']]
    return df
    
def run_pipeline(local = False):
    logging.info('[START] Scraping Bouwinvest properties in Amsterdam...')
    df = scrape_bouwinvest(CITY, local=local)
    df = finalize_dataframe(df)
    append_row_to_sheet(df, RENTAL_DB)
    return df

if __name__ == "__main__":
    df = run_pipeline(local=True)
    logging.info("Bouwinvest scraper completed successfully.")
