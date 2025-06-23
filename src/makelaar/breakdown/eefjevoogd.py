# %%
from bs4 import BeautifulSoup
import re

def extract_eefjevoogd_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.eefjevoogd.nl"

    for obj in soup.select("article.woning"):
        try:
            # Address and City
            street_tag = obj.select_one("header.item_header h3")
            city_tag = obj.select_one("header.item_header .postcode_plaats")
            full_adres = street_tag.text.strip() if street_tag else None
            city_text = city_tag.text.strip() if city_tag else None

            # URL
            url_tag = obj.select_one("a.item_link")
            url = url_tag["href"] if url_tag and url_tag.has_attr("href") else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price = None
            price_tag = obj.select_one("div.prijs_info div.prijs")
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
            area_tag = obj.select_one("div.meta_info div.oppervlakte")
            if area_tag:
                area_match = re.search(r"(\d+)\s*m", area_tag.text)
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            room_tag = obj.select_one("div.meta_info div.slaapkamers")
            if room_tag:
                room_match = re.search(r"(\d+)", room_tag.text)
                if room_match:
                    num_rooms = int(room_match.group(1))

            # Availability
            status_tag = obj.select_one("a.thumbnail span.label_new")
            status_text = status_tag.text.strip().lower() if status_tag else ""
            available = "Beschikbaar"
            if "onder bod" in status_text:
                available = "Onder bod"
            elif "verkocht" in status_text:
                available = "Verkocht"

            listings.append({
                "full_adres": full_adres,
                "url": url,
                "city": city_text,
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
    url = 'https://www.eefjevoogd.nl/nl/woningen/aanbod/?adress=amsterdam&koopprijs%5Bmin%5D=&koopprijs%5Bmax%5D=&woonoppervlakte=&slaapkamers=&objecttype=&orderby=publicatiedatum%3Adesc%2Cstatus%3Aasc'

    html = get_html(url)
    listings = extract_eefjevoogd_data(html)
    for listing in listings:
        print(listing)

    url_format = 'https://www.eefjevoogd.nl/nl/woningen/aanbod/page/{page}/?adress=amsterdam&koopprijs%5Bmin%5D&koopprijs%5Bmax%5D&woonoppervlakte&slaapkamers&objecttype&orderby=publicatiedatum%3Adesc%2Cstatus%3Aasc'