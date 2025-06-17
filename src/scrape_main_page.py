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


def get_page_information(page_number):
    url = f"https://www.funda.nl/zoeken/koop?selected_area=[%22amsterdam/straat-willem-de-zwijgerlaan,2km%22]&page={page_number}&price=%220-500000%22&object_type=[%22apartment%22]&search_result=1"
    html = get_html(url)

    # Extract JSON-LD data block
    soup = BeautifulSoup(html, 'html.parser')
    json_ld = soup.find('script', {'type': 'application/ld+json'})
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

import os
from datetime import timedelta

def scrape_main():

    date = pd.Timestamp.now().strftime('%Y-%m-%d')
    output_path = f"data/funda_data_{date}.csv"

    yesterday = (pd.Timestamp.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    yesterday_path = f"data/funda_data_{yesterday}.csv"

    existing_df = pd.read_csv(yesterday_path) if os.path.exists(yesterday_path) else pd.DataFrame()

    if os.path.exists(output_path):
        print(f"File {output_path} already exists. Loading existing data.")
        df = pd.read_csv(output_path)
    else:
        print(f"File {output_path} does not exist. Starting fresh scrape.")
        df = pd.DataFrame()
        counter = 0
        for page in pages:
            if counter % 10 == 0:
                print(f"Processing page {page}...")
            try:
                if page % 10 == 0:
                    print(f"Processing page {page}...")
                print(f"Processing page {page}...")
                page_df = get_page_information(page)
                if page_df is not None:
                    df = pd.concat([df, page_df], ignore_index=True)
                else:
                    print(f"Skipping page {page} due to data mismatch.")
                df = pd.concat([df, page_df], ignore_index=True)
            except Exception as e:
                print(f"Error processing page {page}: {e}")
                break
        df.drop_duplicates(subset=['street_name', 'number'], inplace=True)
        df.reset_index(drop=True, inplace=True)
        df = merge_with_existing_geo(df, existing_df)
        # df = add_neighborhood_info(df)

    if not df.empty:
        df.to_csv(output_path, index=False)
        print(f"Data saved to {output_path}")

if __name__ == "__main__":
    scrape_main()
    print("Scraping completed successfully!")
    