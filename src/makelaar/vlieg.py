# %%
from bs4 import BeautifulSoup
import re

def extract_vlieg_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []

    for obj in soup.select("article.object"):
        try:
            # Street and city
            street_tag = obj.select_one("div.title h2")
            city_tag = obj.select_one("div.title h3")
            street = street_tag.text.strip() if street_tag else None
            city = city_tag.text.strip() if city_tag else None
            full_adres = f"{street} in {city}" if street and city else None

            # URL
            url_tag = obj.select_one("a.overlay[href]")
            url = url_tag["href"] if url_tag else None

            # Price
            price = None
            price_tag = obj.select_one("span.price")
            if price_tag:
                price_match = re.search(r"€\s?([\d\.,]+)", price_tag.text)
                if price_match:
                    price = float(price_match.group(1).replace(".", "").replace(",", "."))

            # Area and number of rooms not in this HTML, set as None
            area = None
            num_rooms = None

            # Availability: always marked "Nieuw" or fallback to "Beschikbaar"
            status_tag = obj.select_one("div.status")
            status_text = status_tag.get_text(strip=True).lower() if status_tag else ""
            if "verkocht" in status_text:
                available = "Verkocht"
            elif "onder bod" in status_text:
                available = "Onder bod"
            else:
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
    url ='https://www.vlieg.nl/woningen/#FckxDoAgEAXRu_yawsaGy5gNbBQVlsBGjYS7i1O-acgnkdYlS1UnnmFBsSoXTxEGh0jOJewVtiHSM_Y8_aEbyMXlDW7TobekkFZO6B8'
    html = get_html(url)
    listings = extract_vlieg_data(html)
    for listing in listings:
        print(listing)
        