# %%
# scr/funda/page_scraper.py
"""
This module contains functions to scrape HTML content from a given URL.

"""

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import logging

def _get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve page with status code: {response.status_code}")
        return None
    
def _get_html_without_cookie(url, service=None, options=None):
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    html = driver.page_source
    driver.quit()
    return html
def get_valid_html_versions(url, service=None, options=None):

    html_req = _get_html(url)
    if html_req and "<title>Je bent bijna op de pagina die je zoekt" not in html_req and "captcha" not in html_req.lower():
        return html_req
    try: 
        pre_cookie_html = _get_html_without_cookie(url, service=service, options=options)
        return pre_cookie_html
    except Exception as e:
        logging.error(f"❌ Selenium failed to fetch page {url}: {e}")


def unit_test_get_valid_html_versions():
    url = "https://www.funda.nl/koop/amsterdam/huis-42912323-van-der-heijdenstraat-1/"
    service = Service(executable_path="path/to/chromedriver")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode for testing
    html = get_valid_html_versions(url, service=service, options=options)
    assert html is not None, "HTML content should not be None"
    assert "<title>Je bent bijna op de pagina die je zoekt" not in html, "Page should not contain captcha message"

if __name__ == "__main__":
    # Run unit test
    unit_test_get_valid_html_versions()
    print("Unit test passed successfully.")