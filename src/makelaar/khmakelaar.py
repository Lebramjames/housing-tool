# %%
from bs4 import BeautifulSoup
import re

def extract_khmakelaardij_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.khmakelaardij.nl"

    for obj in soup.select("div.object"):
        try:
            # Address
            street = obj.select_one("span.object-street")
            number = obj.select_one("span.object-housenumber")
            addition = obj.select_one("span.object-housenumber-addition")
            city = obj.select_one("span.object-place")
            street_str = f"{street.text.strip()} {number.text.strip()}" if street and number else None
            if addition:
                street_str += f" {addition.text.strip()}"
            full_adres = f"{street_str} in {city.text.strip()}" if street_str and city else None

            # URL
            url_tag = obj.select_one("a[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price = None
            price_tag = obj.select_one("span.object-price-value")
            if price_tag:
                price_match = re.search(r"€\s?([\d\.,]+)", price_tag.text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        price = None

            # Area
            area = None
            area_tag = obj.select_one("div.object-feature-woonoppervlakte div.object-feature-info")
            if area_tag:
                area_match = re.search(r"(\d+)\s*m", area_tag.text)
                area = int(area_match.group(1)) if area_match else None

            # Number of rooms
            num_rooms = None
            room_tag = obj.select_one("div.object-feature-aantalkamers div.object-feature-info")
            if room_tag:
                room_match = re.search(r"(\d+)\s+kamer", room_tag.text.lower())
                num_rooms = int(room_match.group(1)) if room_match else None

            # Status
            status_tag = obj.select_one("div.object-status, div.object .object-status")
            status_text = status_tag.text.strip().lower() if status_tag else ""
            available = "Beschikbaar"
            if "verkocht" in status_text:
                available = "Verkocht"
            elif "onder bod" in status_text:
                available = "Onder bod"

            listings.append({
                "full_adres": full_adres,
                "url": url,
                "city": city.text.strip() if city else None,
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
    url ='https://www.khmakelaardij.nl/koopwoningen/?_prijs_tot=1-500000'
    html = get_html(url)
    listings = extract_khmakelaardij_data(html)
    for listing in listings:
        print(listing)
        