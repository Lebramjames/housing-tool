# %%
from bs4 import BeautifulSoup
import re

def extract_ldmakelaars_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.ldmakelaars.nl"

    for obj in soup.select("article.objectcontainer"):
        try:
            # URL
            url_tag = obj.select_one("a.img-container[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Address components
            street_tag = obj.select_one("span.street")
            zip_tag = obj.select_one("span.zipcode")
            city_tag = obj.select_one("span.locality")
            street = street_tag.text.strip() if street_tag else ""
            zipcode = zip_tag.text.strip() if zip_tag else ""
            city = city_tag.text.strip() if city_tag else ""

            full_adres = f"{street} {zipcode} in {city}".strip() if street and city else None

            # Price
            price = None
            price_tag = obj.select_one("span.obj_price")
            if price_tag:
                price_text = price_tag.get_text(strip=True)
                price_match = re.search(r"€\s?([\d\.,]+)", price_text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area
            area = None
            area_tag = obj.select_one("span.object_label.object_sqfeet .number")
            if area_tag:
                area_match = re.search(r"(\d+)", area_tag.text)
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            room_tag = obj.select_one("span.object_label.object_rooms .number")
            if room_tag:
                room_match = re.search(r"(\d+)", room_tag.text)
                if room_match:
                    num_rooms = int(room_match.group(1))

            # Availability
            status_tag = obj.select_one("span.object_status")
            status_text = status_tag.text.strip().lower() if status_tag else ""
            available = "Beschikbaar"
            if "onder bod" in status_text:
                available = "Onder bod"
            elif "verkocht" in status_text:
                available = "Verkocht"
            elif "verhuurd" in status_text:
                available = "Verhuurd"

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
    url = 'https://www.ldmakelaars.nl/woningaanbod/'
    html = get_html(url)
    listings = extract_ldmakelaars_data(html)
    for listing in listings:
        print(listing)
        
    # where skipping is done 0, 12, 24, 36, etc.
    url_format ='https://www.ldmakelaars.nl/woningaanbod?skip=1{page}'