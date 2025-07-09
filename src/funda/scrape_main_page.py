# %%
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re
import numpy as np
import urllib3

import warnings
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
pages = np.arange(1, 100)  # Adjust range for more pages if needed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MICROSOFT_DRIVER = r"C:\Users\bgriffioen\OneDrive - STX Commodities B.V\Desktop\funda-project\funda-tool\src\utils\msedgedriver.exe"

def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        logging.info(f"Successfully retrieved page: {url}")
        return response.text
    else:
        print(f"Failed to retrieve page with status code: {response.status_code}")
        return None

def get_valid_html_versions(page_number, service=None, options=None):

    url = (
        f"https://www.funda.nl/zoeken/koop?"
        f"selected_area=[%22amsterdam/straat-willem-de-zwijgerlaan,2km%22]"
        f"&page={page_number}&price=%220-500000%22"
        f"&object_type=[%22apartment%22]&search_result=1"
    )
    logging.info(f"Fetching page {page_number} from URL: {url}")

    # Try with requests first
    html_req = get_html(url)
    if html_req and "<title>Je bent bijna op de pagina die je zoekt" not in html_req and "captcha" not in html_req.lower():
        soup = BeautifulSoup(html_req, 'html.parser')
        json_ld = soup.find('script', {'type': 'application/ld+json'})
        if json_ld:
            logging.info("✅ Using HTML from requests (no Selenium needed).")
            return html_req, soup, json_ld
        else:
            logging.warning("⚠️ HTML from requests is valid but JSON-LD not found.")

    # Fallback to Selenium if needed
    try:
        pre_cookie_html = get_html_without_cookie(url=url, service=service, options=options)
        if pre_cookie_html:
            soup = BeautifulSoup(pre_cookie_html, 'html.parser')
            json_ld = soup.find('script', {'type': 'application/ld+json'})
            if json_ld:
                logging.info("✅ Using HTML from Selenium (pre-cookie).")
                return pre_cookie_html, soup, json_ld
    except Exception as e:
        logging.error(f"❌ Selenium failed to fetch page {page_number}: {e}")

    logging.error("❌ No valid HTML version with JSON-LD found after all attempts.")
    return None, None, None


def get_page_information(page_number, service=None, options=None):
    """
    Scrape the page information from Funda for a given page number.
    Args:
        page_number (int): The page number to scrape.
    Returns:
        pd.DataFrame: A DataFrame containing the scraped data.
    """
    logging.info(f"Starting to scrape page {page_number}...")

    html, soup, json_ld = get_valid_html_versions(page_number, service=service, options=options)
    # store the html file as txt file with page and date in title: 
    html_path = f"data/html_page_{page_number}_{pd.Timestamp.now().strftime('%Y%m%d')}.txt"
    if page_number == 1:
        if html:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html)
            logging.info(f"HTML content saved to {html_path}")

    logging.info("Parsing HTML to find JSON-LD script block...")
    logging.info(f"Total script tags found: {len(soup.find_all('script'))}")

    
    json_ld = soup.find('script', {'type': 'application/ld+json'})
    logging.info(f"JSON-LD script block found: {json_ld is not None}")

    if json_ld is None:
        print("No JSON-LD script block found on page.")
        return None
    if html is None:
        return None
    
    
    data = json.loads(json_ld.text)
    items = data['itemListElement']

    # Find all elements containing "k.k." (price)
    price_elements = soup.find_all(string=lambda text: "k.k." in text)
    m2_values = []

    for price_elem in price_elements:
        next_elem = price_elem.parent
        found = False
        m2_value = None
        while next_elem and not found:
            for sibling in next_elem.next_siblings:
                if hasattr(sibling, 'get_text'):
                    text = sibling.get_text()
                else:
                    text = str(sibling)
                if "m²" in text:
                    match = re.search(r'(\d+)\s*m²', text)
                    if match:
                        m2_value = match.group(1)
                    found = True
                    break
            next_elem = next_elem.next_element if not found else None
        m2_values.append(m2_value)

    results = []
    for item in items:
        try:
            detail_url = item['url']
            # Extract the last part after 'appartement-' and before the trailing slash
            match = re.search(r'appartement-([^-/]+(?:-[^-/]+)*)/?', detail_url)
            if match:
                address_part = match.group(1)
                # Split on hyphens, last part is number, rest is street name
                parts = address_part.split('-')
                if len(parts) > 1:
                    street_name = ' '.join(parts[:-1]).title()
                    number = parts[-1]
                else:
                    street_name = parts[0].title()
                    number = ''
                results.append({
                    'street_name': street_name,
                    'number': number,
                    'url': detail_url
                })
        except Exception as e:
            print("Skipping due to error:", e)

    df = pd.DataFrame(results)


    # check if len is equal to the number of items
    if len(df) != len(m2_values) or len(df) != len(price_elements):
        return None

    df['m2'] = m2_values[:len(df)]
    df['price'] = [float(re.sub(r'[^\d]', '', str(p))) for p in price_elements[:len(df)]]

    df['price/m2'] = (df['price'] / df['m2'].astype(float)).round(2)

    df['street_name'] = df['street_name'].str.replace('Appartement ', '', regex=False)
    
    def adjust_number(row):
        parts = row['street_name'].split()
        last_part = parts[-1]
        if last_part.isdigit():
            if row['number']:
                return f"{last_part}-{row['number']}"
            else:
                return last_part
        return row['number']

    # Step 1: Modify the 'number' field based on logic
    df['number'] = df.apply(adjust_number, axis=1)

    # Step 2: Remove trailing numbers from 'street_name'
    df['street_name'] = df['street_name'].str.replace(r'\s*\d+$', '', regex=True)

    # Step 3: Add city and country
    df['city'] = 'Amsterdam'
    df['country'] = 'Netherlands'
    # --- Step 2: Build full address ---
    df['full_address'] = df['street_name'] + ' ' + df['number'] + ', ' + df['city'] + ', ' + df['country']


    return df

