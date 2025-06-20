# %%
from bs4 import BeautifulSoup
import re

def extract_dehuizenbemiddelaar_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.dehuizenbemiddelaar.nl"

    for obj in soup.select("a.object"):
        try:
            # URL
            url = obj.get("href")
            if url and not url.startswith("http"):
                url = base_url + url

            # Address: street and city
            street_tag = obj.select_one("h2.object-address span:nth-of-type(1)")
            city_tag = obj.select_one("h2.object-address span:nth-of-type(2)")
            street = street_tag.get_text(strip=True) if street_tag else None
            city = city_tag.get_text(strip=True) if city_tag else None
            full_adres = f"{street} in {city}" if street and city else None

            # Price
            price = None
            price_tag = obj.select_one("span.object-price")
            if price_tag:
                price_text = price_tag.get_text(strip=True).replace("\u20ac", "€")
                match = re.search(r"€\s?([\d\.,]+)", price_text)
                if match:
                    price = float(match.group(1).replace(".", "").replace(",", "."))

            # Area (Wonen)
            area = None
            woon_match = re.search(r"Wonen:\s*([\d,\.]+)\s*m", obj.text)
            if woon_match:
                try:
                    area = float(woon_match.group(1).replace(",", "."))
                except ValueError:
                    area = None

            # Rooms
            num_rooms = None
            room_match = re.search(r"Kamers:\s*(\d+)", obj.text)
            if room_match:
                num_rooms = int(room_match.group(1))

            # Availability
            status_tag = obj.select_one("span.object-status")
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

    url = 'https://dehuizenbemiddelaar.nl/amsterdam/woningaanbod'
    html = get_html(url)
    listings = extract_dehuizenbemiddelaar_data(html)
    for listing in listings:
        print(listing)