# %%
try:
    from src import scrape_main_page
    from src import scrape_company_page
    from src import clean_company_scrape
except ImportError:
    import scrape_main_page
    import scrape_company_page
    import clean_company_scrape

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')




def run_scraper():
    """
    Run the scraper to collect data from Funda.
    """
    logging.info("Starting the Funda scraper...")
    scrape_main_page.scrape_main()
    logging.info("Scraping main page completed.")
    scrape_company_page.scrape_company_information()
    logging.info("Scraping company page completed.")
    clean_company_scrape.clean_company_scrape()

    print("Scraping completed successfully!")

if __name__ == "__main__":
    run_scraper()
    print("All scraping tasks completed successfully!")
