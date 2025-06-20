# %%
from bs4 import BeautifulSoup
import re

def extract_homi_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.homi-makelaars.nl"

    for obj in soup.select("div.property-item"):
        try:
            # URL
            url_tag = obj.select_one("a[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Street + City
            address_tag = obj.select_one("h4.address")
            location_tag = obj.select_one("div.property-location")
            street = address_tag.get_text(strip=True) if address_tag else None
            city_text = location_tag.get_text(strip=True) if location_tag else None
            full_adres = f"{street} in {city_text}" if street and city_text else None

            # City (parsed from postal + city line)
            city = None
            if city_text:
                parts = city_text.split()
                city = parts[-1] if len(parts) > 1 else None

            # Price
            price = None
            price_tag = obj.select_one("div.cta-price-tag")
            if price_tag:
                price_match = re.search(r"€\s?([\d\.,]+)", price_tag.text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    price = float(price_str)

            # Area (Afmeting)
            area = None
            area_tag = obj.select_one("div.meta-data[title='Afmeting'], div.meta-data[data-original-title='Afmeting']")
            if area_tag:
                area_match = re.search(r"(\d+)", area_tag.text)
                area = int(area_match.group(1)) if area_match else None

            # Number of rooms (Kamer(s))
            num_rooms = None
            rooms_tag = obj.select_one("div.meta-data[title='Kamer(s)'], div.meta-data[data-original-title='Kamer(s)']")
            if rooms_tag:
                room_match = re.search(r"(\d+)", rooms_tag.text)
                num_rooms = int(room_match.group(1)) if room_match else None

            # Availability
            status_tag = obj.select_one("div.property-status")
            status_text = status_tag.text.strip().lower() if status_tag else ""
            available = "Beschikbaar"
            if "onder bod" in status_text:
                available = "Onder bod"
            elif "verkocht" in status_text:
                available = "Verkocht"

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
    url = 'https://www.homi-makelaars.nl/aanbod/'
    html = get_html(url)
    listings = extract_homi_data(html)
    for listing in listings:
        print(listing)