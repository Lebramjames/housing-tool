# %%
from bs4 import BeautifulSoup
import re

def extract_bnv_data(html: str):
    return []

if __name__ == "__main__":
    from src.utils.get_url import get_html
    url = 'https://www.bertvanvulpen.nl/woningaanbod/beschikbaar/koop/#JcrBCYAwDEDRVSRnJ-gGjpE2AaXWlCQKRdzdiLfP593Qd0Q3SIDNnJWwwQzm6Oc3M1tZt5oRNbYoseYR_wcJrcwTRbbluIQ1UfiAPjqHqiIdnhc'
    html = get_html(url)
    listings = extract_bnv_data(html)
    for listing in listings:
        print(listing)
