# %%
from bs4 import BeautifulSoup
import re

def extract_newcurb_data(html: str):
    return []

if __name__ == "__main__":
    from src.utils.get_url import get_html
    url = 'https://newcurbmakelaars.nl/woningaanbod/koop/amsterdam?availability=1&locationofinterest=Amsterdam&moveunavailablelistingstothebottom=true&orderby=10&orderdescending=true'
    html = get_html(url)
    listings = extract_newcurb_data(html)
    for listing in listings:
        print(listing)
