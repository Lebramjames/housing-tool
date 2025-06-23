# %%
from bs4 import BeautifulSoup
import re

def extract_roxxle_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.roxxle.nl"

    for obj in soup.select("a.property-horizontal"):
        try:
            # URL
            url = obj["href"]
            if not url.startswith("http"):
                url = base_url + url

            # Address
            address_tag = obj.select_one("div.address")
            city_price_tag = obj.select_one("p.town-price")
            address = address_tag.get_text(strip=True) if address_tag else None

            # City
            city_match = re.search(r"^(.*?)\s*∙", city_price_tag.text) if city_price_tag else None
            city = city_match.group(1).strip() if city_match else None

            # Full address
            full_adres = f"{address} in {city}" if address and city else None

            # Price
            price = None
            price_match = re.search(r"€\s?([\d\.,]+)", city_price_tag.text) if city_price_tag else None
            if price_match:
                price_str = price_match.group(1).replace(".", "").replace(",", ".")
                price = float(price_str)

            # Availability
            stickers = obj.select("div.stickers span.sticker")
            available = "Beschikbaar"
            for sticker in stickers:
                text = sticker.get_text(strip=True).lower()
                if "onder optie" in text:
                    available = "Onder optie"
                    break
                elif "verkocht" in text:
                    available = "Verkocht"
                    break

            # Area and number of rooms are not in provided HTML, default to None
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
    url = 'https://www.roxxle.nl/aanbod?makelaar=690'
    html = get_html(url)
    listings = extract_roxxle_data(html)
    for listing in listings:
        print(listing)
        