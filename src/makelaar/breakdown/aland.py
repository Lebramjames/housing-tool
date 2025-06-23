# %%
from bs4 import BeautifulSoup
import re

def extract_aland_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://aland.nl"

    for obj in soup.select("div.listing-item"):
        try:
            # Address and city
            address = obj.get("data-title") or obj.get("data-address") or ""
            full_adres = address.strip() if address else None

            # Extract city from address (last word if it ends with a city name)
            city = None
            if full_adres:
                city_parts = full_adres.split()
                city = city_parts[-1] if len(city_parts) > 0 else None

            # URL
            url_tag = obj.select_one("a[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price = None
            price_raw = obj.get("data-price", "")
            price_match = re.search(r"€\s?([\d\.,]+)", price_raw)
            if price_match:
                price_str = price_match.group(1).replace(".", "").replace(",", ".")
                price = float(price_str)

            # Area
            area = None
            area_tag = obj.select_one("li.main-detail-_area span")
            if area_tag:
                area_match = re.search(r"(\d+)", area_tag.text.replace(".", ""))
                area = int(area_match.group(1)) if area_match else None

            # Number of rooms
            num_rooms = None
            rooms_tag = obj.select_one("li.main-detail-_kamers span")
            if rooms_tag:
                num_rooms = int(rooms_tag.text.strip())

            # Availability
            available = "Beschikbaar"
            badge_tag = obj.select_one("div.listing-badges span")
            if badge_tag:
                status = badge_tag.text.strip().lower()
                if "verkocht" in status:
                    available = "Verkocht"
                elif "aangekocht" in status:
                    available = "Aangekocht"
                elif "onder bod" in status:
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
    url = "https://aland.nl/aanbod/?realteo_order=date-desc&_property_type=woonhuis&_offer_type=&tax-region=amsterdam&_kamers=&_bedrooms=&_area_min=44&_area_max=212" 
    html = get_html(url)
    listings = extract_aland_data(html)
    for listing in listings:
        print(listing)
    