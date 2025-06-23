# %%
from bs4 import BeautifulSoup
import re

def extract_gewoonsimpel_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.gewoonsimpelmakelaars.nl"

    for obj in soup.select("article.objectcontainer"):
        try:
            # Address and city
            street_tag = obj.select_one("span.street")
            zip_tag = obj.select_one("span.zipcode")
            city_tag = obj.select_one("span.locality") or obj.select_one("span.location")
            street = street_tag.text.strip() if street_tag else None
            zipcode = zip_tag.text.strip() if zip_tag else ""
            city = city_tag.text.strip() if city_tag else None
            full_adres = f"{street}, {zipcode} in {city}" if street and city else None

            # URL
            url_tag = obj.select_one("a.img-container[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price = None
            price_tag = obj.select_one("span.obj_price")
            if price_tag:
                match = re.search(r"€\s?([\d\.,]+)", price_tag.text)
                if match:
                    price_str = match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area (woonoppervlakte)
            area = None
            area_tag = obj.select_one("span.object_sqfeet .number")
            if area_tag:
                match = re.search(r"(\d+)", area_tag.text)
                area = int(match.group(1)) if match else None

            # Number of rooms
            num_rooms = None
            rooms_tag = obj.select_one("span.object_rooms .number")
            if rooms_tag:
                match = re.search(r"(\d+)", rooms_tag.text)
                num_rooms = int(match.group(1)) if match else None

            # Status
            status_tag = obj.select_one("span.object_status")
            status_text = status_tag.text.strip().lower() if status_tag else ""
            available = "Beschikbaar"
            if "onder bod" in status_text:
                available = "Onder bod"
            elif "verkocht" in status_text:
                available = "Verkocht"

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
    url ='https://www.gewoonsimpelmakelaars.nl/woningaanbod/amsterdam?locationofinterest=Amsterdam&moveunavailablelistingstothebottom=true&orderby=10&orderdescending=true'
    html = get_html(url)
    listings = extract_gewoonsimpel_data(html)
    for listing in listings:
        print(listing)
        