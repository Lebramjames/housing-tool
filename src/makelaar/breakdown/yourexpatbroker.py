# %%
from bs4 import BeautifulSoup
import re

def extract_yourexpatbroker_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://yourexpatbroker.nl"

    for obj in soup.select("article.object"):
        try:
            # Address
            street_tag = obj.select_one("h3.object__address span.street")
            zip_tag = obj.select_one("h3.object__address span.zipcode")
            city_tag = obj.select_one("h3.object__address span.locality")
            street = street_tag.text.strip() if street_tag else ""
            zip_code = zip_tag.text.strip() if zip_tag else ""
            city = city_tag.text.strip() if city_tag else ""
            full_adres = f"{street} in {city} {zip_code}" if street and city else None

            # URL
            url_tag = obj.select_one("a.object__address-container")
            url = url_tag["href"] if url_tag and url_tag.has_attr("href") else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price_tag = obj.select_one("h3.object__address span.price")
            price_text = price_tag.get_text(strip=True) if price_tag else ""
            price_match = re.search(r"€\s?([\d\.,]+)", price_text)
            price = None
            if price_match:
                price_str = price_match.group(1).replace(".", "").replace(",", ".")
                try:
                    price = float(price_str)
                except ValueError:
                    pass

            # Area
            area_tag = obj.select_one("span.object_sqfeet .number")
            area_text = area_tag.get_text(strip=True) if area_tag else ""
            area_match = re.search(r"(\d+)", area_text)
            area = int(area_match.group(1)) if area_match else None

            # Number of rooms
            rooms_tag = obj.select_one("span.object_rooms .number")
            rooms_text = rooms_tag.get_text(strip=True) if rooms_tag else ""
            rooms_match = re.search(r"(\d+)", rooms_text)
            num_rooms = int(rooms_match.group(1)) if rooms_match else None

            # Status
            status_tag = obj.select_one("span.object__status")
            status_text = status_tag.get_text(strip=True).lower() if status_tag else ""
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
    url ='https://yourexpatbroker.nl/woningaanbod/koop'
    html = get_html(url)
    listings = extract_yourexpatbroker_data(html)
    for listing in listings:
        print(listing)
