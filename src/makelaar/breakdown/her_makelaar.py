# %%
# TODO: PAGE without prices or area 
from bs4 import BeautifulSoup
import json
import html
import re

def extract_her_data(html_content: str):
    return None

if __name__ == "__main__":
    from src.utils.get_url import get_html
    url ='https://www.her-makelaardij.nl/aanbod'
    html = get_html(url)
    listings = extract_her_data(html)
    for listing in listings:
        print(listing)