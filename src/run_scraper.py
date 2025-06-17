# %%
try:
    from src import scrape_main_page
    from src import scrape_company_page
    from src import clean_company_scrape
except ImportError:
    import scrape_main_page
    import scrape_company_page
    import clean_company_scrape





def run_scraper():
    """
    Run the scraper to collect data from Funda.
    """
    scrape_main_page.scrape_main()
    scrape_company_page.scrape_company_information()
    clean_company_scrape.clean_company_scrape()

    print("Scraping completed successfully!")

if __name__ == "__main__":
    run_scraper()
    print("All scraping tasks completed successfully!")
