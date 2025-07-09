# %%
import pandas as pd
import re

import sys
import os
# add the path src to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# verify this as well that the path is added
try :
    from src.utils.get_url import get_html
except ImportError:
    print("Error: Could not import get_html from src.utils. Please check the path.")
    sys.exit(1)

from src.utils.get_url import get_html
from src.makelaar.scrape_makelaar import run_makelaar_scraper
from src.makelaar.clean_makelaar import prepare_address_fields
from src.makelaar.geocode_addresses import geocode_addresses_with_history

def scrape_makelaar_main_page() -> pd.DataFrame:
    # results_df = run_makelaar_scraper()

    # retrieve today's results: 
    today = pd.Timestamp.now().strftime("%Y-%m-%d")
    # makelaar_results_2025-06-23
    results_df = pd.read_csv("data/makelaar/makelaar_results_" + today + ".csv")
    results_df = prepare_address_fields(results_df, full_address_col="full_adres")
    results_df = geocode_addresses_with_history(results_df)

    results_df.to_csv("data/makelaar/makelaar_results_" + today + ".csv", index=False)

if __name__ == "__main__":
    scrape_makelaar_main_page()