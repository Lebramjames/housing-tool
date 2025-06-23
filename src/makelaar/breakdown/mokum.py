# %%
from bs4 import BeautifulSoup
import re

def extract_mokum_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://mokummakelaardij.com"

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
            price_tags = obj.select("div.object-price")
            for tag in price_tags:
                price_text = tag.get_text()
                price_match = re.search(r"€\s?([\d\.,]+)", price_text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                        break
                    except ValueError:
                        pass

            # Area
            area = None
            area_tag = obj.select_one("div.object-feature-woonoppervlakte")
            if area_tag:
                area_match = re.search(r"(\d+)\s*m", area_tag.get_text())
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            room_tag = obj.select_one("div.object-feature-aantalkamers")
            if room_tag:
                room_match = re.search(r"(\d+)\s+kamer", room_tag.get_text())
                if room_match:
                    num_rooms = int(room_match.group(1))

            # Availability
            status_classes = obj.get("class", [])
            available = "Beschikbaar"
            if any("verkocht" in cls for cls in status_classes):
                available = "Verkocht"
            elif any("onder-bod" in cls for cls in status_classes):
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
    url ='https://mokummakelaardij.com/aanbod/?_zoeken=amsterdam'
    html = get_html(url)
    listings = extract_mokum_data(html)
    for listing in listings:
        print(listing)

    url_format ='https://mokummakelaardij.com/aanbod/?_zoeken=amsterdam&_paged={page}'