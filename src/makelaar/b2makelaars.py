# %%
from bs4 import BeautifulSoup
import re

def extract_b2makelaars_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.b2makelaars.nl"

    for obj in soup.select("article.objectcontainer"):
        try:
            # Address components
            street_tag = obj.select_one("span.street")
            zipcode_tag = obj.select_one("span.zipcode")
            city_tag = obj.select_one("span.locality")
            full_adres = " ".join(filter(None, [
                street_tag.text.strip() if street_tag else None,
                zipcode_tag.text.strip() if zipcode_tag else None,
                city_tag.text.strip() if city_tag else None
            ]))

            # URL
            url_tag = obj.select_one("a[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # City
            city = city_tag.text.strip() if city_tag else None

            # Price
            price = None
            price_tag = obj.select_one("span.obj_price")
            if price_tag:
                price_match = re.search(r"€\s?([\d\.,]+)", price_tag.get_text())
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area
            area = None
            area_tag = obj.select_one("span.object_label.object_sqfeet span.number")
            if area_tag:
                area_match = re.search(r"(\d+)", area_tag.text.replace("\xa0", " "))
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            room_tag = obj.select_one("span.object_label.object_rooms span.number")
            if room_tag:
                room_match = re.search(r"\d+", room_tag.text)
                if room_match:
                    num_rooms = int(room_match.group(0))

            # Availability
            available = "Beschikbaar"
            status_text = obj.text.lower()
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
    url = 'https://www.b2makelaars.nl/woningaanbod/amsterdam?locationofinterest=Amsterdam&moveunavailablelistingstothebottom=true&orderby=10&orderdescending=true'
    html = get_html(url)
    listings = extract_b2makelaars_data(html)
    for listing in listings:
        print(listing)