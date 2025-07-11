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

from src.utils import *
from src.utils.config import logging

NAME = "vesteda"
CITY = "amsterdam"

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "huren")
BASE_URL = "https://hurenbij.vesteda.com/login"

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


def finalize_dataframe(data):
    df = pd.DataFrame(data)
    df['price'] = df['price'].str.replace(',-', '').str.replace('.', '',
                                                regex=False).astype(int)

    df['link'] = df['link'].apply(lambda x: f"https://hurenbij.vesteda.com{x}" if x else None)
    df['address_full'] = df['address'] + ', ' + df['location']
    df['street'] = df['address'].apply(lambda x: re.match(r"^(.*?)(\d)", x).group(1).strip() if re.match(r"^(.*?)(\d)", x) else x)
    df['squared_m2'] = df['area'].str.replace(' m2', '').astype(int)
    df['price_per_m2'] = df['price'] / df['squared_m2']
    df['is_available'] = df['status_note'].apply(lambda x: True if x and 'Beschikbaar' in x else False)
    df['note'] = df['status_note']
    df['date_scraped'] = pd.Timestamp.now()
    df['rental_company'] = NAME    
    df['available_from_date']  = None

    df = df[['address_full', 'street', 'price', 'squared_m2', 'price_per_m2', 'is_available', 'note', 'date_scraped', 'link', 'available_from_date', 'rental_company']]
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
    driver.quit()
    dict = extract_listings(html)

    df = finalize_dataframe(dict)

    append_row_to_sheet(df, RENTAL_DB)

    logging.info(f"[END] Scraping completed for {NAME} in {CITY}.") 
    
if __name__ == "__main__":
    run_pipeline(local=True)