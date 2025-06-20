# %%
from bs4 import BeautifulSoup
import re

def extract_maxdemakelaer_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.maxdemakelaer.com"

    for obj in soup.select("a.elementor-element[href]"):
        try:
            # URL
            url = obj["href"]
            if not url.startswith("http"):
                url = base_url + url

            # Address (h1 inside the card)
            address_tag = obj.select_one("h1.elementor-heading-title")
            full_adres = address_tag.get_text(strip=True) if address_tag else None

            # City (assume Amsterdam based on all provided listings)
            city = "Amsterdam"

            # Price
            price_tag = obj.select_one("h2.elementor-heading-title:contains('€')")
            price_text = price_tag.get_text() if price_tag else ""
            price_match = re.search(r"€\s?([\d\.,]+)", price_text)
            price = float(price_match.group(1).replace(".", "").replace(",", ".")) if price_match else None

            # Status
            status_tag = obj.select_one("h2.elementor-heading-title:not(:contains('€'))")
            status_text = status_tag.get_text(strip=True).lower() if status_tag else ""
            if "beschikbaar" in status_text:
                available = "Beschikbaar"
            elif "onder voorbehoud" in status_text:
                available = "Verkocht onder voorbehoud"
            elif "verkocht" in status_text:
                available = "Verkocht"
            else:
                available = None

            # Area and number of rooms not present in trimmed HTML – default to None
            area = None
            num_rooms = None

            listings.append({
                "full_adres": full_adres,
                "url": url,
                "city": city,
                "price": price,
                "area": area,
                "num_rooms": num_rooms,
                "available": available
            })
        except Exception:
            continue

    return listings

if __name__ == "__main__":
    from src.utils.get_url import get_html
    url = "https://www.maxdemakelaer.com/aanbod/"
    html = get_html(url)
    listings = extract_maxdemakelaer_data(html)
    for listing in listings:
        print(listing)
