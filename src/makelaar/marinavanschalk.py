# %%
from bs4 import BeautifulSoup
import re

def extract_marinavanschaik_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.marinavanschaik.nl"

    for obj in soup.select("div.prop"):
        try:
            # Address
            street_tag = obj.select_one("h3.street_value")
            city_tag = obj.select_one("h4")
            full_adres = f"{street_tag.text.strip()} in {city_tag.text.strip()}" if street_tag and city_tag else None

            # URL
            url_tag = obj.select_one("a[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # City
            city = city_tag.text.strip() if city_tag else None

            # Price
            price = None
            price_tag = obj.select_one("span.price_value")
            if price_tag:
                try:
                    price = float(price_tag.text.replace(".", "").replace(",", ".").strip())
                except ValueError:
                    pass

            # Area
            area_tag = obj.select_one("span.surface_area_value")
            area = int(area_tag.text.strip()) if area_tag and area_tag.text.strip().isdigit() else None

            # Number of rooms
            room_tag = obj.select_one("span.num_rooms")
            num_rooms = int(room_tag.text.strip()) if room_tag and room_tag.text.strip().isdigit() else None

            # Availability
            status_tag = obj.select_one("div.status")
            status_text = status_tag.text.strip().lower() if status_tag else ""
            available = "Beschikbaar"
            if "verkocht" in status_text:
                available = "Verkocht"
            elif "onder bod" in status_text:
                available = "Onder bod"

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
    url = 'https://www.marinavanschaik.nl/'
    html = get_html(url)
    listings = extract_marinavanschaik_data(html)
    for listing in listings:
        print(listing)