def merge_with_existing_geo(new_df, existing_df):
    if existing_df.empty:
        print("No existing geo data found. Geocoding all new addresses.")
        return get_lat_long_information(new_df)

    # Merge to bring in lat/lon from existing dataset
    geo_cols = ['street_name', 'number', 'lat', 'lon']
    merged_df = pd.merge(
        new_df,
        existing_df[geo_cols].dropna(),
        on=['street_name', 'number'],
        how='left'
    )
    num_merged = merged_df['lat'].notna().sum()
    num_to_lookup = merged_df['lat'].isna().sum()
    print(f"{num_merged} addresses merged with existing geo data.")
    print(f"{num_to_lookup} addresses need to be geocoded.")

    # Identify rows that still need geocoding
    to_geocode = merged_df[merged_df['lat'].isna()].copy()
    if not to_geocode.empty:
        to_geocode = get_lat_long_information(to_geocode)

        # Update missing lat/lon
        merged_df.update(to_geocode[['lat', 'lon']])

    return merged_df

def get_lat_long_information(df):
    """
    Geocode addresses in the DataFrame to get latitude and longitude.
    """
    from geopy.geocoders import Nominatim
    from geopy.extra.rate_limiter import RateLimiter

    geolocator = Nominatim(user_agent="streamlit-geocoder")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    latitudes = []
    longitudes = []

    for address in df['full_address']:
        print(f"Geocoding address: {address}")
        location = geocode(address)
        if location:
            latitudes.append(location.latitude)
            longitudes.append(location.longitude)
        else:
            latitudes.append(None)
            longitudes.append(None)

    df['lat'] = latitudes
    df['lon'] = longitudes
    return df

