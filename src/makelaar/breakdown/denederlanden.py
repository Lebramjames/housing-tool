# %%
from bs4 import BeautifulSoup
import re

def extract_denederlanden_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.denederlanden.eu"

    for card in soup.select("a.card-property"):
        try:
            # URL
            url = card.get("href")
            if url and not url.startswith("http"):
                url = base_url + url

            # Address and City
            address_tag = card.select_one("div.card-property__text span:first-of-type")
            address = address_tag.get_text(strip=True) if address_tag else None

            # Attempt to infer city from the URL (as it's embedded like /object/street-city/)
            city = None
            if url:
                match = re.search(r'/object/[\w-]+-([\w\-]+?)/', url)
                if match:
                    city = match.group(1).replace('-', ' ').title()

            full_adres = f"{address} in {city}" if address and city else None

            # Price
            price = None
            price_tag = card.select_one("div.card-property__text span:nth-of-type(2)")
            if price_tag:
                price_text = price_tag.get_text()
                price_match = re.search(r"€\s?([\d\.,]+)", price_text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area and number of rooms not found in this HTML → set as None
            area = None
            num_rooms = None

            # Availability – default "Beschikbaar"
            available = "Beschikbaar"

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
    url = "https://www.denederlanden.eu/wonen/zoeken/heel-nederland/0-500000/"
    html = get_html(url)
    listings = extract_denederlanden_data(html)
    for listing in listings:
        print(listing)
