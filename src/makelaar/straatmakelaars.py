# %%
from bs4 import BeautifulSoup
import re

def extract_staatmakelaars_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.staatmakelaars.nl"

    for obj in soup.select("div.object"):
        try:
            # Address and City
            address_tag = obj.select_one("h2.obj_address") or obj.select_one("span.obj_address")
            full_adres = address_tag.get_text(strip=True) if address_tag else None

            city = None
            if full_adres:
                parts = full_adres.split(",")
                if len(parts) > 1:
                    city = parts[-1].strip().split()[-1]

            # URL
            url_tag = obj.select_one("a[href*='/woningaanbod/koop/']")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

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
            area_tag = obj.select_one("span.object_effective_area")
            if area_tag:
                area_match = re.search(r"(\d+)\s*m", area_tag.get_text())
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            room_tag = obj.select_one("span.object_bed_rooms")
            if room_tag:
                room_match = re.search(r"(\d+)", room_tag.get_text())
                if room_match:
                    num_rooms = int(room_match.group(1))

            # Availability
            available = "Beschikbaar"
            status_tag = obj.select_one("span.object_status")
            status_text = status_tag.get_text(strip=True).lower() if status_tag else ""
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
    url = "https://www.staatmakelaars.nl/woningaanbod/koop/amsterdam?locationofinterest=Amsterdam&moveunavailablelistingstothebottom=true&orderby=10"
    html = get_html(url)
    listings = extract_staatmakelaars_data(html)
    for listing in listings:
        print(listing)
        
# %%