def add_neighborhood_info(df):
    import json
    import geopandas as gpd
    from shapely.geometry import Point, shape

    with open("data/neighborhoods_amsterdam.json", "r") as f:
        geojson_data = json.load(f)

    # Convert to GeoDataFrame
    # Convert GeoJSON to GeoDataFrame
    neighborhoods_gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
    neighborhoods_gdf.set_crs(epsg=4326, inplace=True)

    # Create geometry column in df
    df['geometry'] = df.apply(lambda row: Point(row['lon'], row['lat']), axis=1)
    df_gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')

    # Spatial join to assign neighborhood
    df_gdf = gpd.sjoin(df_gdf, neighborhoods_gdf[['geometry', 'neighborhood']], how='left', predicate='within')

    # If you want to keep as DataFrame
    df = pd.DataFrame(df_gdf.drop(columns=['geometry', 'index_right']))

    # df neighborhood if emtpy print: 
    # df  for neighbordhoods that were not found add a new column with value "Unknown"
    if 'neighborhood' not in df.columns:
        df['neighborhood'] = 'Unknown'
    else:
        df['neighborhood'].fillna('Unknown', inplace=True)

    return df

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_html_without_cookie(url, service=None, options=None, local=False):

    if local ==True:
        driver = webdriver.Edge(executable_path=MICROSOFT_DRIVER, options=options)
        # make sure it is pageless 
        
    else:
        driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)
    html = driver.page_source
    driver.quit()
    return html


import os
from datetime import timedelta
import glob

def scrape_main(local = False):
    if local == True:
        from selenium.webdriver.edge.options import Options as EdgeOptions
        from selenium.webdriver.edge.service import Service as EdgeService

        service = EdgeService(MICROSOFT_DRIVER)
        options = EdgeOptions()
        options.use_chromium = True
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    else:
        service = Service(ChromeDriverManager().install())
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

    date = pd.Timestamp.now().strftime('%Y-%m-%d')
    output_path = f"data/funda/raw/raw_funda_main_data_{date}.csv"

    # Retrieve all CSV files in the directory and append, dropping duplicates

    data_dir = "data/funda"
    all_files = glob.glob(os.path.join(data_dir, "funda_data_*.csv"))
    if all_files:
        df_list = [pd.read_csv(f) for f in all_files]
        existing_df = pd.concat(df_list, ignore_index=True)
        existing_df.drop_duplicates(subset=['street_name', 'number'], inplace=True)
        yesterday_path = all_files[-1]  # Use the latest file for logging
    else:
        existing_df = pd.DataFrame()
        yesterday_path = None

    logging.info(f"Using existing data from {yesterday_path} if available.")
    logging.info(f"Output will be saved to {output_path}")
    logging.info(f"Total pages to scrape: {len(pages)}")

    logging.info(f"Checking for existing data at {yesterday_path}...")
    if not existing_df.empty:
        logging.info(f"Found existing data with {len(existing_df)} rows.")
    else:
        logging.info("No existing data found. Starting fresh scrape.")

    max_retries = 3


    if os.path.exists(output_path):
        print(f"File {output_path} already exists. Loading existing data.")
        df = pd.read_csv(output_path)
    else:
        print(f"File {output_path} does not exist. Starting fresh scrape.")
        df = pd.DataFrame()  # <-- move this up before retry loop

        for page in pages:
            success = False  # track success for this page
            for attempt in range(max_retries):
                try:
                    print(f"Processing page {page}, attempt {attempt + 1}...")
                    page_df = get_page_information(page, service=service, options=options)

                    if page_df is not None and not page_df.empty:
                        logging.info(f"✅ Page {page} processed with {len(page_df)} records.")
                        df = pd.concat([df, page_df], ignore_index=True)
                        success = True
                        break  # ✅ Successful, break retry loop
                    else:
                        logging.warning(f"⚠️ Page {page} returned no data on attempt {attempt + 1}.")
                except Exception as e:
                    logging.error(f"❌ Error processing page {page} on attempt {attempt + 1}: {e}")

            if not success:
                logging.error(f"⛔ Page {page} failed after {max_retries} attempts.")
                if page > 40:
                    logging.error(f"🛑 Stopping page loop because page {page} > 40 failed.")
                    break
                else:
                    logging.warning(f"➡️ Continuing despite failure on page {page} (page ≤ 40).")


        df.drop_duplicates(subset=['street_name', 'number'], inplace=True)
        df.reset_index(drop=True, inplace=True)
        df = merge_with_existing_geo(df, existing_df)
        df = add_neighborhood_info(df)
    
    if not df.empty:
        df.to_csv(output_path, index=False)
        print(f"Data saved to {output_path}")

if __name__ == "__main__":
    scrape_main(local=True)
    print("Scraping completed successfully!")
# %%
