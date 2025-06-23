# %%
from bs4 import BeautifulSoup
import re

def extract_bob_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.bob-makelaardij.nl"

    for obj in soup.select("article.objectcontainer"):
        try:
            # Address
            street_tag = obj.select_one("span.street")
            zip_tag = obj.select_one("span.zipcode")
            city_tag = obj.select_one("span.locality") or obj.select_one("span.location")

            street = street_tag.text.strip() if street_tag else ""
            zip_code = zip_tag.text.strip() if zip_tag else ""
            city = city_tag.text.strip() if city_tag else ""

            full_adres = f"{street} in {city} {zip_code}".strip() if street and city else None

            # URL
            url_tag = obj.select_one("a.img-container[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price_tag = obj.select_one("span.obj_price")
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
            room_tag = obj.select_one("span.object_rooms .number")
            room_text = room_tag.get_text(strip=True) if room_tag else ""
            room_match = re.search(r"(\d+)", room_text)
            num_rooms = int(room_match.group(1)) if room_match else None

            # Availability
            status_tag = obj.select_one("span.object_status")
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
    url ='https://www.bob-makelaardij.nl/woningaanbod/koop/amsterdam?locationofinterest=Amsterdam&pricerange.maxprice=500000'
    html = get_html(url)
    listings = extract_bob_data(html)
    for listing in listings:
        print(listing)
    # url_format = https://www.bob-makelaardij.nl/woningaanbod/koop/amsterdam?locationofinterest=Amsterdam&skip=1{page}