# %%
import pandas as pd
import re

from src.utils.get_url import get_html
from src.makelaar.scrape_makelaar import run_makelaar_scraper
from src.makelaar.clean_makelaar import prepare_address_fields
from src.makelaar.geocode_addresses import geocode_addresses_with_history

def scrape_makelaar_main_page() -> pd.DataFrame:
    results_df = run_makelaar_scraper()
    results_df = prepare_address_fields(results_df, full_address_col="full_adres")
    results_df = geocode_addresses_with_history(results_df)

    