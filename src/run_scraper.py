# %%
try:
    from src.funda import scrape_main_page
    from src.funda import scrape_company_page
    from src.funda import clean_company_scrape
except ImportError:
    from funda import scrape_main_page
    from funda import scrape_company_page
    from funda import clean_company_scrape

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



def run_makelaar_scraper():
    pass 

def run_funda_scraper():

    logging.info("Starting the Funda scraper...")
    scrape_main_page.scrape_main()
    logging.info("Scraping main page completed.")
    scrape_company_page.scrape_company_information()
    logging.info("Scraping company page completed.")
    clean_company_scrape.clean_company_scrape()

def combine_scrapers():
    pass 

def run_scraper():
    """
    Run the scraper to collect data from Funda.
    """
    run_funda_scraper()
    run_makelaar_scraper()
    combine_scrapers()

if __name__ == "__main__":
    run_scraper()
    print("All scraping tasks completed successfully!")
