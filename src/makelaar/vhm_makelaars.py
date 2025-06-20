 #%%

from bs4 import BeautifulSoup
import re

def extract_vhm_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.vhmmakelaars.nl"

    for obj in soup.select("div.object"):
        try:
            # Address
            street = obj.select_one("span.object-street")
            number = obj.select_one("span.object-housenumber")
            city_tag = obj.select_one("span.object-place")
            street_str = f"{street.text.strip()} {number.text.strip()}" if street and number else None
            full_adres = f"{street_str} in {city_tag.text.strip()}" if street_str and city_tag else None

            # URL
            url_tag = obj.select_one("a[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price = None
            price_tag = obj.select_one("div.object-price-value")
            if price_tag:
                price_text = price_tag.get_text()
                price_match = re.search(r"€\s?([\d\.,]+)", price_text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area (woonoppervlakte)
            area = None
            area_tag = obj.select_one("div.object-feature-woonoppervlakte .object-feature-info")
            if area_tag:
                area_match = re.search(r"(\d+)\s*m", area_tag.get_text())
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            room_tag = obj.select_one("div.object-feature-aantalkamers .object-feature-info")
            if room_tag:
                room_match = re.search(r"(\d+)\s+kamer", room_tag.get_text())
                if room_match:
                    num_rooms = int(room_match.group(1))

            # Status
            status_text = obj.get("class", [])
            status_text = " ".join(status_text).lower()
            available = "Beschikbaar"
            if "onder-bod" in status_text:
                available = "Onder bod"
            elif "verkocht" in status_text:
                available = "Verkocht"

            listings.append({
                "full_adres": full_adres,
                "url": url,
                "city": city_tag.text.strip() if city_tag else None,
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
    url ='https://www.vhmmakelaars.nl/aanbod/?_zoeken=amsterdam'
    html = get_html(url)
    listings = extract_vhm_data(html)
    for listing in listings:
        print(listing)
    url_format ='https://www.vhmmakelaars.nl/aanbod/?_zoeken=amsterdam&_paged=2'