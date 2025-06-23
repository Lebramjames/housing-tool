# %%
from bs4 import BeautifulSoup
import re

def extract_ldb_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.ldbmakelaardij.nl"

    for obj in soup.select("article.objectcontainer"):
        try:
            # URL
            link_tag = obj.select_one("a.img-container")
            url = link_tag["href"] if link_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Address
            street_tag = obj.select_one("span.street")
            zipcode_tag = obj.select_one("span.zipcode")
            city_tag = obj.select_one("span.locality") or obj.select_one("span.location")
            street = street_tag.text.strip() if street_tag else ""
            zipcode = zipcode_tag.text.strip() if zipcode_tag else ""
            city = city_tag.text.strip() if city_tag else None
            full_adres = f"{street}, {zipcode} {city}".strip(", ")

            # Price
            price = None
            price_tag = obj.select_one("span.obj_price")
            if price_tag:
                price_match = re.search(r"€\s?([\d\.,]+)", price_tag.text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    price = float(price_str)

            # Area (woonoppervlakte)
            area = None
            area_tag = obj.select_one("span.object_label.object_sqfeet span.number")
            if area_tag:
                area_match = re.search(r"(\d+)", area_tag.text.replace("\xa0", " "))
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            room_tag = obj.select_one("span.object_label.object_rooms span.number")
            if room_tag and room_tag.text.isdigit():
                num_rooms = int(room_tag.text)

            # Availability (based on presence of status label text)
            status_tag = obj.select_one("span.object_status")
            status_text = status_tag.text.strip().lower() if status_tag else ""
            if "nieuw" in status_text or "beschikbaar" in status_text:
                available = "Beschikbaar"
            elif "verkocht onder voorbehoud" in status_text:
                available = "Verkocht onder voorbehoud"
            elif "verkocht" in status_text:
                available = "Verkocht"
            else:
                available = None

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
    url = 'https://www.ldbmakelaardij.nl/woningaanbod/koop/amsterdam?locationofinterest=Amsterdam&moveunavailablelistingstothebottom=true'
    html = get_html(url)
    listings = extract_ldb_data(html)
    for listing in listings:
        print(listing)

    # skip format: 0, 12, 24, ...
    url_format ='https://www.ldbmakelaardij.nl/woningaanbod/koop/amsterdam?locationofinterest=Amsterdam&moveunavailablelistingstothebottom=true&skip={page}'