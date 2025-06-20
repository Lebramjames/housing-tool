# %%
from bs4 import BeautifulSoup
import re

def extract_cocq_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.cocqmakelaars.amsterdam"

    for obj in soup.select("article.objectcontainer"):
        try:
            # URL
            url_tag = obj.select_one("a.img-container[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Street and city
            street_tag = obj.select_one("h3.obj_address span.street")
            city_tag = obj.select_one("h3.obj_address span.locality")
            street = street_tag.get_text(strip=True) if street_tag else None
            city = city_tag.get_text(strip=True) if city_tag else None
            full_adres = f"{street} in {city}" if street and city else None

            # Price
            price = None
            price_tag = obj.select_one("span.obj_price")
            if price_tag:
                price_text = price_tag.get_text()
                price_match = re.search(r"€\s?([\d\.,]+)", price_text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    price = float(price_str)

            # Area (woonoppervlakte)
            area = None
            area_tag = obj.select_one("span.object_label.object_sqfeet span.number")
            if area_tag:
                area_match = re.search(r"([\d,\.]+)", area_tag.text.replace(",", "."))
                if area_match:
                    try:
                        area = float(area_match.group(1))
                    except ValueError:
                        pass

            # Number of rooms
            num_rooms = None
            rooms_tag = obj.select_one("span.object_label.object_rooms span.number")
            if rooms_tag:
                try:
                    num_rooms = int(rooms_tag.text.strip())
                except ValueError:
                    pass

            # Availability (status)
            status = "Beschikbaar"
            status_tag = obj.select_one("span.object_status")
            if status_tag:
                status_text = status_tag.text.strip().lower()
                if "onder bod" in status_text:
                    status = "Onder bod"
                elif "verkocht" in status_text:
                    status = "Verkocht"

            listings.append({
                "full_adres": full_adres,
                "url": url,
                "city": city,
                "price": price,
                "area": area,
                "num_rooms": num_rooms,
                "available": status
            })
        except Exception:
            continue

    return listings

if __name__ == "__main__":
    from src.utils.get_url import get_html
    url = 'https://www.cocqmakelaars.amsterdam/woningaanbod'
    html = get_html(url)
    listings = extract_cocq_data(html)
    for listing in listings:
        print(listing)
    # url_format = 'https://www.cocqmakelaars.amsterdam/woningaanbod?skip=12
