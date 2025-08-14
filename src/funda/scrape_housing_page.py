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

import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from src.funda.clean_housing_page import clean_company_scrape

from src.funda.information_extracter import (
    extract_indeling_info,
    extract_kadastrale_info_from_flat_html,
    extract_listing_data,
    extract_energy_label,
    extract_overdracht_from_json_block,
    extract_surface_areas,
    extract_popularity_data,
    extract_omschrijving,
    extract_neighborhood_block,
    extract_company_information
)

from src.funda.page_scraper import get_valid_html_versions

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



def extract_all(local = False):
    today = pd.Timestamp.now().strftime('%Y-%m-%d')

    input_path = os.path.join(os.getcwd(), 'data', "funda", "raw", f'raw_funda_main_data_{today}.csv')
    df = pd.read_csv(input_path)

    df.sort_values(by='price/m2', inplace=True)
    df_working = df.copy()

    max_tries = 3
    counter = 0

    if local == True:
    # use local msedgedriver.exe
        service = Service('C:/Users/bgriffioen/OneDrive - STX Commodities B.V/Desktop/funda-project/funda-tool/msedgedriver.exe')
    else:   
        service = Service(ChromeDriverManager().install())

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

    output_path = os.path.join(os.getcwd(), 'data', 'funda', f'funda_data_{today}.csv')
    # sort based on idx in df_working
    df_working = df_working.reset_index(drop=True)

    df_final = pd.DataFrame()

    for idx, row in df_working.iterrows():
        if idx % 10 == 0:
            logging.info(f"Processing row {idx}/{len(df_working)}")
        url = row['url']


        for attempt in range(3):
            try:
                html = get_valid_html_versions(url, service=service, options=options)
                indeling_info = extract_indeling_info(html)
                kadaster_info = extract_kadastrale_info_from_flat_html(html)
                listing_data = extract_listing_data(html)
                energy_label = extract_energy_label(html)
                overdracht_info = extract_overdracht_from_json_block(html)
                surface_info = extract_surface_areas(html)
                popularity_data = extract_popularity_data(html)
                omschrijving = extract_omschrijving(html)
                buurt_info = extract_neighborhood_block(html)

                # Combine all extracted data
                flat_data = {}
                for key, value in {
                    "indeling": indeling_info,
                    "kadaster": kadaster_info,
                    "listing_data": listing_data,
                    "overdracht": overdracht_info,
                    "surface": surface_info,
                    "popularity": popularity_data,
                    "omschrijving": omschrijving,
                    "buurt": buurt_info
                }.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            flat_data[f"{key}_{sub_key}"] = sub_value
                    else:
                        flat_data[key] = value

                flat_data["energy_label"] = energy_label
                for col, val in flat_data.items():
                    df_working.at[idx, col] = val

                df_final = pd.concat([df_final, df_working.iloc[[idx]]], ignore_index=True)
                df_final.drop_duplicates(subset=['url'], keep='last', inplace=True)
                df_final.to_csv(output_path, index=False, sep=';')
                break  # Break out of retry loop after success

            except Exception as e:
                logging.warning(f"⚠️ Error on attempt {attempt + 1} for {url}: {e}")
                if attempt == 2:
                    logging.error(f"⛔ Max retries reached for {url}. Skipping.")
                continue
        


    df_working.to_csv(output_path, index=False)
    logging.info(f"🔄 Saved output to {output_path}")


def run_housing_scrape_pipeline():
    """
    Main function to run the housing scrape pipeline.
    """
    logging.info("Starting housing scrape pipeline...")
    extract_company_information(local=True)  # Set to True for local testing, False for production use
    logging.info("Housing scrape pipeline completed successfully.")
    clean_company_scrape()  # Assuming this function is defined in another module

if __name__ == "__main__":
    run_housing_scrape_pipeline()  # Set to True for local testing, False for production use
    logging.info("Scraping completed successfully.")