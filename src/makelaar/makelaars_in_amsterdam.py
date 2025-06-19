import re
from bs4 import BeautifulSoup

def extract_makelaarsadam_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.makelaars-in-amsterdam.nl"

    for li in soup.select("li.metalist__item--forsale"):
        try:
            # Full address
            street = li.select_one("span.object__address-street")
            city = li.select_one("span.object__address-city")
            full_adres = f"{street.text.strip()} in {city.text.strip()}" if street and city else None

            # URL
            url_tag = li.select_one("a[href][title]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price_tag = li.select_one("p.metalist__price")
            price = int(re.sub(r"[^\d]", "", price_tag.text)) if price_tag else None

            # Area
            area_tag = li.select_one("span.object__woonoppervlakte")
            area = int(re.search(r"(\d+)", area_tag.text).group(1)) if area_tag else None

            # Rooms
            room_tag = li.select_one("span.object__aantalkamers")
            num_rooms = int(re.search(r"(\d+)", room_tag.text).group(1)) if room_tag else None

            listings.append({
                "full_adres": full_adres,
                "url": url,
                "city": city.text.strip() if city else None,
                "price": price,
                "area": area,
                "num_rooms": num_rooms,
                "available": "Beschikbaar"
            })
        except Exception:
            continue

    return listings