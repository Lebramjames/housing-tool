# %%
# TODO
from bs4 import BeautifulSoup
import re

def extract_alicebakker_data(html: str):
    return []

if __name__ == "__main__":
    from src.utils.get_url import get_html
    url ='https://www.alicebakker.nl/aanbod'
    html = get_html(url)
    listings = extract_alicebakker_data(html)
    for listing in listings:
        print(listing)
